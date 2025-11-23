import { DashboardLayout } from "@/components/dashboard-layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ShieldCheck, AlertTriangle, FileCheck, HardHat } from "lucide-react";

export default function DashboardSafety() {
  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground">Safety & Compliance</h1>
            <p className="text-muted-foreground mt-1">Monitor incidents, inspections, and crew certifications.</p>
          </div>
          <Button className="gap-2" variant="destructive">
            <AlertTriangle className="h-4 w-4" /> Report Incident
          </Button>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <Card className="bg-card border-white/5 border-l-4 border-l-green-500">
            <CardContent className="pt-6">
              <div className="text-2xl font-bold font-display">142 Days</div>
              <p className="text-xs text-muted-foreground mt-1">Incident Free Streak</p>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5">
            <CardContent className="pt-6">
              <div className="text-2xl font-bold font-display">98%</div>
              <p className="text-xs text-muted-foreground mt-1">Compliance Score</p>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5">
            <CardContent className="pt-6">
              <div className="text-2xl font-bold font-display">12</div>
              <p className="text-xs text-muted-foreground mt-1">Pending Inspections</p>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5">
            <CardContent className="pt-6">
              <div className="text-2xl font-bold font-display">45</div>
              <p className="text-xs text-muted-foreground mt-1">Active Certifications</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
           <Card className="border-white/5 bg-card">
             <CardHeader>
               <CardTitle className="flex items-center gap-2">
                 <FileCheck className="h-5 w-5 text-primary" /> Recent Inspections
               </CardTitle>
             </CardHeader>
             <CardContent>
               <div className="space-y-4">
                 {[
                   { site: "Site A - Foundation", status: "Passed", date: "Today", inspector: "John D." },
                   { site: "Site B - Electrical", status: "Warning", date: "Yesterday", inspector: "Sarah M." },
                   { site: "Site A - Crane Ops", status: "Passed", date: "Oct 22", inspector: "Mike R." },
                 ].map((insp, i) => (
                   <div key={i} className="flex items-center justify-between p-3 bg-secondary/30 rounded-sm border border-white/5">
                      <div>
                        <div className="font-medium text-sm">{insp.site}</div>
                        <div className="text-xs text-muted-foreground">Inspector: {insp.inspector}</div>
                      </div>
                      <div className={`px-2 py-1 rounded text-xs font-bold ${
                        insp.status === 'Passed' ? 'bg-green-500/20 text-green-500' : 'bg-yellow-500/20 text-yellow-500'
                      }`}>
                        {insp.status}
                      </div>
                   </div>
                 ))}
               </div>
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
                 <div className="flex justify-between items-center">
                   <div>
                     <div className="font-medium text-sm">OSHA 30-Hour</div>
                     <div className="text-xs text-muted-foreground">Due in 15 days</div>
                   </div>
                   <Button size="sm" variant="outline" className="border-white/10">Assign</Button>
                 </div>
                 <div className="flex justify-between items-center">
                   <div>
                     <div className="font-medium text-sm">Heavy Machinery License</div>
                     <div className="text-xs text-muted-foreground">Valid until Dec 2025</div>
                   </div>
                   <Button size="sm" variant="outline" className="border-white/10">View</Button>
                 </div>
                 <div className="flex justify-between items-center">
                   <div>
                     <div className="font-medium text-sm">First Aid Response</div>
                     <div className="text-xs text-muted-foreground">Renewal Required</div>
                   </div>
                   <Button size="sm" variant="outline" className="border-red-500/20 text-red-400 hover:text-red-500">Renew</Button>
                 </div>
               </div>
             </CardContent>
           </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
