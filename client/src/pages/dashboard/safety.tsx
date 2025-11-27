import { DashboardLayout } from "@/components/dashboard-layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { ShieldCheck, AlertTriangle, FileCheck, HardHat, Plus, Calendar, User, CheckCircle2 } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getSafetyInspections } from "@/lib/api";
import { useState } from "react";
import { format } from "date-fns";

export default function DashboardSafety() {
  const queryClient = useQueryClient();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [newInspection, setNewInspection] = useState({
    site: "",
    type: "Foundation",
    status: "Passed",
    inspector: "",
    notes: "",
  });

  const { data: inspections, isLoading } = useQuery({
    queryKey: ["safetyInspections"],
    queryFn: getSafetyInspections,
  });

  const createInspection = useMutation({
    mutationFn: async (data: typeof newInspection) => {
      const response = await fetch("/api/v1/safety/inspections", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...data,
          date: new Date(),
        }),
      });
      if (!response.ok) throw new Error("Failed to create inspection");
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["safetyInspections"] });
      setIsDialogOpen(false);
      setNewInspection({ site: "", type: "Foundation", status: "Passed", inspector: "", notes: "" });
    },
  });

  const passedInspections = inspections?.filter(i => i.status === "Passed") || [];
  const warningInspections = inspections?.filter(i => i.status === "Warning") || [];
  const failedInspections = inspections?.filter(i => i.status === "Failed") || [];

  const incidentFreeDays = 142;
  const complianceScore = inspections && inspections.length > 0
    ? Math.round((passedInspections.length / inspections.length) * 100)
    : 100;

  const stats = [
    { 
      value: `${incidentFreeDays} Days`, 
      label: "Incident Free Streak", 
      color: "border-l-green-500",
      icon: ShieldCheck,
    },
    { 
      value: `${complianceScore}%`, 
      label: "Compliance Score", 
      color: "border-l-blue-500",
      icon: CheckCircle2,
    },
    { 
      value: warningInspections.length.toString(), 
      label: "Pending Reviews", 
      color: "border-l-orange-500",
      icon: AlertTriangle,
    },
    { 
      value: (inspections?.length || 0).toString(), 
      label: "Total Inspections", 
      color: "border-l-primary",
      icon: FileCheck,
    },
  ];

  const certifications = [
    { name: "OSHA 30-Hour", status: "Valid", expiry: "Dec 2025", urgent: false },
    { name: "Heavy Machinery License", status: "Valid", expiry: "Dec 2025", urgent: false },
    { name: "First Aid Response", status: "Renewal Required", expiry: "Expired", urgent: true },
    { name: "Confined Space Entry", status: "Valid", expiry: "Mar 2026", urgent: false },
    { name: "Fall Protection", status: "Due Soon", expiry: "15 days", urgent: true },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground" data-testid="text-page-title">
              Safety & Compliance
            </h1>
            <p className="text-muted-foreground mt-1">ERP Safety Module - Monitor incidents, inspections, and crew certifications.</p>
          </div>
          <div className="flex gap-2">
            <Button variant="destructive" className="gap-2" data-testid="button-report-incident">
              <AlertTriangle className="h-4 w-4" /> Report Incident
            </Button>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button className="gap-2" data-testid="button-new-inspection">
                  <Plus className="h-4 w-4" /> New Inspection
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-card border-white/10">
                <DialogHeader>
                  <DialogTitle>Log Safety Inspection</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 mt-4">
                  <div className="space-y-2">
                    <Label>Site / Location</Label>
                    <Input
                      placeholder="e.g., Site A - Foundation"
                      value={newInspection.site}
                      onChange={(e) => setNewInspection({ ...newInspection, site: e.target.value })}
                      className="bg-background border-white/10"
                      data-testid="input-site"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Inspection Type</Label>
                      <Select value={newInspection.type} onValueChange={(v) => setNewInspection({ ...newInspection, type: v })}>
                        <SelectTrigger className="bg-background border-white/10" data-testid="select-type">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Foundation">Foundation</SelectItem>
                          <SelectItem value="Electrical">Electrical</SelectItem>
                          <SelectItem value="Structural">Structural</SelectItem>
                          <SelectItem value="Crane Operations">Crane Operations</SelectItem>
                          <SelectItem value="Fire Safety">Fire Safety</SelectItem>
                          <SelectItem value="PPE Compliance">PPE Compliance</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Result</Label>
                      <Select value={newInspection.status} onValueChange={(v) => setNewInspection({ ...newInspection, status: v })}>
                        <SelectTrigger className="bg-background border-white/10" data-testid="select-status">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Passed">Passed</SelectItem>
                          <SelectItem value="Warning">Warning</SelectItem>
                          <SelectItem value="Failed">Failed</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>Inspector Name</Label>
                    <Input
                      placeholder="e.g., John Smith"
                      value={newInspection.inspector}
                      onChange={(e) => setNewInspection({ ...newInspection, inspector: e.target.value })}
                      className="bg-background border-white/10"
                      data-testid="input-inspector"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Notes (Optional)</Label>
                    <Textarea
                      placeholder="Additional inspection notes..."
                      value={newInspection.notes}
                      onChange={(e) => setNewInspection({ ...newInspection, notes: e.target.value })}
                      className="bg-background border-white/10"
                      data-testid="input-notes"
                    />
                  </div>
                  <Button 
                    className="w-full" 
                    onClick={() => createInspection.mutate(newInspection)}
                    disabled={!newInspection.site || !newInspection.inspector}
                    data-testid="button-submit"
                  >
                    Log Inspection
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          {stats.map((stat, i) => (
            <Card key={i} className={`bg-card border-white/5 border-l-4 ${stat.color}`}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold font-display" data-testid={`stat-${i}`}>
                      {stat.value}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">{stat.label}</p>
                  </div>
                  <stat.icon className="h-6 w-6 text-muted-foreground" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          <Card className="border-white/5 bg-card">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <FileCheck className="h-5 w-5 text-primary" /> Recent Inspections
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="text-center py-8 text-muted-foreground">Loading inspections...</div>
              ) : inspections && inspections.length > 0 ? (
                <div className="space-y-4">
                  {inspections.slice(0, 5).map((insp) => (
                    <div 
                      key={insp.id} 
                      className="flex items-center justify-between p-3 bg-secondary/30 rounded-sm border border-white/5"
                      data-testid={`inspection-${insp.id}`}
                    >
                      <div>
                        <div className="font-medium text-sm" data-testid={`inspection-site-${insp.id}`}>
                          {insp.site} - {insp.type}
                        </div>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
                          <User className="h-3 w-3" /> {insp.inspector}
                          <span>•</span>
                          <Calendar className="h-3 w-3" />
                          {insp.date ? format(new Date(insp.date), 'MMM dd, yyyy') : 'Unknown'}
                        </div>
                      </div>
                      <div className={`px-2 py-1 rounded text-xs font-bold ${
                        insp.status === 'Passed' ? 'bg-green-500/20 text-green-500' : 
                        insp.status === 'Warning' ? 'bg-yellow-500/20 text-yellow-500' :
                        'bg-red-500/20 text-red-500'
                      }`} data-testid={`inspection-status-${insp.id}`}>
                        {insp.status}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No inspections logged yet. Create your first inspection record.
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="border-white/5 bg-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <HardHat className="h-5 w-5 text-primary" /> Training & Certifications
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {certifications.map((cert, i) => (
                  <div key={i} className="flex justify-between items-center" data-testid={`cert-${i}`}>
                    <div>
                      <div className="font-medium text-sm">{cert.name}</div>
                      <div className={`text-xs ${cert.urgent ? 'text-red-400' : 'text-muted-foreground'}`}>
                        {cert.status === 'Valid' ? `Valid until ${cert.expiry}` : cert.status}
                      </div>
                    </div>
                    <Button 
                      size="sm" 
                      variant="outline" 
                      className={cert.urgent 
                        ? "border-red-500/20 text-red-400 hover:text-red-500" 
                        : "border-white/10"
                      }
                    >
                      {cert.urgent ? 'Renew' : 'View'}
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="border-white/5 bg-card">
          <CardHeader>
            <CardTitle>Inspection Summary by Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-sm">
                <div className="flex items-center gap-3 mb-2">
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                  <span className="font-medium">Passed</span>
                </div>
                <div className="text-2xl font-bold font-display">{passedInspections.length}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {inspections?.length ? Math.round((passedInspections.length / inspections.length) * 100) : 0}% of total
                </div>
              </div>
              <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-sm">
                <div className="flex items-center gap-3 mb-2">
                  <AlertTriangle className="h-5 w-5 text-yellow-500" />
                  <span className="font-medium">Warnings</span>
                </div>
                <div className="text-2xl font-bold font-display">{warningInspections.length}</div>
                <div className="text-xs text-muted-foreground mt-1">Needs attention</div>
              </div>
              <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-sm">
                <div className="flex items-center gap-3 mb-2">
                  <AlertTriangle className="h-5 w-5 text-red-500" />
                  <span className="font-medium">Failed</span>
                </div>
                <div className="text-2xl font-bold font-display">{failedInspections.length}</div>
                <div className="text-xs text-muted-foreground mt-1">Requires immediate action</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
