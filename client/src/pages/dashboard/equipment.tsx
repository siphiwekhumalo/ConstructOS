import { DashboardLayout } from "@/components/dashboard-layout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Truck, Wrench, CalendarClock, Plus, AlertTriangle, CheckCircle, Settings } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getEquipment } from "@/lib/api";
import { useState } from "react";

export default function DashboardEquipment() {
  const queryClient = useQueryClient();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [newEquipment, setNewEquipment] = useState({
    name: "",
    status: "Active",
    location: "",
    nextService: "30 Days",
  });

  const { data: equipment, isLoading } = useQuery({
    queryKey: ["equipment"],
    queryFn: getEquipment,
  });

  const createEquipment = useMutation({
    mutationFn: async (data: typeof newEquipment) => {
      const response = await fetch("/api/v1/equipment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error("Failed to create equipment");
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["equipment"] });
      setIsDialogOpen(false);
      setNewEquipment({ name: "", status: "Active", location: "", nextService: "30 Days" });
    },
  });

  const activeEquipment = equipment?.filter(e => e.status === "Active") || [];
  const maintenanceEquipment = equipment?.filter(e => e.status === "Maintenance") || [];
  const overdueService = equipment?.filter(e => e.nextService === "Overdue") || [];

  const stats = [
    { label: "Total Assets", value: equipment?.length || 0, icon: Truck, color: "text-primary" },
    { label: "Active", value: activeEquipment.length, icon: CheckCircle, color: "text-green-500" },
    { label: "In Maintenance", value: maintenanceEquipment.length, icon: Settings, color: "text-orange-500" },
    { label: "Service Overdue", value: overdueService.length, icon: AlertTriangle, color: "text-red-500" },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground" data-testid="text-page-title">
              Equipment Inventory
            </h1>
            <p className="text-muted-foreground mt-1">ERP Asset Management - Track fleet status, location, and maintenance schedules.</p>
          </div>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button className="gap-2" data-testid="button-add-equipment">
                <Plus className="h-4 w-4" /> Add Equipment
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-card border-white/10">
              <DialogHeader>
                <DialogTitle>Add Equipment</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div className="space-y-2">
                  <Label>Equipment Name</Label>
                  <Input
                    placeholder="e.g., Excavator CAT 320"
                    value={newEquipment.name}
                    onChange={(e) => setNewEquipment({ ...newEquipment, name: e.target.value })}
                    className="bg-background border-white/10"
                    data-testid="input-name"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Location</Label>
                    <Input
                      placeholder="Site A"
                      value={newEquipment.location}
                      onChange={(e) => setNewEquipment({ ...newEquipment, location: e.target.value })}
                      className="bg-background border-white/10"
                      data-testid="input-location"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Status</Label>
                    <Select value={newEquipment.status} onValueChange={(v) => setNewEquipment({ ...newEquipment, status: v })}>
                      <SelectTrigger className="bg-background border-white/10" data-testid="select-status">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Active">Active</SelectItem>
                        <SelectItem value="Maintenance">Maintenance</SelectItem>
                        <SelectItem value="Inactive">Inactive</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Next Service</Label>
                  <Select value={newEquipment.nextService} onValueChange={(v) => setNewEquipment({ ...newEquipment, nextService: v })}>
                    <SelectTrigger className="bg-background border-white/10" data-testid="select-service">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="7 Days">7 Days</SelectItem>
                      <SelectItem value="15 Days">15 Days</SelectItem>
                      <SelectItem value="30 Days">30 Days</SelectItem>
                      <SelectItem value="45 Days">45 Days</SelectItem>
                      <SelectItem value="60 Days">60 Days</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button 
                  className="w-full" 
                  onClick={() => createEquipment.mutate(newEquipment)}
                  disabled={!newEquipment.name || !newEquipment.location}
                  data-testid="button-submit-equipment"
                >
                  Add Equipment
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

        {isLoading ? (
          <div className="text-center py-12 text-muted-foreground">Loading equipment...</div>
        ) : equipment && equipment.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {equipment.map((item) => (
              <Card 
                key={item.id} 
                className="bg-card border-white/5 overflow-hidden group hover:border-primary/30 transition-colors"
                data-testid={`card-equipment-${item.id}`}
              >
                <div className="h-48 overflow-hidden relative bg-gradient-to-br from-secondary to-background">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Truck className="h-24 w-24 text-primary/20" />
                  </div>
                  {item.imageUrl && (
                    <>
                      <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent z-10" />
                      <img 
                        src={item.imageUrl} 
                        alt={item.name} 
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                    </>
                  )}
                  <div className="absolute bottom-4 left-4 z-20">
                    <Badge 
                      variant={item.status === 'Active' ? 'default' : 'destructive'} 
                      className="mb-2"
                      data-testid={`status-${item.id}`}
                    >
                      {item.status}
                    </Badge>
                    <h3 className="font-bold text-white text-lg" data-testid={`text-name-${item.id}`}>
                      {item.name}
                    </h3>
                  </div>
                  <div className="absolute top-4 right-4 z-20 font-mono text-xs text-white/60">
                    {item.id}
                  </div>
                </div>
                <CardContent className="pt-6 space-y-4">
                  <div className="flex justify-between items-center text-sm border-b border-white/5 pb-3">
                    <span className="text-muted-foreground">Location</span>
                    <span className="font-medium" data-testid={`text-location-${item.id}`}>
                      {item.location}
                    </span>
                  </div>
                  <div className="flex justify-between items-center text-sm border-b border-white/5 pb-3">
                    <span className="text-muted-foreground">Next Service</span>
                    <div className={`flex items-center gap-2 font-medium ${
                      item.nextService === 'Overdue' ? 'text-red-500' : 'text-foreground'
                    }`} data-testid={`text-service-${item.id}`}>
                      <CalendarClock className="h-4 w-4" />
                      {item.nextService}
                    </div>
                  </div>
                  <div className="flex gap-2 pt-2">
                    <Button 
                      variant="outline" 
                      className="w-full border-white/10 hover:bg-white/5"
                      data-testid={`button-service-${item.id}`}
                    >
                      <Wrench className="h-4 w-4 mr-2" /> Log Service
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-muted-foreground border border-dashed border-white/10 rounded-sm">
            No equipment registered. Add your first equipment to start tracking assets.
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
