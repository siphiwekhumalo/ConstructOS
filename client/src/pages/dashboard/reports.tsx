import { DashboardLayout } from "@/components/dashboard-layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { BarChart3, FileSpreadsheet, Share2, RefreshCw, ExternalLink, Database } from "lucide-react";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";

export default function DashboardReports() {
  const [isPowerBIConnected, setIsPowerBIConnected] = useState(false);
  const { toast } = useToast();

  const handleConnect = () => {
    setIsPowerBIConnected(true);
    toast({
      title: "PowerBI Connected",
      description: "Successfully linked to your corporate PowerBI workspace.",
    });
  };

  const handleExport = (format: string) => {
    toast({
      title: "Export Started",
      description: `Generating ${format} report. Download will start shortly.`,
    });
  };

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground">Analytics & Reports</h1>
            <p className="text-muted-foreground mt-1">Advanced visualization and data export tools.</p>
          </div>
          <div className="flex gap-2">
             <Button variant="outline" className="gap-2 border-white/10" onClick={() => handleExport('Excel')}>
               <FileSpreadsheet className="h-4 w-4" /> Export to Excel
             </Button>
             <Button variant="outline" className="gap-2 border-white/10" onClick={() => handleExport('Google Sheets')}>
               <Share2 className="h-4 w-4" /> Sync to Sheets
             </Button>
          </div>
        </div>

        <div className="grid gap-6">
          {/* PowerBI Integration Section */}
          <Card className="bg-card border-white/5 overflow-hidden">
            <CardHeader className="border-b border-white/5 bg-secondary/20">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="h-8 w-8 bg-[#F2C811] rounded-sm flex items-center justify-center text-black font-bold text-xs">
                    PBI
                  </div>
                  <div>
                    <CardTitle>PowerBI Integration</CardTitle>
                    <CardDescription>Embedded analytics from your workspace</CardDescription>
                  </div>
                </div>
                {!isPowerBIConnected ? (
                  <Button onClick={handleConnect} className="bg-[#F2C811] text-black hover:bg-[#F2C811]/90">
                    Connect Account
                  </Button>
                ) : (
                  <div className="flex items-center gap-2">
                    <div className="text-xs text-muted-foreground flex items-center gap-1">
                      <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse" />
                      Live Sync
                    </div>
                    <Button variant="ghost" size="icon" onClick={() => setIsPowerBIConnected(false)}>
                      <RefreshCw className="h-4 w-4" />
                    </Button>
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent className="p-0 min-h-[500px] relative bg-black/20">
              {!isPowerBIConnected ? (
                <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-8">
                   <BarChart3 className="h-16 w-16 text-muted-foreground mb-4 opacity-20" />
                   <h3 className="text-lg font-medium mb-2">No Report Loaded</h3>
                   <p className="text-muted-foreground max-w-md mb-6">
                     Connect your PowerBI account to view real-time construction analytics, resource forecasting, and cross-project performance metrics directly in this dashboard.
                   </p>
                   <Button variant="outline" onClick={handleConnect} className="border-white/10">
                     Connect PowerBI
                   </Button>
                </div>
              ) : (
                <div className="p-6 space-y-6">
                  {/* Mock PowerBI Dashboard UI */}
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-4">
                       <Select defaultValue="overview">
                         <SelectTrigger className="w-[200px] bg-background border-white/10">
                           <SelectValue placeholder="Select Report" />
                         </SelectTrigger>
                         <SelectContent>
                           <SelectItem value="overview">Executive Overview</SelectItem>
                           <SelectItem value="costs">Cost Analysis</SelectItem>
                           <SelectItem value="labor">Labor Efficiency</SelectItem>
                         </SelectContent>
                       </Select>
                       <span className="text-xs text-muted-foreground">Last refreshed: Just now</span>
                    </div>
                    <Button variant="ghost" size="sm" className="gap-2 text-muted-foreground">
                      <ExternalLink className="h-3 w-3" /> Open in PowerBI
                    </Button>
                  </div>

                  <div className="grid md:grid-cols-3 gap-4">
                    {/* Mock Charts */}
                    <div className="bg-background p-4 rounded-sm border border-white/5 h-[200px] flex flex-col">
                      <span className="text-xs font-bold text-muted-foreground mb-4">COST VARIANCE BY PROJECT</span>
                      <div className="flex-1 flex items-end gap-2 justify-between px-2">
                        {[60, 45, 80, 30, 70, 55].map((h, i) => (
                          <div key={i} className="w-full bg-primary/80 hover:bg-primary transition-colors rounded-t-sm" style={{ height: `${h}%` }} />
                        ))}
                      </div>
                    </div>
                    <div className="bg-background p-4 rounded-sm border border-white/5 h-[200px] flex flex-col">
                      <span className="text-xs font-bold text-muted-foreground mb-4">RESOURCE ALLOCATION</span>
                      <div className="flex-1 flex items-center justify-center relative">
                         <div className="h-24 w-24 rounded-full border-8 border-secondary border-t-primary border-r-primary/50" />
                         <div className="absolute text-2xl font-bold">78%</div>
                      </div>
                    </div>
                    <div className="bg-background p-4 rounded-sm border border-white/5 h-[200px] flex flex-col">
                      <span className="text-xs font-bold text-muted-foreground mb-4">SAFETY INCIDENTS TREND</span>
                      <div className="flex-1 flex items-end">
                         <svg className="w-full h-full" viewBox="0 0 100 50" preserveAspectRatio="none">
                           <path d="M0,50 L10,40 L30,45 L50,20 L70,25 L90,10 L100,30 V50 H0 Z" fill="currentColor" className="text-primary/20" />
                           <path d="M0,50 L10,40 L30,45 L50,20 L70,25 L90,10 L100,30" fill="none" stroke="currentColor" strokeWidth="2" className="text-primary" />
                         </svg>
                      </div>
                    </div>
                  </div>

                  <div className="bg-background p-4 rounded-sm border border-white/5 h-[300px]">
                    <span className="text-xs font-bold text-muted-foreground mb-4 block">PROJECT TIMELINE FORECAST</span>
                    {/* Gantt Chart Mock */}
                    <div className="space-y-4 mt-6">
                       <div className="space-y-1">
                         <div className="flex justify-between text-xs">
                           <span>Phase 1: Foundation</span>
                           <span className="text-green-500">Completed</span>
                         </div>
                         <div className="h-2 bg-secondary rounded-full overflow-hidden">
                           <div className="h-full bg-green-500 w-full" />
                         </div>
                       </div>
                       <div className="space-y-1">
                         <div className="flex justify-between text-xs">
                           <span>Phase 2: Structure</span>
                           <span className="text-primary">In Progress</span>
                         </div>
                         <div className="h-2 bg-secondary rounded-full overflow-hidden">
                           <div className="h-full bg-primary w-[65%]" />
                         </div>
                       </div>
                       <div className="space-y-1">
                         <div className="flex justify-between text-xs">
                           <span>Phase 3: Electrical</span>
                           <span className="text-muted-foreground">Pending</span>
                         </div>
                         <div className="h-2 bg-secondary rounded-full overflow-hidden">
                           <div className="h-full bg-white/10 w-[20%]" />
                         </div>
                       </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Data Sync Section */}
          <div className="grid md:grid-cols-2 gap-6">
            <Card className="bg-card border-white/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileSpreadsheet className="h-5 w-5 text-green-600" /> Excel Export
                </CardTitle>
                <CardDescription>Download raw data for offline analysis</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-3 border border-white/5 rounded-sm hover:bg-white/5 transition-colors">
                  <div className="flex items-center gap-3">
                    <Database className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Financial Transactions</span>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => handleExport('Excel')}>Download .xlsx</Button>
                </div>
                <div className="flex items-center justify-between p-3 border border-white/5 rounded-sm hover:bg-white/5 transition-colors">
                  <div className="flex items-center gap-3">
                    <Database className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Equipment Logs</span>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => handleExport('Excel')}>Download .xlsx</Button>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-card border-white/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Share2 className="h-5 w-5 text-blue-500" /> Google Sheets Sync
                </CardTitle>
                <CardDescription>Keep your team's spreadsheets up to date</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-3 border border-white/5 rounded-sm hover:bg-white/5 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="h-2 w-2 bg-green-500 rounded-full" />
                    <span className="text-sm font-medium">Project Timelines</span>
                  </div>
                  <div className="text-xs text-muted-foreground">Auto-sync: ON</div>
                </div>
                <div className="flex items-center justify-between p-3 border border-white/5 rounded-sm hover:bg-white/5 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="h-2 w-2 bg-green-500 rounded-full" />
                    <span className="text-sm font-medium">Safety Incident Reports</span>
                  </div>
                  <div className="text-xs text-muted-foreground">Auto-sync: ON</div>
                </div>
                <Button className="w-full variant-outline border-white/10" onClick={() => handleExport('Google Sheets')}>
                  Force Sync Now
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
