import { DashboardLayout } from "@/components/dashboard-layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { 
  Ticket, Plus, Search, Clock, CheckCircle, AlertCircle, 
  MessageSquare, User, Calendar, Filter
} from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getTickets, createTicket, updateTicket, getAccounts } from "@/lib/api";
import { useState } from "react";

export default function DashboardSupport() {
  const queryClient = useQueryClient();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [newTicket, setNewTicket] = useState({
    subject: "",
    description: "",
    priority: "medium",
    category: "general",
    accountId: "",
  });

  const { data: tickets, isLoading } = useQuery({
    queryKey: ["tickets"],
    queryFn: getTickets,
  });

  const { data: accounts } = useQuery({
    queryKey: ["accounts"],
    queryFn: getAccounts,
  });

  const createTicketMutation = useMutation({
    mutationFn: createTicket,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tickets"] });
      setIsDialogOpen(false);
      setNewTicket({ subject: "", description: "", priority: "medium", category: "general", accountId: "" });
    },
  });

  const updateTicketMutation = useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: any }) => updateTicket(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tickets"] });
    },
  });

  const openTickets = tickets?.filter(t => t.status === "open").length || 0;
  const inProgressTickets = tickets?.filter(t => t.status === "in_progress").length || 0;
  const resolvedTickets = tickets?.filter(t => t.status === "resolved" || t.status === "closed").length || 0;

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      open: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
      in_progress: "bg-blue-500/20 text-blue-400 border-blue-500/30",
      waiting_on_customer: "bg-purple-500/20 text-purple-400 border-purple-500/30",
      resolved: "bg-green-500/20 text-green-400 border-green-500/30",
      closed: "bg-gray-500/20 text-gray-400 border-gray-500/30",
    };
    return styles[status] || styles.open;
  };

  const getPriorityBadge = (priority: string) => {
    const styles: Record<string, string> = {
      low: "bg-gray-500/20 text-gray-400 border-gray-500/30",
      medium: "bg-blue-500/20 text-blue-400 border-blue-500/30",
      high: "bg-orange-500/20 text-orange-400 border-orange-500/30",
      urgent: "bg-red-500/20 text-red-400 border-red-500/30",
    };
    return styles[priority] || styles.medium;
  };

  const filteredTickets = tickets?.filter(ticket => {
    const matchesSearch = ticket.subject?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ticket.ticketNumber?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === "all" || ticket.status === statusFilter;
    return matchesSearch && matchesStatus;
  }) || [];

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground" data-testid="text-page-title">
              Support Center
            </h1>
            <p className="text-muted-foreground mt-1">Manage customer tickets and support requests.</p>
          </div>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button className="gap-2" data-testid="button-add-ticket">
                <Plus className="h-4 w-4" /> New Ticket
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-card border-white/10 max-w-lg">
              <DialogHeader>
                <DialogTitle>Create Support Ticket</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div className="space-y-2">
                  <Label>Subject</Label>
                  <Input
                    placeholder="Brief description of the issue"
                    value={newTicket.subject}
                    onChange={(e) => setNewTicket({ ...newTicket, subject: e.target.value })}
                    className="bg-background border-white/10"
                    data-testid="input-subject"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Description</Label>
                  <Textarea
                    placeholder="Detailed description of the issue..."
                    value={newTicket.description}
                    onChange={(e) => setNewTicket({ ...newTicket, description: e.target.value })}
                    className="bg-background border-white/10 min-h-[100px]"
                    data-testid="input-description"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Priority</Label>
                    <Select value={newTicket.priority} onValueChange={(v) => setNewTicket({ ...newTicket, priority: v })}>
                      <SelectTrigger className="bg-background border-white/10" data-testid="select-priority">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                        <SelectItem value="urgent">Urgent</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Category</Label>
                    <Select value={newTicket.category} onValueChange={(v) => setNewTicket({ ...newTicket, category: v })}>
                      <SelectTrigger className="bg-background border-white/10" data-testid="select-category">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="general">General</SelectItem>
                        <SelectItem value="technical">Technical</SelectItem>
                        <SelectItem value="billing">Billing</SelectItem>
                        <SelectItem value="feature_request">Feature Request</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Related Account (Optional)</Label>
                  <Select value={newTicket.accountId} onValueChange={(v) => setNewTicket({ ...newTicket, accountId: v })}>
                    <SelectTrigger className="bg-background border-white/10" data-testid="select-account">
                      <SelectValue placeholder="Select account" />
                    </SelectTrigger>
                    <SelectContent>
                      {accounts?.map(account => (
                        <SelectItem key={account.id} value={account.id}>{account.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <Button
                  className="w-full"
                  onClick={() => createTicketMutation.mutate(newTicket as any)}
                  disabled={!newTicket.subject}
                  data-testid="button-save-ticket"
                >
                  Create Ticket
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <Card className="bg-card border-white/5">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Tickets</p>
                  <p className="text-2xl font-bold font-display" data-testid="stat-total">{tickets?.length || 0}</p>
                </div>
                <Ticket className="h-8 w-8 text-primary opacity-80" />
              </div>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Open</p>
                  <p className="text-2xl font-bold font-display text-yellow-500" data-testid="stat-open">{openTickets}</p>
                </div>
                <AlertCircle className="h-8 w-8 text-yellow-500 opacity-80" />
              </div>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">In Progress</p>
                  <p className="text-2xl font-bold font-display text-blue-500" data-testid="stat-in-progress">{inProgressTickets}</p>
                </div>
                <Clock className="h-8 w-8 text-blue-500 opacity-80" />
              </div>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Resolved</p>
                  <p className="text-2xl font-bold font-display text-green-500" data-testid="stat-resolved">{resolvedTickets}</p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-500 opacity-80" />
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="bg-card border-white/5">
          <CardHeader className="border-b border-white/5">
            <div className="flex flex-col md:flex-row md:items-center gap-4">
              <div className="relative flex-1 max-w-sm">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search tickets..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-background border-white/10"
                  data-testid="input-search"
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[180px] bg-background border-white/10" data-testid="select-filter">
                  <Filter className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="open">Open</SelectItem>
                  <SelectItem value="in_progress">In Progress</SelectItem>
                  <SelectItem value="waiting_on_customer">Waiting on Customer</SelectItem>
                  <SelectItem value="resolved">Resolved</SelectItem>
                  <SelectItem value="closed">Closed</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-white/5">
              {isLoading ? (
                <div className="p-8 text-center text-muted-foreground">Loading tickets...</div>
              ) : filteredTickets.length === 0 ? (
                <div className="p-8 text-center text-muted-foreground">No tickets found</div>
              ) : (
                filteredTickets.map((ticket) => (
                  <div key={ticket.id} className="flex items-start gap-4 p-4 hover:bg-white/5" data-testid={`ticket-row-${ticket.id}`}>
                    <div className="flex-shrink-0 pt-1">
                      <Ticket className="h-5 w-5 text-muted-foreground" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs text-muted-foreground font-mono">{ticket.ticketNumber}</span>
                        <Badge className={getPriorityBadge(ticket.priority || "medium")}>
                          {ticket.priority || "medium"}
                        </Badge>
                      </div>
                      <p className="font-medium truncate">{ticket.subject}</p>
                      <p className="text-sm text-muted-foreground line-clamp-1">{ticket.description}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {new Date(ticket.createdAt).toLocaleDateString()}
                        </span>
                        {ticket.type && (
                          <span className="capitalize">{ticket.type.replace("_", " ")}</span>
                        )}
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <Badge className={getStatusBadge(ticket.status || "open")}>
                        {ticket.status?.replace("_", " ") || "open"}
                      </Badge>
                      {ticket.status === "open" && (
                        <Button 
                          size="sm" 
                          variant="outline" 
                          className="text-xs border-white/10"
                          onClick={() => updateTicketMutation.mutate({ id: ticket.id, updates: { status: "in_progress" } })}
                          data-testid={`button-start-${ticket.id}`}
                        >
                          Start Working
                        </Button>
                      )}
                      {ticket.status === "in_progress" && (
                        <Button 
                          size="sm" 
                          variant="outline" 
                          className="text-xs border-white/10 text-green-500 hover:text-green-400"
                          onClick={() => updateTicketMutation.mutate({ id: ticket.id, updates: { status: "resolved" } })}
                          data-testid={`button-resolve-${ticket.id}`}
                        >
                          Resolve
                        </Button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
