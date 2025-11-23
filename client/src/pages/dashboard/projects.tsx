import { DashboardLayout } from "@/components/dashboard-layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { Plus, Search, Filter, MoreHorizontal, Calendar } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { getProjects } from "@/lib/api";

export default function DashboardProjects() {
  const { data: projects, isLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: getProjects,
  });

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground">Projects</h1>
            <p className="text-muted-foreground mt-1">Manage and track construction projects.</p>
          </div>
          <Button className="gap-2" data-testid="button-new-project">
            <Plus className="h-4 w-4" /> New Project
          </Button>
        </div>

        <div className="flex items-center gap-4 bg-card p-4 rounded-sm border border-white/5">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input 
              placeholder="Search projects..." 
              className="pl-9 bg-background border-white/10 focus-visible:ring-primary"
              data-testid="input-search-projects"
            />
          </div>
          <Button variant="outline" size="icon" className="border-white/10" data-testid="button-filter">
            <Filter className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="icon" className="border-white/10" data-testid="button-calendar">
            <Calendar className="h-4 w-4" />
          </Button>
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
                  <TableHead className="font-mono text-xs uppercase tracking-wider text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {projects && projects.length > 0 ? (
                  projects.map((project) => (
                    <TableRow 
                      key={project.id} 
                      className="border-white/5 hover:bg-white/5 group"
                      data-testid={`row-project-${project.id}`}
                    >
                      <TableCell className="font-mono text-xs text-muted-foreground" data-testid={`text-id-${project.id}`}>
                        {project.id}
                      </TableCell>
                      <TableCell className="font-medium" data-testid={`text-name-${project.id}`}>
                        {project.name}
                      </TableCell>
                      <TableCell className="text-muted-foreground" data-testid={`text-location-${project.id}`}>
                        {project.location}
                      </TableCell>
                      <TableCell>
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${
                          project.status === 'In Progress' ? 'bg-blue-500/10 text-blue-500 border-blue-500/20' :
                          project.status === 'Completed' ? 'bg-green-500/10 text-green-500 border-green-500/20' :
                          project.status === 'Delayed' ? 'bg-red-500/10 text-red-500 border-red-500/20' :
                          'bg-gray-500/10 text-gray-400 border-gray-500/20'
                        }`} data-testid={`status-${project.id}`}>
                          {project.status}
                        </span>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="h-1.5 w-24 bg-secondary rounded-full overflow-hidden">
                            <div 
                              className={`h-full rounded-full ${
                                project.status === 'Delayed' ? 'bg-red-500' : 
                                project.status === 'Completed' ? 'bg-green-500' : 'bg-primary'
                              }`} 
                              style={{ width: `${project.progress}%` }} 
                            />
                          </div>
                          <span className="text-xs font-mono" data-testid={`progress-${project.id}`}>
                            {project.progress}%
                          </span>
                        </div>
                      </TableCell>
                      <TableCell className="font-mono" data-testid={`budget-${project.id}`}>
                        ${parseFloat(project.budget).toLocaleString()}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button 
                          variant="ghost" 
                          size="icon" 
                          className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                          data-testid={`button-actions-${project.id}`}
                        >
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center text-muted-foreground py-12">
                      No projects found. Create your first project to get started.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
