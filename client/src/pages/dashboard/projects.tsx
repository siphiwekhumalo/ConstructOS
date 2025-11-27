import { DashboardLayout } from "@/components/dashboard-layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Calendar as CalendarComponent } from "@/components/ui/calendar";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Plus, Search, Filter, MoreHorizontal, Calendar, X, MapPin, Users, 
  Phone, Mail, Building, Clock, Banknote, Eye, Edit, Trash2, CheckCircle,
  AlertCircle, User, FileText, Briefcase
} from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getProjects, createProject, updateProject, deleteProject, getAccounts, getEmployees } from "@/lib/api";
import { useState, useMemo } from "react";
import { format, isWithinInterval, parseISO, startOfDay, endOfDay } from "date-fns";
import { formatCurrency } from "@/lib/currency";
import type { Project, Account, Employee } from "@shared/schema";
import { DateRange } from "react-day-picker";

interface ProjectTeamMember {
  id: string;
  name: string;
  role: string;
  phone?: string;
  email?: string;
}

const MOCK_TEAM_MEMBERS: Record<string, ProjectTeamMember[]> = {};

function seededRandom(seed: string): () => number {
  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    hash = ((hash << 5) - hash) + seed.charCodeAt(i);
    hash = hash & hash;
  }
  return () => {
    hash = (hash * 1103515245 + 12345) & 0x7fffffff;
    return hash / 0x7fffffff;
  };
}

function generateTeamForProject(projectId: string): ProjectTeamMember[] {
  if (MOCK_TEAM_MEMBERS[projectId]) return MOCK_TEAM_MEMBERS[projectId];
  
  const random = seededRandom(projectId);
  const roles = ["Site Manager", "Project Engineer", "Safety Officer", "Foreman", "Quantity Surveyor"];
  const firstNames = ["Thabo", "Sipho", "Nomvula", "Lerato", "Andile", "Zanele", "Kagiso", "Thandiwe"];
  const lastNames = ["Molefe", "Dlamini", "Nkosi", "Zulu", "Mthembu", "Khumalo", "Ndlovu", "Shabalala"];
  
  const numMembers = 3 + Math.floor(random() * 3);
  const team: ProjectTeamMember[] = [];
  
  for (let i = 0; i < numMembers; i++) {
    const firstName = firstNames[Math.floor(random() * firstNames.length)];
    const lastName = lastNames[Math.floor(random() * lastNames.length)];
    team.push({
      id: `${projectId}-${i}`,
      name: `${firstName} ${lastName}`,
      role: roles[i % roles.length],
      phone: `+27 ${Math.floor(60 + random() * 20)} ${Math.floor(100 + random() * 900)} ${Math.floor(1000 + random() * 9000)}`,
      email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}@construct.co.za`,
    });
  }
  
  MOCK_TEAM_MEMBERS[projectId] = team;
  return team;
}

export default function DashboardProjects() {
  const queryClient = useQueryClient();
  
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [dateRange, setDateRange] = useState<DateRange | undefined>(undefined);
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  
  const [isNewProjectOpen, setIsNewProjectOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDeleteConfirmOpen, setIsDeleteConfirmOpen] = useState(false);
  
  const [newProject, setNewProject] = useState({
    name: "",
    location: "",
    status: "Planning",
    progress: 0,
    budget: "",
    dueDate: "",
    description: "",
  });
  
  const [editProject, setEditProject] = useState({
    name: "",
    location: "",
    status: "",
    progress: 0,
    budget: "",
    dueDate: "",
    description: "",
  });

  const { data: projects, isLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: getProjects,
  });

  const { data: accounts } = useQuery({
    queryKey: ["accounts"],
    queryFn: getAccounts,
  });

  const { data: employees } = useQuery({
    queryKey: ["employees"],
    queryFn: getEmployees,
  });

  const createProjectMutation = useMutation({
    mutationFn: createProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      setIsNewProjectOpen(false);
      setNewProject({
        name: "",
        location: "",
        status: "Planning",
        progress: 0,
        budget: "",
        dueDate: "",
        description: "",
      });
    },
  });

  const updateProjectMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => updateProject(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      setIsEditOpen(false);
      setSelectedProject(null);
    },
  });

  const deleteProjectMutation = useMutation({
    mutationFn: deleteProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      setIsDeleteConfirmOpen(false);
      setSelectedProject(null);
      setIsDetailOpen(false);
    },
  });

  const filteredProjects = useMemo(() => {
    if (!projects) return [];
    
    return projects.filter((project) => {
      const matchesSearch = 
        project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project.location.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesStatus = 
        statusFilter === "all" || project.status === statusFilter;
      
      let matchesDate = true;
      if (dateRange?.from && project.dueDate) {
        const projectDate = parseISO(project.dueDate);
        if (dateRange.to) {
          matchesDate = isWithinInterval(projectDate, {
            start: startOfDay(dateRange.from),
            end: endOfDay(dateRange.to),
          });
        } else {
          matchesDate = projectDate >= startOfDay(dateRange.from);
        }
      }
      
      return matchesSearch && matchesStatus && matchesDate;
    });
  }, [projects, searchTerm, statusFilter, dateRange]);

  const handleProjectClick = (project: Project) => {
    setSelectedProject(project);
    setIsDetailOpen(true);
  };

  const handleEditClick = (project: Project) => {
    setSelectedProject(project);
    setEditProject({
      name: project.name,
      location: project.location,
      status: project.status,
      progress: project.progress,
      budget: project.budget?.toString() || "",
      dueDate: project.dueDate || "",
      description: (project as any).description || "",
    });
    setIsEditOpen(true);
  };

  const handleDeleteClick = (project: Project) => {
    setSelectedProject(project);
    setIsDeleteConfirmOpen(true);
  };

  const handleSaveEdit = () => {
    if (!selectedProject) return;
    updateProjectMutation.mutate({
      id: selectedProject.id,
      data: {
        name: editProject.name,
        location: editProject.location,
        status: editProject.status,
        progress: editProject.progress,
        budget: editProject.budget,
        due_date: editProject.dueDate,
      },
    });
  };

  const handleCreateProject = () => {
    createProjectMutation.mutate({
      name: newProject.name,
      location: newProject.location,
      status: newProject.status,
      progress: newProject.progress,
      budget: newProject.budget,
      due_date: newProject.dueDate,
    } as any);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "In Progress":
        return "bg-blue-500/10 text-blue-500 border-blue-500/20";
      case "Completed":
        return "bg-green-500/10 text-green-500 border-green-500/20";
      case "Delayed":
        return "bg-red-500/10 text-red-500 border-red-500/20";
      case "Planning":
        return "bg-purple-500/10 text-purple-400 border-purple-500/20";
      case "On Hold":
        return "bg-yellow-500/10 text-yellow-400 border-yellow-500/20";
      default:
        return "bg-gray-500/10 text-gray-400 border-gray-500/20";
    }
  };

  const getProgressColor = (status: string) => {
    switch (status) {
      case "Delayed":
        return "bg-red-500";
      case "Completed":
        return "bg-green-500";
      default:
        return "bg-primary";
    }
  };

  const clearFilters = () => {
    setSearchTerm("");
    setStatusFilter("all");
    setDateRange(undefined);
  };

  const hasActiveFilters = searchTerm || statusFilter !== "all" || dateRange;

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground">Projects</h1>
            <p className="text-muted-foreground mt-1">Manage and track construction projects.</p>
          </div>
          <Dialog open={isNewProjectOpen} onOpenChange={setIsNewProjectOpen}>
            <DialogTrigger asChild>
              <Button className="gap-2" data-testid="button-new-project">
                <Plus className="h-4 w-4" /> New Project
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-card border-white/10 max-w-lg">
              <DialogHeader>
                <DialogTitle>Create New Project</DialogTitle>
                <DialogDescription>
                  Add a new construction project to your portfolio.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div className="space-y-2">
                  <Label>Project Name</Label>
                  <Input
                    placeholder="e.g., Sandton City Tower Development"
                    value={newProject.name}
                    onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                    className="bg-background border-white/10"
                    data-testid="input-project-name"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Location</Label>
                  <Input
                    placeholder="e.g., Sandton, Johannesburg"
                    value={newProject.location}
                    onChange={(e) => setNewProject({ ...newProject, location: e.target.value })}
                    className="bg-background border-white/10"
                    data-testid="input-project-location"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Status</Label>
                    <Select 
                      value={newProject.status} 
                      onValueChange={(v) => setNewProject({ ...newProject, status: v })}
                    >
                      <SelectTrigger className="bg-background border-white/10" data-testid="select-status">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Planning">Planning</SelectItem>
                        <SelectItem value="In Progress">In Progress</SelectItem>
                        <SelectItem value="On Hold">On Hold</SelectItem>
                        <SelectItem value="Delayed">Delayed</SelectItem>
                        <SelectItem value="Completed">Completed</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Budget (R)</Label>
                    <Input
                      placeholder="5000000"
                      value={newProject.budget}
                      onChange={(e) => setNewProject({ ...newProject, budget: e.target.value })}
                      className="bg-background border-white/10"
                      data-testid="input-project-budget"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Due Date</Label>
                    <Input
                      type="date"
                      value={newProject.dueDate}
                      onChange={(e) => setNewProject({ ...newProject, dueDate: e.target.value })}
                      className="bg-background border-white/10"
                      data-testid="input-project-due-date"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Progress (%)</Label>
                    <Input
                      type="number"
                      min="0"
                      max="100"
                      placeholder="0"
                      value={newProject.progress}
                      onChange={(e) => setNewProject({ ...newProject, progress: parseInt(e.target.value) || 0 })}
                      className="bg-background border-white/10"
                      data-testid="input-project-progress"
                    />
                  </div>
                </div>
                <Button
                  className="w-full"
                  onClick={handleCreateProject}
                  disabled={!newProject.name || !newProject.location || createProjectMutation.isPending}
                  data-testid="button-save-project"
                >
                  {createProjectMutation.isPending ? "Creating..." : "Create Project"}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        <div className="flex flex-wrap items-center gap-4 bg-card p-4 rounded-sm border border-white/5">
          <div className="relative flex-1 min-w-[200px] max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input 
              placeholder="Search projects..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 bg-background border-white/10 focus-visible:ring-primary"
              data-testid="input-search-projects"
            />
          </div>
          
          <Popover open={isFilterOpen} onOpenChange={setIsFilterOpen}>
            <PopoverTrigger asChild>
              <Button 
                variant="outline" 
                className={`gap-2 border-white/10 ${statusFilter !== "all" ? "bg-primary/10 border-primary/30" : ""}`}
                data-testid="button-filter"
              >
                <Filter className="h-4 w-4" />
                {statusFilter !== "all" ? statusFilter : "Filter"}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-56 bg-card border-white/10 p-2">
              <div className="space-y-1">
                <Button
                  variant={statusFilter === "all" ? "secondary" : "ghost"}
                  className="w-full justify-start"
                  onClick={() => { setStatusFilter("all"); setIsFilterOpen(false); }}
                >
                  All Status
                </Button>
                {["Planning", "In Progress", "On Hold", "Delayed", "Completed"].map((status) => (
                  <Button
                    key={status}
                    variant={statusFilter === status ? "secondary" : "ghost"}
                    className="w-full justify-start"
                    onClick={() => { setStatusFilter(status); setIsFilterOpen(false); }}
                  >
                    <span className={`mr-2 h-2 w-2 rounded-full ${
                      status === "In Progress" ? "bg-blue-500" :
                      status === "Completed" ? "bg-green-500" :
                      status === "Delayed" ? "bg-red-500" :
                      status === "Planning" ? "bg-purple-500" :
                      "bg-yellow-500"
                    }`} />
                    {status}
                  </Button>
                ))}
              </div>
            </PopoverContent>
          </Popover>

          <Popover open={isCalendarOpen} onOpenChange={setIsCalendarOpen}>
            <PopoverTrigger asChild>
              <Button 
                variant="outline" 
                className={`gap-2 border-white/10 ${dateRange?.from ? "bg-primary/10 border-primary/30" : ""}`}
                data-testid="button-calendar"
              >
                <Calendar className="h-4 w-4" />
                {dateRange?.from ? (
                  dateRange.to ? (
                    `${format(dateRange.from, "MMM d")} - ${format(dateRange.to, "MMM d")}`
                  ) : (
                    format(dateRange.from, "MMM d, yyyy")
                  )
                ) : (
                  "Due Date"
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0 bg-card border-white/10" align="start">
              <CalendarComponent
                mode="range"
                selected={dateRange}
                onSelect={setDateRange}
                numberOfMonths={2}
                className="rounded-md"
              />
              <div className="flex items-center justify-end gap-2 p-3 border-t border-white/10">
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => { setDateRange(undefined); setIsCalendarOpen(false); }}
                >
                  Clear
                </Button>
                <Button 
                  size="sm"
                  onClick={() => setIsCalendarOpen(false)}
                >
                  Apply
                </Button>
              </div>
            </PopoverContent>
          </Popover>

          {hasActiveFilters && (
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={clearFilters}
              className="gap-1 text-muted-foreground hover:text-foreground"
            >
              <X className="h-3 w-3" /> Clear filters
            </Button>
          )}
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-muted-foreground">Loading projects...</div>
          </div>
        ) : (
          <div className="bg-card border border-white/5 rounded-sm overflow-hidden">
            <Table>
              <TableHeader className="bg-secondary/50">
                <TableRow className="hover:bg-transparent border-white/5">
                  <TableHead className="font-mono text-xs uppercase tracking-wider">ID</TableHead>
                  <TableHead className="font-mono text-xs uppercase tracking-wider">Project Name</TableHead>
                  <TableHead className="font-mono text-xs uppercase tracking-wider">Location</TableHead>
                  <TableHead className="font-mono text-xs uppercase tracking-wider">Status</TableHead>
                  <TableHead className="font-mono text-xs uppercase tracking-wider">Progress</TableHead>
                  <TableHead className="font-mono text-xs uppercase tracking-wider">Budget</TableHead>
                  <TableHead className="font-mono text-xs uppercase tracking-wider">Due Date</TableHead>
                  <TableHead className="font-mono text-xs uppercase tracking-wider text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredProjects.length > 0 ? (
                  filteredProjects.map((project) => (
                    <TableRow 
                      key={project.id} 
                      className="border-white/5 hover:bg-white/5 group cursor-pointer"
                      onClick={() => handleProjectClick(project)}
                      data-testid={`row-project-${project.id}`}
                    >
                      <TableCell className="font-mono text-xs text-muted-foreground" data-testid={`text-id-${project.id}`}>
                        {project.id.slice(0, 8)}...
                      </TableCell>
                      <TableCell className="font-medium" data-testid={`text-name-${project.id}`}>
                        {project.name}
                      </TableCell>
                      <TableCell className="text-muted-foreground" data-testid={`text-location-${project.id}`}>
                        <div className="flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          {project.location}
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(project.status)}`} data-testid={`status-${project.id}`}>
                          {project.status}
                        </span>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="h-1.5 w-24 bg-secondary rounded-full overflow-hidden">
                            <div 
                              className={`h-full rounded-full ${getProgressColor(project.status)}`} 
                              style={{ width: `${project.progress}%` }} 
                            />
                          </div>
                          <span className="text-xs font-mono" data-testid={`progress-${project.id}`}>
                            {project.progress}%
                          </span>
                        </div>
                      </TableCell>
                      <TableCell className="font-mono" data-testid={`budget-${project.id}`}>
                        {formatCurrency(project.budget)}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {project.dueDate ? format(parseISO(project.dueDate), "MMM d, yyyy") : "-"}
                      </TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                            <Button 
                              variant="ghost" 
                              size="icon" 
                              className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                              data-testid={`button-actions-${project.id}`}
                            >
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end" className="bg-card border-white/10">
                            <DropdownMenuItem onClick={(e) => { e.stopPropagation(); handleProjectClick(project); }}>
                              <Eye className="h-4 w-4 mr-2" /> View Details
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={(e) => { e.stopPropagation(); handleEditClick(project); }}>
                              <Edit className="h-4 w-4 mr-2" /> Edit
                            </DropdownMenuItem>
                            <DropdownMenuSeparator className="bg-white/10" />
                            <DropdownMenuItem 
                              onClick={(e) => { e.stopPropagation(); handleDeleteClick(project); }}
                              className="text-red-500 focus:text-red-500"
                            >
                              <Trash2 className="h-4 w-4 mr-2" /> Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center text-muted-foreground py-12">
                      {hasActiveFilters 
                        ? "No projects match your filters. Try adjusting your search criteria."
                        : "No projects found. Create your first project to get started."}
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        )}

        <Dialog open={isDetailOpen} onOpenChange={setIsDetailOpen}>
          <DialogContent className="bg-card border-white/10 max-w-2xl max-h-[85vh]">
            {selectedProject && (
              <>
                <DialogHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <DialogTitle className="text-xl">{selectedProject.name}</DialogTitle>
                      <DialogDescription className="flex items-center gap-2 mt-1">
                        <MapPin className="h-4 w-4" />
                        {selectedProject.location}
                      </DialogDescription>
                    </div>
                    <Badge className={`${getStatusColor(selectedProject.status)} text-sm`}>
                      {selectedProject.status}
                    </Badge>
                  </div>
                </DialogHeader>
                
                <ScrollArea className="max-h-[60vh] pr-4">
                  <div className="space-y-6 mt-4">
                    <div className="grid grid-cols-2 gap-4">
                      <Card className="bg-secondary/20 border-white/5">
                        <CardContent className="pt-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-xs text-muted-foreground uppercase tracking-wider">Budget</p>
                              <p className="text-xl font-bold mt-1">{formatCurrency(selectedProject.budget)}</p>
                            </div>
                            <Banknote className="h-8 w-8 text-primary opacity-60" />
                          </div>
                        </CardContent>
                      </Card>
                      <Card className="bg-secondary/20 border-white/5">
                        <CardContent className="pt-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-xs text-muted-foreground uppercase tracking-wider">Progress</p>
                              <p className="text-xl font-bold mt-1">{selectedProject.progress}%</p>
                            </div>
                            <CheckCircle className="h-8 w-8 text-green-500 opacity-60" />
                          </div>
                          <Progress value={selectedProject.progress} className="mt-2 h-2" />
                        </CardContent>
                      </Card>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div className="flex items-center gap-3 p-3 rounded-lg bg-secondary/20">
                        <Calendar className="h-5 w-5 text-muted-foreground" />
                        <div>
                          <p className="text-xs text-muted-foreground">Due Date</p>
                          <p className="font-medium">
                            {selectedProject.dueDate 
                              ? format(parseISO(selectedProject.dueDate), "MMMM d, yyyy") 
                              : "Not set"}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-3 rounded-lg bg-secondary/20">
                        <Building className="h-5 w-5 text-muted-foreground" />
                        <div>
                          <p className="text-xs text-muted-foreground">Project ID</p>
                          <p className="font-mono text-xs">{selectedProject.id}</p>
                        </div>
                      </div>
                    </div>

                    <Separator className="bg-white/10" />

                    <div>
                      <h3 className="text-sm font-semibold flex items-center gap-2 mb-4">
                        <Users className="h-4 w-4" /> Team on Site
                      </h3>
                      <div className="space-y-3">
                        {generateTeamForProject(selectedProject.id).map((member) => (
                          <div 
                            key={member.id} 
                            className="flex items-center gap-3 p-3 rounded-lg bg-secondary/20 hover:bg-secondary/30 transition-colors"
                          >
                            <Avatar className="h-10 w-10">
                              <AvatarFallback className="bg-primary/20 text-primary">
                                {member.name.split(" ").map(n => n[0]).join("")}
                              </AvatarFallback>
                            </Avatar>
                            <div className="flex-1 min-w-0">
                              <p className="font-medium">{member.name}</p>
                              <p className="text-xs text-muted-foreground">{member.role}</p>
                            </div>
                            <div className="flex items-center gap-2">
                              <Button 
                                variant="ghost" 
                                size="icon" 
                                className="h-8 w-8"
                                onClick={() => window.location.href = `tel:${member.phone}`}
                              >
                                <Phone className="h-4 w-4" />
                              </Button>
                              <Button 
                                variant="ghost" 
                                size="icon" 
                                className="h-8 w-8"
                                onClick={() => window.location.href = `mailto:${member.email}`}
                              >
                                <Mail className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <Separator className="bg-white/10" />

                    <div>
                      <h3 className="text-sm font-semibold flex items-center gap-2 mb-4">
                        <Briefcase className="h-4 w-4" /> Client Information
                      </h3>
                      <div className="p-4 rounded-lg bg-secondary/20">
                        <div className="flex items-start gap-4">
                          <Avatar className="h-12 w-12">
                            <AvatarFallback className="bg-blue-500/20 text-blue-400">
                              <Building className="h-6 w-6" />
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1">
                            <p className="font-medium">
                              {accounts && accounts.length > 0 
                                ? accounts[Math.floor(Math.random() * accounts.length)].name 
                                : "Client Name Pending"}
                            </p>
                            <p className="text-sm text-muted-foreground mt-1">
                              {selectedProject.location}
                            </p>
                            <div className="flex items-center gap-4 mt-3 text-sm text-muted-foreground">
                              <span className="flex items-center gap-1">
                                <Phone className="h-3 w-3" /> +27 11 123 4567
                              </span>
                              <span className="flex items-center gap-1">
                                <Mail className="h-3 w-3" /> client@company.co.za
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </ScrollArea>

                <DialogFooter className="mt-4">
                  <Button 
                    variant="outline" 
                    onClick={() => handleEditClick(selectedProject)}
                    className="gap-2"
                  >
                    <Edit className="h-4 w-4" /> Edit Project
                  </Button>
                  <Button onClick={() => setIsDetailOpen(false)}>Close</Button>
                </DialogFooter>
              </>
            )}
          </DialogContent>
        </Dialog>

        <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
          <DialogContent className="bg-card border-white/10 max-w-lg">
            <DialogHeader>
              <DialogTitle>Edit Project</DialogTitle>
              <DialogDescription>
                Update project details.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <div className="space-y-2">
                <Label>Project Name</Label>
                <Input
                  value={editProject.name}
                  onChange={(e) => setEditProject({ ...editProject, name: e.target.value })}
                  className="bg-background border-white/10"
                />
              </div>
              <div className="space-y-2">
                <Label>Location</Label>
                <Input
                  value={editProject.location}
                  onChange={(e) => setEditProject({ ...editProject, location: e.target.value })}
                  className="bg-background border-white/10"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Status</Label>
                  <Select 
                    value={editProject.status} 
                    onValueChange={(v) => setEditProject({ ...editProject, status: v })}
                  >
                    <SelectTrigger className="bg-background border-white/10">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Planning">Planning</SelectItem>
                      <SelectItem value="In Progress">In Progress</SelectItem>
                      <SelectItem value="On Hold">On Hold</SelectItem>
                      <SelectItem value="Delayed">Delayed</SelectItem>
                      <SelectItem value="Completed">Completed</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Budget (R)</Label>
                  <Input
                    value={editProject.budget}
                    onChange={(e) => setEditProject({ ...editProject, budget: e.target.value })}
                    className="bg-background border-white/10"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Due Date</Label>
                  <Input
                    type="date"
                    value={editProject.dueDate}
                    onChange={(e) => setEditProject({ ...editProject, dueDate: e.target.value })}
                    className="bg-background border-white/10"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Progress (%)</Label>
                  <Input
                    type="number"
                    min="0"
                    max="100"
                    value={editProject.progress}
                    onChange={(e) => setEditProject({ ...editProject, progress: parseInt(e.target.value) || 0 })}
                    className="bg-background border-white/10"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setIsEditOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  className="flex-1"
                  onClick={handleSaveEdit}
                  disabled={updateProjectMutation.isPending}
                >
                  {updateProjectMutation.isPending ? "Saving..." : "Save Changes"}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>

        <Dialog open={isDeleteConfirmOpen} onOpenChange={setIsDeleteConfirmOpen}>
          <DialogContent className="bg-card border-white/10 max-w-md">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2 text-red-500">
                <AlertCircle className="h-5 w-5" /> Delete Project
              </DialogTitle>
              <DialogDescription>
                Are you sure you want to delete "{selectedProject?.name}"? This action cannot be undone.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter className="mt-4">
              <Button variant="outline" onClick={() => setIsDeleteConfirmOpen(false)}>
                Cancel
              </Button>
              <Button 
                variant="destructive" 
                onClick={() => selectedProject && deleteProjectMutation.mutate(selectedProject.id)}
                disabled={deleteProjectMutation.isPending}
              >
                {deleteProjectMutation.isPending ? "Deleting..." : "Delete Project"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  );
}
