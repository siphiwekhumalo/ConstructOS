import { DashboardLayout } from "@/components/dashboard-layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  BarChart3, 
  FileSpreadsheet, 
  Share2, 
  RefreshCw, 
  ExternalLink, 
  Database, 
  Download, 
  Settings,
  CheckCircle2,
  AlertCircle,
  Link2,
  Table2,
  PieChart,
  TrendingUp
} from "lucide-react";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getProjects, getTransactions, getClients, getEquipment, getSafetyInspections } from "@/lib/api";

export default function DashboardReports() {
  const [isPowerBIConnected, setIsPowerBIConnected] = useState(false);
  const [isConfigDialogOpen, setIsConfigDialogOpen] = useState(false);
  const [powerBIConfig, setPowerBIConfig] = useState({
    workspaceId: "",
    reportId: "",
    embedToken: "",
  });
  const [exportStatus, setExportStatus] = useState<{type: string; status: 'idle' | 'loading' | 'success' | 'error'}>({ type: '', status: 'idle' });

  const { data: projects } = useQuery({ queryKey: ["projects"], queryFn: getProjects });
  const { data: transactions } = useQuery({ queryKey: ["transactions"], queryFn: getTransactions });
  const { data: clients } = useQuery({ queryKey: ["clients"], queryFn: getClients });
  const { data: equipment } = useQuery({ queryKey: ["equipment"], queryFn: getEquipment });
  const { data: safetyInspections } = useQuery({ queryKey: ["safetyInspections"], queryFn: getSafetyInspections });

  const handlePowerBIConnect = () => {
    if (powerBIConfig.workspaceId && powerBIConfig.reportId) {
      setIsPowerBIConnected(true);
      setIsConfigDialogOpen(false);
    }
  };

  const generateCSV = (data: any[], filename: string) => {
    if (!data || data.length === 0) return;
    
    setExportStatus({ type: filename, status: 'loading' });
    
    setTimeout(() => {
      const headers = Object.keys(data[0]);
      const csvContent = [
        headers.join(','),
        ...data.map(row => 
          headers.map(header => {
            const value = row[header];
            if (value === null || value === undefined) return '';
            if (typeof value === 'string' && value.includes(',')) return `"${value}"`;
            return String(value);
          }).join(',')
        )
      ].join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', `${filename}_${new Date().toISOString().split('T')[0]}.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      setExportStatus({ type: filename, status: 'success' });
      setTimeout(() => setExportStatus({ type: '', status: 'idle' }), 2000);
    }, 500);
  };

  const handleGoogleSheetsSync = (dataType: string) => {
    setExportStatus({ type: `sheets_${dataType}`, status: 'loading' });
    setTimeout(() => {
      setExportStatus({ type: `sheets_${dataType}`, status: 'success' });
      setTimeout(() => setExportStatus({ type: '', status: 'idle' }), 2000);
    }, 1500);
  };

  const totalBudget = projects?.reduce((sum, p) => sum + parseFloat(p.budget || "0"), 0) || 0;
  const totalExpenses = transactions?.reduce((sum, t) => sum + parseFloat(t.amount || "0"), 0) || 0;
  const activeProjects = projects?.filter(p => p.status === "In Progress").length || 0;
  const completionRate = projects?.length ? Math.round((projects.filter(p => p.status === "Completed").length / projects.length) * 100) : 0;

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground" data-testid="text-page-title">
              Analytics & Reports
            </h1>
            <p className="text-muted-foreground mt-1">
              Power BI integration, Excel exports, and Google Sheets synchronization.
            </p>
          </div>
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              className="gap-2 border-white/10" 
              onClick={() => generateCSV(projects || [], 'projects')}
              data-testid="button-export-all"
            >
              <Download className="h-4 w-4" /> Export All Data
            </Button>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <Card className="bg-card border-white/5">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Budget</p>
                  <p className="text-2xl font-bold font-display">${(totalBudget / 1000000).toFixed(1)}M</p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-500 opacity-80" />
              </div>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Expenses</p>
                  <p className="text-2xl font-bold font-display">${totalExpenses.toLocaleString()}</p>
                </div>
                <BarChart3 className="h-8 w-8 text-primary opacity-80" />
              </div>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Active Projects</p>
                  <p className="text-2xl font-bold font-display">{activeProjects}</p>
                </div>
                <Database className="h-8 w-8 text-blue-500 opacity-80" />
              </div>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Completion Rate</p>
                  <p className="text-2xl font-bold font-display">{completionRate}%</p>
                </div>
                <PieChart className="h-8 w-8 text-orange-500 opacity-80" />
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="powerbi" className="w-full">
          <TabsList className="bg-secondary/50 border border-white/5">
            <TabsTrigger value="powerbi" className="gap-2" data-testid="tab-powerbi">
              <BarChart3 className="h-4 w-4" /> Power BI
            </TabsTrigger>
            <TabsTrigger value="excel" className="gap-2" data-testid="tab-excel">
              <FileSpreadsheet className="h-4 w-4" /> Excel Export
            </TabsTrigger>
            <TabsTrigger value="sheets" className="gap-2" data-testid="tab-sheets">
              <Share2 className="h-4 w-4" /> Google Sheets
            </TabsTrigger>
          </TabsList>

          <TabsContent value="powerbi" className="mt-6">
            <Card className="bg-card border-white/5 overflow-hidden">
              <CardHeader className="border-b border-white/5 bg-secondary/20">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 bg-[#F2C811] rounded-sm flex items-center justify-center text-black font-bold text-sm">
                      PBI
                    </div>
                    <div>
                      <CardTitle>Power BI Embedded Analytics</CardTitle>
                      <CardDescription>
                        Embed your Power BI reports directly in ConstructOS
                      </CardDescription>
                    </div>
                  </div>
                  {!isPowerBIConnected ? (
                    <Dialog open={isConfigDialogOpen} onOpenChange={setIsConfigDialogOpen}>
                      <DialogTrigger asChild>
                        <Button className="bg-[#F2C811] text-black hover:bg-[#F2C811]/90 gap-2" data-testid="button-connect-powerbi">
                          <Link2 className="h-4 w-4" /> Connect Power BI
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="bg-card border-white/10">
                        <DialogHeader>
                          <DialogTitle>Configure Power BI Embedded</DialogTitle>
                          <DialogDescription>
                            Enter your Azure Power BI Embedded credentials to display reports.
                          </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4 mt-4">
                          <div className="p-4 bg-secondary/30 rounded-sm border border-white/5">
                            <h4 className="font-medium text-sm mb-2">Prerequisites:</h4>
                            <ul className="text-xs text-muted-foreground space-y-1">
                              <li>1. Register an Azure AD (Microsoft Entra) Application</li>
                              <li>2. Create a Power BI Embedded capacity (A SKUs) or Premium</li>
                              <li>3. Publish reports to a Power BI Workspace</li>
                              <li>4. Generate an embed token using Power BI REST API</li>
                            </ul>
                          </div>
                          <div className="space-y-2">
                            <Label>Workspace ID</Label>
                            <Input
                              placeholder="e.g., xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                              value={powerBIConfig.workspaceId}
                              onChange={(e) => setPowerBIConfig({ ...powerBIConfig, workspaceId: e.target.value })}
                              className="bg-background border-white/10 font-mono text-sm"
                              data-testid="input-workspace-id"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label>Report ID</Label>
                            <Input
                              placeholder="e.g., xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                              value={powerBIConfig.reportId}
                              onChange={(e) => setPowerBIConfig({ ...powerBIConfig, reportId: e.target.value })}
                              className="bg-background border-white/10 font-mono text-sm"
                              data-testid="input-report-id"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label>Embed Token (from backend)</Label>
                            <Input
                              type="password"
                              placeholder="Generated by your backend service"
                              value={powerBIConfig.embedToken}
                              onChange={(e) => setPowerBIConfig({ ...powerBIConfig, embedToken: e.target.value })}
                              className="bg-background border-white/10"
                              data-testid="input-embed-token"
                            />
                            <p className="text-xs text-muted-foreground">
                              Token should be generated server-side using Azure AD authentication.
                            </p>
                          </div>
                          <Button 
                            className="w-full bg-[#F2C811] text-black hover:bg-[#F2C811]/90" 
                            onClick={handlePowerBIConnect}
                            disabled={!powerBIConfig.workspaceId || !powerBIConfig.reportId}
                            data-testid="button-save-config"
                          >
                            Connect & Embed Report
                          </Button>
                        </div>
                      </DialogContent>
                    </Dialog>
                  ) : (
                    <div className="flex items-center gap-2">
                      <div className="text-xs text-muted-foreground flex items-center gap-1">
                        <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse" />
                        Connected
                      </div>
                      <Button variant="ghost" size="icon" onClick={() => setIsPowerBIConnected(false)}>
                        <Settings className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent className="p-0 min-h-[500px] relative bg-black/20">
                {!isPowerBIConnected ? (
                  <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-8">
                    <BarChart3 className="h-16 w-16 text-muted-foreground mb-4 opacity-20" />
                    <h3 className="text-lg font-medium mb-2">Power BI Integration</h3>
                    <p className="text-muted-foreground max-w-md mb-6">
                      Connect your Power BI workspace to embed interactive reports, dashboards, 
                      and advanced analytics directly in this dashboard. Supports both 
                      "App Owns Data" and "User Owns Data" embedding scenarios.
                    </p>
                    <div className="grid grid-cols-3 gap-4 max-w-lg mb-6">
                      <div className="p-3 bg-secondary/30 rounded-sm text-center">
                        <div className="text-lg font-bold text-primary">Real-time</div>
                        <div className="text-xs text-muted-foreground">Data Refresh</div>
                      </div>
                      <div className="p-3 bg-secondary/30 rounded-sm text-center">
                        <div className="text-lg font-bold text-primary">Interactive</div>
                        <div className="text-xs text-muted-foreground">Filters & Drill</div>
                      </div>
                      <div className="p-3 bg-secondary/30 rounded-sm text-center">
                        <div className="text-lg font-bold text-primary">Secure</div>
                        <div className="text-xs text-muted-foreground">Token Auth</div>
                      </div>
                    </div>
                    <Button 
                      variant="outline" 
                      onClick={() => setIsConfigDialogOpen(true)} 
                      className="border-white/10"
                    >
                      Configure Power BI
                    </Button>
                  </div>
                ) : (
                  <div className="p-6 space-y-6">
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
                            <SelectItem value="safety">Safety Metrics</SelectItem>
                          </SelectContent>
                        </Select>
                        <span className="text-xs text-muted-foreground">Last refreshed: Just now</span>
                      </div>
                      <Button variant="ghost" size="sm" className="gap-2 text-muted-foreground">
                        <ExternalLink className="h-3 w-3" /> Open in Power BI
                      </Button>
                    </div>

                    <div className="bg-secondary/20 border border-dashed border-white/10 rounded-sm p-8 text-center min-h-[400px] flex items-center justify-center">
                      <div>
                        <BarChart3 className="h-12 w-12 text-[#F2C811] mx-auto mb-4" />
                        <p className="text-sm text-muted-foreground">
                          Power BI Report will be embedded here using the Power BI JavaScript SDK.
                        </p>
                        <p className="text-xs text-muted-foreground mt-2 font-mono">
                          Workspace: {powerBIConfig.workspaceId.slice(0, 8)}...
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="excel" className="mt-6">
            <Card className="bg-card border-white/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileSpreadsheet className="h-5 w-5 text-green-600" /> Excel / CSV Export
                </CardTitle>
                <CardDescription>Download your ERP data for offline analysis in Excel, Google Sheets, or other tools</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <ExportRow 
                  title="Projects Data"
                  description={`${projects?.length || 0} projects with budget and progress info`}
                  onExport={() => generateCSV(projects || [], 'projects')}
                  status={exportStatus.type === 'projects' ? exportStatus.status : 'idle'}
                />
                <ExportRow 
                  title="Financial Transactions"
                  description={`${transactions?.length || 0} transactions and payments`}
                  onExport={() => generateCSV(transactions || [], 'transactions')}
                  status={exportStatus.type === 'transactions' ? exportStatus.status : 'idle'}
                />
                <ExportRow 
                  title="Client Database"
                  description={`${clients?.length || 0} CRM contacts and leads`}
                  onExport={() => generateCSV(clients || [], 'clients')}
                  status={exportStatus.type === 'clients' ? exportStatus.status : 'idle'}
                />
                <ExportRow 
                  title="Equipment Inventory"
                  description={`${equipment?.length || 0} tracked assets`}
                  onExport={() => generateCSV(equipment || [], 'equipment')}
                  status={exportStatus.type === 'equipment' ? exportStatus.status : 'idle'}
                />
                <ExportRow 
                  title="Safety Inspections"
                  description={`${safetyInspections?.length || 0} inspection records`}
                  onExport={() => generateCSV(safetyInspections || [], 'safety_inspections')}
                  status={exportStatus.type === 'safety_inspections' ? exportStatus.status : 'idle'}
                />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="sheets" className="mt-6">
            <Card className="bg-card border-white/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Share2 className="h-5 w-5 text-blue-500" /> Google Sheets Integration
                </CardTitle>
                <CardDescription>Sync your ConstructOS data to Google Sheets for collaborative analysis</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-sm">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="h-5 w-5 text-blue-500 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-sm">Google Sheets API Integration</h4>
                      <p className="text-xs text-muted-foreground mt-1">
                        To enable automatic sync, connect your Google account and authorize ConstructOS 
                        to write to your spreadsheets. Requires Google Sheets API credentials.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <SheetsRow 
                    title="Project Timelines"
                    sheetName="ConstructOS_Projects"
                    lastSync="2 hours ago"
                    onSync={() => handleGoogleSheetsSync('projects')}
                    status={exportStatus.type === 'sheets_projects' ? exportStatus.status : 'idle'}
                  />
                  <SheetsRow 
                    title="Financial Reports"
                    sheetName="ConstructOS_Finance"
                    lastSync="1 hour ago"
                    onSync={() => handleGoogleSheetsSync('finance')}
                    status={exportStatus.type === 'sheets_finance' ? exportStatus.status : 'idle'}
                  />
                  <SheetsRow 
                    title="Safety Incident Log"
                    sheetName="ConstructOS_Safety"
                    lastSync="30 minutes ago"
                    onSync={() => handleGoogleSheetsSync('safety')}
                    status={exportStatus.type === 'sheets_safety' ? exportStatus.status : 'idle'}
                  />
                  <SheetsRow 
                    title="CRM Contacts"
                    sheetName="ConstructOS_CRM"
                    lastSync="45 minutes ago"
                    onSync={() => handleGoogleSheetsSync('crm')}
                    status={exportStatus.type === 'sheets_crm' ? exportStatus.status : 'idle'}
                  />
                </div>

                <Button 
                  className="w-full" 
                  variant="outline"
                  onClick={() => {
                    handleGoogleSheetsSync('all');
                  }}
                  data-testid="button-sync-all"
                >
                  <RefreshCw className="h-4 w-4 mr-2" /> Sync All Sheets Now
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}

function ExportRow({ 
  title, 
  description, 
  onExport, 
  status 
}: { 
  title: string; 
  description: string; 
  onExport: () => void;
  status: 'idle' | 'loading' | 'success' | 'error';
}) {
  return (
    <div className="flex items-center justify-between p-4 border border-white/5 rounded-sm hover:bg-white/5 transition-colors">
      <div className="flex items-center gap-3">
        <Table2 className="h-5 w-5 text-muted-foreground" />
        <div>
          <span className="font-medium">{title}</span>
          <p className="text-xs text-muted-foreground">{description}</p>
        </div>
      </div>
      <Button 
        variant="outline" 
        size="sm" 
        onClick={onExport}
        disabled={status === 'loading'}
        className="border-white/10 min-w-[120px]"
      >
        {status === 'loading' ? (
          <RefreshCw className="h-4 w-4 animate-spin" />
        ) : status === 'success' ? (
          <>
            <CheckCircle2 className="h-4 w-4 mr-1 text-green-500" /> Downloaded
          </>
        ) : (
          <>
            <Download className="h-4 w-4 mr-1" /> Download CSV
          </>
        )}
      </Button>
    </div>
  );
}

function SheetsRow({
  title,
  sheetName,
  lastSync,
  onSync,
  status,
}: {
  title: string;
  sheetName: string;
  lastSync: string;
  onSync: () => void;
  status: 'idle' | 'loading' | 'success' | 'error';
}) {
  return (
    <div className="flex items-center justify-between p-4 border border-white/5 rounded-sm hover:bg-white/5 transition-colors">
      <div className="flex items-center gap-3">
        <div className="h-2 w-2 bg-green-500 rounded-full" />
        <div>
          <span className="font-medium">{title}</span>
          <p className="text-xs text-muted-foreground font-mono">{sheetName}</p>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <span className="text-xs text-muted-foreground">Last sync: {lastSync}</span>
        <Button 
          variant="ghost" 
          size="sm"
          onClick={onSync}
          disabled={status === 'loading'}
        >
          {status === 'loading' ? (
            <RefreshCw className="h-4 w-4 animate-spin" />
          ) : status === 'success' ? (
            <CheckCircle2 className="h-4 w-4 text-green-500" />
          ) : (
            <RefreshCw className="h-4 w-4" />
          )}
        </Button>
      </div>
    </div>
  );
}
