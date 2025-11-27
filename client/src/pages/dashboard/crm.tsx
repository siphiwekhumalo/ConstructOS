import { DashboardLayout } from "@/components/dashboard-layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Search, Phone, Mail, MoreVertical, Plus, Users, Building, TrendingUp, UserPlus } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getClients } from "@/lib/api";
import { useState } from "react";

export default function DashboardCRM() {
  const queryClient = useQueryClient();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [newClient, setNewClient] = useState({
    name: "",
    company: "",
    role: "",
    email: "",
    phone: "",
    status: "Lead",
  });

  const { data: clients, isLoading } = useQuery({
    queryKey: ["clients"],
    queryFn: getClients,
  });

  const createClient = useMutation({
    mutationFn: async (data: typeof newClient) => {
      const response = await fetch("/api/v1/clients", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...data,
          avatar: data.name.split(" ").map(n => n[0]).join("").toUpperCase().slice(0, 2),
        }),
      });
      if (!response.ok) throw new Error("Failed to create client");
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      setIsDialogOpen(false);
      setNewClient({ name: "", company: "", role: "", email: "", phone: "", status: "Lead" });
    },
  });

  const filteredClients = clients?.filter(client =>
    client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    client.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
    client.email.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const leadClients = filteredClients.filter(c => c.status === "Lead" || c.status === "Proposal Sent");
  const activeClients = filteredClients.filter(c => c.status === "Active Negotiation");
  const closedClients = filteredClients.filter(c => c.status === "Contract Signed");

  const stats = [
    { label: "Total Contacts", value: clients?.length || 0, icon: Users, color: "text-primary" },
    { label: "Active Leads", value: leadClients.length, icon: UserPlus, color: "text-blue-500" },
    { label: "In Negotiation", value: activeClients.length, icon: TrendingUp, color: "text-orange-500" },
    { label: "Closed Deals", value: closedClients.length, icon: Building, color: "text-green-500" },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground" data-testid="text-page-title">
              Customer Relationship Management
            </h1>
            <p className="text-muted-foreground mt-1">Manage client relationships, leads, and sales pipeline.</p>
          </div>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button className="gap-2" data-testid="button-add-contact">
                <Plus className="h-4 w-4" /> Add Contact
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-card border-white/10 max-w-md">
              <DialogHeader>
                <DialogTitle>Add New Contact</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Full Name</Label>
                    <Input
                      placeholder="John Smith"
                      value={newClient.name}
                      onChange={(e) => setNewClient({ ...newClient, name: e.target.value })}
                      className="bg-background border-white/10"
                      data-testid="input-name"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Company</Label>
                    <Input
                      placeholder="Acme Corp"
                      value={newClient.company}
                      onChange={(e) => setNewClient({ ...newClient, company: e.target.value })}
                      className="bg-background border-white/10"
                      data-testid="input-company"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Role / Title</Label>
                  <Input
                    placeholder="Project Manager"
                    value={newClient.role}
                    onChange={(e) => setNewClient({ ...newClient, role: e.target.value })}
                    className="bg-background border-white/10"
                    data-testid="input-role"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Email</Label>
                    <Input
                      type="email"
                      placeholder="john@acme.com"
                      value={newClient.email}
                      onChange={(e) => setNewClient({ ...newClient, email: e.target.value })}
                      className="bg-background border-white/10"
                      data-testid="input-email"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Phone</Label>
                    <Input
                      placeholder="+1 (555) 000-0000"
                      value={newClient.phone}
                      onChange={(e) => setNewClient({ ...newClient, phone: e.target.value })}
                      className="bg-background border-white/10"
                      data-testid="input-phone"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Pipeline Stage</Label>
                  <Select value={newClient.status} onValueChange={(v) => setNewClient({ ...newClient, status: v })}>
                    <SelectTrigger className="bg-background border-white/10" data-testid="select-status">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Lead">Lead</SelectItem>
                      <SelectItem value="Proposal Sent">Proposal Sent</SelectItem>
                      <SelectItem value="Active Negotiation">Active Negotiation</SelectItem>
                      <SelectItem value="Contract Signed">Contract Signed</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button 
                  className="w-full" 
                  onClick={() => createClient.mutate(newClient)}
                  disabled={!newClient.name || !newClient.email}
                  data-testid="button-submit-contact"
                >
                  Add Contact
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          {stats.map((stat, i) => (
            <Card key={i} className="bg-card border-white/5">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{stat.label}</p>
                    <p className="text-2xl font-bold font-display mt-1" data-testid={`text-stat-${i}`}>
                      {stat.value}
                    </p>
                  </div>
                  <stat.icon className={`h-8 w-8 ${stat.color} opacity-80`} />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="flex items-center gap-4 bg-card p-4 rounded-sm border border-white/5">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input 
              placeholder="Search contacts by name, company, or email..." 
              className="pl-9 bg-background border-white/10 focus-visible:ring-primary"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              data-testid="input-search"
            />
          </div>
        </div>

        <Tabs defaultValue="all" className="w-full">
          <TabsList className="bg-secondary/50 border border-white/5">
            <TabsTrigger value="all" data-testid="tab-all">All Contacts ({filteredClients.length})</TabsTrigger>
            <TabsTrigger value="leads" data-testid="tab-leads">Leads ({leadClients.length})</TabsTrigger>
            <TabsTrigger value="negotiation" data-testid="tab-negotiation">Negotiation ({activeClients.length})</TabsTrigger>
            <TabsTrigger value="closed" data-testid="tab-closed">Closed ({closedClients.length})</TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="mt-6">
            <ClientList clients={filteredClients} isLoading={isLoading} />
          </TabsContent>
          <TabsContent value="leads" className="mt-6">
            <ClientList clients={leadClients} isLoading={isLoading} />
          </TabsContent>
          <TabsContent value="negotiation" className="mt-6">
            <ClientList clients={activeClients} isLoading={isLoading} />
          </TabsContent>
          <TabsContent value="closed" className="mt-6">
            <ClientList clients={closedClients} isLoading={isLoading} />
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}

function ClientList({ clients, isLoading }: { clients: any[]; isLoading: boolean }) {
  if (isLoading) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        Loading contacts...
      </div>
    );
  }

  if (clients.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        No contacts found. Add your first contact to get started.
      </div>
    );
  }

  return (
    <div className="grid gap-4">
      {clients.map((client) => (
        <Card 
          key={client.id} 
          className="bg-card border-white/5 hover:border-primary/30 transition-colors"
          data-testid={`card-client-${client.id}`}
        >
          <CardContent className="flex items-center justify-between p-6">
            <div className="flex items-center gap-4">
              <Avatar className="h-12 w-12 border border-white/10">
                <AvatarFallback className="bg-secondary text-primary font-bold">
                  {client.avatar || client.name.split(" ").map((n: string) => n[0]).join("").toUpperCase().slice(0, 2)}
                </AvatarFallback>
              </Avatar>
              <div>
                <h3 className="font-bold text-lg text-foreground" data-testid={`text-name-${client.id}`}>
                  {client.name}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {client.role} at {client.company}
                </p>
              </div>
            </div>

            <div className="hidden md:flex items-center gap-8">
              <a 
                href={`mailto:${client.email}`} 
                className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground cursor-pointer transition-colors"
              >
                <Mail className="h-4 w-4" /> {client.email}
              </a>
              <a 
                href={`tel:${client.phone}`}
                className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground cursor-pointer transition-colors"
              >
                <Phone className="h-4 w-4" /> {client.phone}
              </a>
            </div>

            <div className="flex items-center gap-4">
              <span className={`px-3 py-1 rounded-full text-xs font-medium border ${
                client.status === 'Active Negotiation' ? 'bg-blue-500/10 text-blue-500 border-blue-500/20' :
                client.status === 'Contract Signed' ? 'bg-green-500/10 text-green-500 border-green-500/20' :
                client.status === 'Proposal Sent' ? 'bg-purple-500/10 text-purple-500 border-purple-500/20' :
                'bg-orange-500/10 text-orange-500 border-orange-500/20'
              }`} data-testid={`status-${client.id}`}>
                {client.status}
              </span>
              <Button variant="ghost" size="icon" data-testid={`button-more-${client.id}`}>
                <MoreVertical className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
