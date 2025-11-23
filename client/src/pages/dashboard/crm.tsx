import { DashboardLayout } from "@/components/dashboard-layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Search, Phone, Mail, MoreVertical } from "lucide-react";

const clients = [
  {
    id: 1,
    name: "Alice Freeman",
    company: "Skyline Developers",
    role: "Project Owner",
    email: "alice@skylinedev.com",
    phone: "+1 (555) 123-4567",
    status: "Active Negotiation",
    avatar: "AF"
  },
  {
    id: 2,
    name: "Robert Chen",
    company: "City Planning Dept",
    role: "Civil Engineer",
    email: "r.chen@cityplanning.gov",
    phone: "+1 (555) 987-6543",
    status: "Contract Signed",
    avatar: "RC"
  },
  {
    id: 3,
    name: "Sarah Miller",
    company: "Miller Investments",
    role: "Lead Investor",
    email: "sarah@millerinv.com",
    phone: "+1 (555) 456-7890",
    status: "Proposal Sent",
    avatar: "SM"
  },
];

export default function DashboardCRM() {
  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground">CRM</h1>
            <p className="text-muted-foreground mt-1">Manage client relationships and proposals.</p>
          </div>
          <Button className="gap-2">
            Add Contact
          </Button>
        </div>

        <div className="flex items-center gap-4 bg-card p-4 rounded-sm border border-white/5">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input 
              placeholder="Search contacts..." 
              className="pl-9 bg-background border-white/10 focus-visible:ring-primary"
            />
          </div>
        </div>

        <div className="grid gap-4">
          {clients.map((client) => (
            <Card key={client.id} className="bg-card border-white/5 hover:border-primary/30 transition-colors">
              <CardContent className="flex items-center justify-between p-6">
                <div className="flex items-center gap-4">
                   <Avatar className="h-12 w-12 border border-white/10">
                     <AvatarFallback className="bg-secondary text-primary font-bold">{client.avatar}</AvatarFallback>
                   </Avatar>
                   <div>
                     <h3 className="font-bold text-lg text-foreground">{client.name}</h3>
                     <p className="text-sm text-muted-foreground">{client.role} at {client.company}</p>
                   </div>
                </div>

                <div className="hidden md:flex items-center gap-8">
                   <div className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground cursor-pointer">
                     <Mail className="h-4 w-4" /> {client.email}
                   </div>
                   <div className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground cursor-pointer">
                     <Phone className="h-4 w-4" /> {client.phone}
                   </div>
                </div>

                <div className="flex items-center gap-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium border ${
                    client.status === 'Active Negotiation' ? 'bg-blue-500/10 text-blue-500 border-blue-500/20' :
                    client.status === 'Contract Signed' ? 'bg-green-500/10 text-green-500 border-green-500/20' :
                    'bg-orange-500/10 text-orange-500 border-orange-500/20'
                  }`}>
                    {client.status}
                  </span>
                  <Button variant="ghost" size="icon">
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}
