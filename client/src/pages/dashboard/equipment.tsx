import { DashboardLayout } from "@/components/dashboard-layout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Truck, Wrench, AlertCircle, CalendarClock } from "lucide-react";

const equipment = [
  {
    id: "EQ-001",
    name: "Excavator CAT 320",
    status: "Active",
    location: "Site A",
    nextService: "15 Days",
    image: "https://images.unsplash.com/photo-1586118293331-92a37b211093?q=80&w=300&auto=format&fit=crop"
  },
  {
    id: "EQ-002",
    name: "Tower Crane TC-50",
    status: "Maintenance",
    location: "Site B",
    nextService: "Overdue",
    image: "https://images.unsplash.com/photo-1541625602330-2277a4c46182?q=80&w=300&auto=format&fit=crop"
  },
  {
    id: "EQ-003",
    name: "Bulldozer D6T",
    status: "Active",
    location: "Site A",
    nextService: "45 Days",
    image: "https://images.unsplash.com/photo-1527199768775-bdabf8b3b158?q=80&w=300&auto=format&fit=crop"
  },
];

export default function DashboardEquipment() {
  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground">Equipment Inventory</h1>
            <p className="text-muted-foreground mt-1">Track fleet status, location, and maintenance schedules.</p>
          </div>
          <Button className="gap-2">
            <Truck className="h-4 w-4" /> Add Equipment
          </Button>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {equipment.map((item) => (
            <Card key={item.id} className="bg-card border-white/5 overflow-hidden group">
              <div className="h-48 overflow-hidden relative">
                 <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent z-10" />
                 <img 
                   src={item.image} 
                   alt={item.name} 
                   className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                 />
                 <div className="absolute bottom-4 left-4 z-20">
                   <Badge variant={item.status === 'Active' ? 'default' : 'destructive'} className="mb-2">
                     {item.status}
                   </Badge>
                   <h3 className="font-bold text-white text-lg">{item.name}</h3>
                 </div>
              </div>
              <CardContent className="pt-6 space-y-4">
                <div className="flex justify-between items-center text-sm border-b border-white/5 pb-3">
                  <span className="text-muted-foreground">Location</span>
                  <span className="font-medium">{item.location}</span>
                </div>
                <div className="flex justify-between items-center text-sm border-b border-white/5 pb-3">
                  <span className="text-muted-foreground">Next Service</span>
                  <div className={`flex items-center gap-2 font-medium ${item.nextService === 'Overdue' ? 'text-red-500' : 'text-foreground'}`}>
                    <CalendarClock className="h-4 w-4" />
                    {item.nextService}
                  </div>
                </div>
                <div className="flex gap-2 pt-2">
                  <Button variant="outline" className="w-full border-white/10 hover:bg-white/5">
                    <Wrench className="h-4 w-4 mr-2" /> Log Service
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
