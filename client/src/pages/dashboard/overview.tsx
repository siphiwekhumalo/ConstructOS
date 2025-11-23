import { DashboardLayout } from "@/components/dashboard-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Briefcase, AlertTriangle, CheckCircle2, Clock } from "lucide-react";

const stats = [
  {
    title: "Active Projects",
    value: "12",
    change: "+2 this month",
    icon: Briefcase,
    color: "text-primary",
  },
  {
    title: "Pending Tasks",
    value: "48",
    change: "15 due today",
    icon: Clock,
    color: "text-orange-400",
  },
  {
    title: "Safety Incidents",
    value: "0",
    change: "Last 30 days",
    icon: CheckCircle2,
    color: "text-green-500",
  },
  {
    title: "Critical Alerts",
    value: "3",
    change: "Needs attention",
    icon: AlertTriangle,
    color: "text-red-500",
  },
];

export default function DashboardOverview() {
  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-display font-bold text-foreground">Dashboard Overview</h1>
          <p className="text-muted-foreground mt-1">Welcome back, Site Manager. Here's what's happening today.</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat, index) => (
            <Card key={index} className="bg-card border-white/5 shadow-sm hover:border-white/10 transition-colors">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold font-display">{stat.value}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  {stat.change}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid gap-8 md:grid-cols-2">
           <Card className="border-white/5 bg-card">
             <CardHeader>
               <CardTitle className="text-lg font-display">Recent Activity</CardTitle>
             </CardHeader>
             <CardContent>
               <div className="space-y-4">
                 {[1, 2, 3].map((i) => (
                   <div key={i} className="flex items-start gap-4 pb-4 border-b border-white/5 last:border-0 last:pb-0">
                     <div className="h-2 w-2 mt-2 rounded-full bg-primary" />
                     <div>
                       <p className="text-sm font-medium text-foreground">Blueprint updated for Project Alpha</p>
                       <p className="text-xs text-muted-foreground">2 hours ago by Architect Team</p>
                     </div>
                   </div>
                 ))}
               </div>
             </CardContent>
           </Card>
           
           <Card className="border-white/5 bg-card">
             <CardHeader>
               <CardTitle className="text-lg font-display">Weather Conditions (Site A)</CardTitle>
             </CardHeader>
             <CardContent>
               <div className="flex items-center justify-between">
                 <div className="text-4xl font-bold font-display">72°F</div>
                 <div className="text-right">
                   <div className="text-sm font-medium">Partly Cloudy</div>
                   <div className="text-xs text-muted-foreground">Wind: 5mph NW</div>
                 </div>
               </div>
               <div className="mt-4 h-2 w-full bg-secondary rounded-full overflow-hidden">
                 <div className="h-full bg-yellow-500 w-[60%]" />
               </div>
               <div className="flex justify-between text-xs text-muted-foreground mt-1">
                 <span>Daylight Remaining</span>
                 <span>4h 30m</span>
               </div>
             </CardContent>
           </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
