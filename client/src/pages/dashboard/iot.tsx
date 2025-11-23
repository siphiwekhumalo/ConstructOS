import { DashboardLayout } from "@/components/dashboard-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, Thermometer, Wind, Wifi } from "lucide-react";

export default function DashboardIoT() {
  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="relative flex h-3 w-3">
               <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"></span>
               <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
            </div>
            <span className="font-mono text-sm text-green-500">LIVE FEED ACTIVE</span>
          </div>
          <h1 className="text-3xl font-display font-bold text-foreground">IoT Site Monitor</h1>
          <p className="text-muted-foreground mt-1">Real-time sensor data from Site Alpha (Django Channels Integration).</p>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Main Map Visualization Placeholder */}
          <Card className="lg:col-span-2 bg-card border-white/5 min-h-[400px] relative overflow-hidden">
            <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1621905251189-fc015305ea03?q=80&w=2000&auto=format&fit=crop')] bg-cover bg-center opacity-20 mix-blend-overlay" />
            <div className="absolute inset-0 grid-bg opacity-30 pointer-events-none" />
            
            {/* Mock Sensor Points */}
            <div className="absolute top-1/3 left-1/4 group cursor-pointer">
               <div className="h-4 w-4 bg-green-500 rounded-full border-2 border-white shadow-[0_0_15px_rgba(34,197,94,0.5)] animate-pulse" />
               <div className="absolute top-6 left-1/2 -translate-x-1/2 bg-black/90 text-white text-xs px-2 py-1 rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity">
                 Sensor A1: Normal
               </div>
            </div>

            <div className="absolute bottom-1/3 right-1/3 group cursor-pointer">
               <div className="h-4 w-4 bg-yellow-500 rounded-full border-2 border-white shadow-[0_0_15px_rgba(234,179,8,0.5)]" />
               <div className="absolute top-6 left-1/2 -translate-x-1/2 bg-black/90 text-white text-xs px-2 py-1 rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity">
                 Sensor B4: High Vibration
               </div>
            </div>

            <div className="absolute top-10 right-10 bg-black/80 backdrop-blur border border-white/10 p-4 rounded-sm w-48">
              <h3 className="font-mono text-xs text-muted-foreground mb-2">CONNECTION STATUS</h3>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Latency</span>
                  <span className="text-green-500">24ms</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Packets</span>
                  <span className="text-foreground">1.2k/s</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Uptime</span>
                  <span className="text-foreground">99.9%</span>
                </div>
              </div>
            </div>
          </Card>

          {/* Sensor Cards */}
          <div className="space-y-4">
             <Card className="bg-card border-white/5">
               <CardHeader className="pb-2">
                 <CardTitle className="flex items-center gap-2 text-base">
                   <Thermometer className="h-4 w-4 text-primary" /> Temperature
                 </CardTitle>
               </CardHeader>
               <CardContent>
                 <div className="text-3xl font-bold font-display">72°F</div>
                 <div className="h-1 w-full bg-secondary mt-2 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-400 w-[60%]" />
                 </div>
               </CardContent>
             </Card>

             <Card className="bg-card border-white/5">
               <CardHeader className="pb-2">
                 <CardTitle className="flex items-center gap-2 text-base">
                   <Wind className="h-4 w-4 text-primary" /> Air Quality (AQI)
                 </CardTitle>
               </CardHeader>
               <CardContent>
                 <div className="text-3xl font-bold font-display">45</div>
                 <Badge variant="outline" className="mt-1 text-green-500 border-green-500/20 bg-green-500/10">Good</Badge>
               </CardContent>
             </Card>

             <Card className="bg-card border-white/5">
               <CardHeader className="pb-2">
                 <CardTitle className="flex items-center gap-2 text-base">
                   <Activity className="h-4 w-4 text-primary" /> Vibration Load
                 </CardTitle>
               </CardHeader>
               <CardContent>
                 <div className="text-3xl font-bold font-display">0.4g</div>
                 <p className="text-xs text-muted-foreground mt-1">Structural Integrity: Stable</p>
               </CardContent>
             </Card>
             
             <Card className="bg-card border-white/5">
               <CardHeader className="pb-2">
                 <CardTitle className="flex items-center gap-2 text-base">
                   <Wifi className="h-4 w-4 text-primary" /> Network Strength
                 </CardTitle>
               </CardHeader>
               <CardContent>
                 <div className="text-3xl font-bold font-display">-65dBm</div>
                 <p className="text-xs text-muted-foreground mt-1">Mesh Network: Optimal</p>
               </CardContent>
             </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
