import { DashboardLayout } from "@/components/dashboard-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  Briefcase, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  Banknote, 
  Users, 
  Truck, 
  TrendingUp,
  ArrowRight,
  Activity
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { getProjects, getTransactions, getClients, getEquipment, 
  getFinanceSummary, getAccountsReceivableDays, getProfitMargin, getCashFlow, 
  getSafetySummary, getReworkCost, getResourceUtilization, getSPIMap, 
  getProjectPortfolioMap, getTrendChart 
} from "@/lib/api";
import { Link } from "wouter";
import { formatCurrency, formatCurrencyCompact } from "@/lib/currency";
import { ProfitMarginChart, BudgetTrendChart, ProjectPortfolioMap } from "@/components/DashboardCharts";

export default function DashboardOverview() {
  const { data: projects } = useQuery({ queryKey: ["projects"], queryFn: getProjects });
  const { data: transactions } = useQuery({ queryKey: ["transactions"], queryFn: getTransactions });
  const { data: clients } = useQuery({ queryKey: ["clients"], queryFn: getClients });
  const { data: equipment } = useQuery({ queryKey: ["equipment"], queryFn: getEquipment });

  // --- Executive Financial Health KPIs ---
  const { data: finance } = useQuery({ queryKey: ["finance"], queryFn: getFinanceSummary });
  const { data: arDays } = useQuery({ queryKey: ["arDays"], queryFn: getAccountsReceivableDays });
  const { data: profitMargin } = useQuery({ queryKey: ["profitMargin"], queryFn: getProfitMargin });
  const { data: cashFlow } = useQuery({ queryKey: ["cashFlow"], queryFn: getCashFlow });

  // --- Compliance & Safety KPIs ---
  const { data: safety } = useQuery({ queryKey: ["safety"], queryFn: getSafetySummary });
  const { data: reworkCost } = useQuery({ queryKey: ["reworkCost"], queryFn: getReworkCost });

  // --- Resource Utilization & SPI ---
  const { data: resourceUtilization } = useQuery({ queryKey: ["resourceUtilization"], queryFn: getResourceUtilization });
  const { data: spiMap } = useQuery({ queryKey: ["spiMap"], queryFn: getSPIMap });

  // --- Portfolio Map & Trend Chart ---
  const { data: projectMap } = useQuery({ queryKey: ["projectMap"], queryFn: getProjectPortfolioMap });
  const { data: trendChart } = useQuery({ queryKey: ["trendChart"], queryFn: getTrendChart });

  const activeProjects = projects?.filter(p => p.status === "In Progress") || [];
  const completedProjects = projects?.filter(p => p.status === "Completed") || [];
  const delayedProjects = projects?.filter(p => p.status === "Delayed") || [];
  
  const totalBudget = projects?.reduce((sum, p) => sum + parseFloat(p.budget || "0"), 0) || 0;
  const totalExpenses = transactions?.reduce((sum, t) => sum + parseFloat(t.amount || "0"), 0) || 0;
  const pendingPayments = transactions?.filter(t => t.status === "Pending") || [];
  
  const activeEquipment = equipment?.filter(e => e.status === "Active") || [];
  const overdueService = equipment?.filter(e => e.nextService === "Overdue") || [];

  const stats = [
    {
      title: "Active Projects",
      value: activeProjects.length.toString(),
      change: `${projects?.length || 0} total`,
      icon: Briefcase,
      color: "text-primary",
      href: "/dashboard/projects",
    },
    {
      title: "Total Revenue",
      value: formatCurrencyCompact(totalBudget),
      change: `${projects?.length || 0} projects`,
      icon: Banknote,
      color: "text-green-500",
      href: "/dashboard/finance",
    },
    {
      title: "Active Clients",
      value: clients?.length.toString() || "0",
      change: "CRM contacts",
      icon: Users,
      color: "text-blue-500",
      href: "/dashboard/crm",
    },
    {
      title: "Equipment Fleet",
      value: equipment?.length.toString() || "0",
      change: `${activeEquipment.length} active`,
      icon: Truck,
      color: "text-orange-400",
      href: "/dashboard/equipment",
    },
  ];

  const alerts = [
    ...(delayedProjects.length > 0 ? [{
      type: "warning",
      message: `${delayedProjects.length} project(s) delayed`,
      icon: AlertTriangle,
    }] : []),
    ...(overdueService.length > 0 ? [{
      type: "error",
      message: `${overdueService.length} equipment service overdue`,
      icon: AlertTriangle,
    }] : []),
    ...(pendingPayments.length > 0 ? [{
      type: "info",
      message: `${pendingPayments.length} pending payment(s)`,
      icon: Clock,
    }] : []),
  ];

  // Type guards and default values for dashboard KPIs
  const safeFinance = finance ?? { total_contract_value: 0 };
  const safeArDays = arDays ?? { value: 0 };
  const safeProfitMargin = profitMargin ?? { gross: 0, net: 0 };
  const safeResourceUtilization = resourceUtilization ?? { percent: 0 };
  const safeSafety = safety ?? { ltir: 0, benchmark: 0, open_issues: 0 };
  const safeReworkCost = reworkCost ?? { percent: 0 };
  const safeSpiMap = spiMap ?? { on_time: 0, at_risk: 0, delayed: 0 };
  const safeProjectMap = Array.isArray(projectMap) ? projectMap : [];
  const safeTrendChart = Array.isArray(trendChart) ? trendChart : [];

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground" data-testid="text-page-title">
              Dashboard Overview
            </h1>
            <p className="text-muted-foreground mt-1">
              Welcome back, Site Manager. Here's your ERP/CRM summary.
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" className="gap-2 border-white/10" data-testid="button-reports">
              <Activity className="h-4 w-4" /> View Reports
            </Button>
          </div>
        </div>

        {alerts.length > 0 && (
          <div className="grid gap-3 md:grid-cols-3">
            {alerts.map((alert, i) => (
              <div 
                key={i}
                className={`flex items-center gap-3 p-4 rounded-sm border ${
                  alert.type === 'error' ? 'bg-red-500/10 border-red-500/20 text-red-400' :
                  alert.type === 'warning' ? 'bg-orange-500/10 border-orange-500/20 text-orange-400' :
                  'bg-blue-500/10 border-blue-500/20 text-blue-400'
                }`}
                data-testid={`alert-${i}`}
              >
                <alert.icon className="h-5 w-5" />
                <span className="text-sm font-medium">{alert.message}</span>
              </div>
            ))}
          </div>
        )}

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat, index) => (
            <Link key={index} href={stat.href}>
              <Card className="bg-card border-white/5 shadow-sm hover:border-primary/30 transition-colors cursor-pointer group">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {stat.title}
                  </CardTitle>
                  <stat.icon className={`h-4 w-4 ${stat.color}`} />
                </CardHeader>
                <CardContent>
                  <div className="flex items-end justify-between">
                    <div>
                      <div className="text-2xl font-bold font-display" data-testid={`stat-value-${index}`}>
                        {stat.value}
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">
                        {stat.change}
                      </p>
                    </div>
                    <ArrowRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>

        <div className="grid gap-8 lg:grid-cols-2">
          <Card className="border-white/5 bg-card">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-lg font-display">Project Status</CardTitle>
              <Link href="/dashboard/projects">
                <Button variant="ghost" size="sm" className="text-primary" data-testid="link-projects">
                  View All <ArrowRight className="h-4 w-4 ml-1" />
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-blue-500/10 border border-blue-500/20 rounded-sm">
                  <div className="flex items-center gap-3">
                    <Clock className="h-5 w-5 text-blue-500" />
                    <span>In Progress</span>
                  </div>
                  <span className="font-mono font-bold">{activeProjects.length}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-500/10 border border-green-500/20 rounded-sm">
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="h-5 w-5 text-green-500" />
                    <span>Completed</span>
                  </div>
                  <span className="font-mono font-bold">{completedProjects.length}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-red-500/10 border border-red-500/20 rounded-sm">
                  <div className="flex items-center gap-3">
                    <AlertTriangle className="h-5 w-5 text-red-500" />
                    <span>Delayed</span>
                  </div>
                  <span className="font-mono font-bold">{delayedProjects.length}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-white/5 bg-card">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-lg font-display">Financial Summary</CardTitle>
              <Link href="/dashboard/finance">
                <Button variant="ghost" size="sm" className="text-primary" data-testid="link-finance">
                  View All <ArrowRight className="h-4 w-4 ml-1" />
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between text-sm mb-2">
                    <span className="text-muted-foreground">Budget Utilization</span>
                    <span className="font-mono">
                      {totalBudget > 0 ? Math.round((totalExpenses / totalBudget) * 100) : 0}%
                    </span>
                  </div>
                  <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full transition-all duration-500 ${
                        (totalExpenses / totalBudget) > 0.9 ? 'bg-red-500' :
                        (totalExpenses / totalBudget) > 0.7 ? 'bg-orange-500' : 'bg-primary'
                      }`}
                      style={{ width: `${Math.min((totalExpenses / totalBudget) * 100, 100)}%` }}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 pt-4">
                  <div className="p-3 bg-secondary/30 rounded-sm">
                    <div className="text-xs text-muted-foreground">Total Budget</div>
                    <div className="font-mono font-bold mt-1" data-testid="text-total-budget">
                      {formatCurrency(totalBudget)}
                    </div>
                  </div>
                  <div className="p-3 bg-secondary/30 rounded-sm">
                    <div className="text-xs text-muted-foreground">Expenses</div>
                    <div className="font-mono font-bold mt-1" data-testid="text-expenses">
                      {formatCurrency(totalExpenses)}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-8 lg:grid-cols-2">
          <Card className="border-white/5 bg-card">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-lg font-display">Recent Projects</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {projects?.slice(0, 4).map((project) => (
                  <div key={project.id} className="flex items-center justify-between pb-4 border-b border-white/5 last:border-0 last:pb-0">
                    <div>
                      <p className="font-medium text-foreground" data-testid={`project-name-${project.id}`}>
                        {project.name}
                      </p>
                      <p className="text-xs text-muted-foreground">{project.location}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="h-1.5 w-16 bg-secondary rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${
                            project.status === 'Delayed' ? 'bg-red-500' : 
                            project.status === 'Completed' ? 'bg-green-500' : 'bg-primary'
                          }`}
                          style={{ width: `${project.progress}%` }}
                        />
                      </div>
                      <span className="text-xs font-mono w-8">{project.progress}%</span>
                    </div>
                  </div>
                )) || (
                  <p className="text-muted-foreground text-center py-4">No projects yet</p>
                )}
              </div>
            </CardContent>
          </Card>

          <Card className="border-white/5 bg-card">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-lg font-display">CRM Activity</CardTitle>
              <Link href="/dashboard/crm">
                <Button variant="ghost" size="sm" className="text-primary" data-testid="link-crm">
                  View All <ArrowRight className="h-4 w-4 ml-1" />
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {clients?.slice(0, 4).map((client) => (
                  <div key={client.id} className="flex items-center justify-between pb-4 border-b border-white/5 last:border-0 last:pb-0">
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center text-xs font-bold text-primary">
                        {client.avatar || client.name.split(" ").map((n: string) => n[0]).join("").toUpperCase().slice(0, 2)}
                      </div>
                      <div>
                        <p className="font-medium text-foreground text-sm" data-testid={`client-name-${client.id}`}>
                          {client.name}
                        </p>
                        <p className="text-xs text-muted-foreground">{client.company}</p>
                      </div>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      client.status === 'Contract Signed' ? 'bg-green-500/10 text-green-500' :
                      client.status === 'Active Negotiation' ? 'bg-blue-500/10 text-blue-500' :
                      'bg-orange-500/10 text-orange-500'
                    }`}>
                      {client.status}
                    </span>
                  </div>
                )) || (
                  <p className="text-muted-foreground text-center py-4">No clients yet</p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-4 lg:grid-cols-4 mb-8">
          {/* Executive Financial Health KPIs */}
          <Card className="bg-card border-white/5 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg font-bold">Total Contract Value</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-primary">{safeFinance.total_contract_value ? formatCurrency(safeFinance.total_contract_value) : "-"}</div>
              <Link href="/dashboard/finance" className="text-xs text-primary underline">Drill Down</Link>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg font-bold">Net Cash Flow (90d)</CardTitle>
            </CardHeader>
            
            <CardContent>
              {/* Placeholder for cash flow chart */}
              <div className="h-24 flex items-center justify-center text-muted-foreground">[Chart]</div>
              <Link href="/dashboard/finance" className="text-xs text-primary underline">Drill Down</Link>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg font-bold">AR Days</CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${safeArDays.value > 45 ? 'text-red-500' : safeArDays.value > 30 ? 'text-orange-500' : 'text-green-500'}`}>{safeArDays.value ?? '-'}</div>
              <Link href="/dashboard/finance" className="text-xs text-primary underline">Drill Down</Link>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg font-bold">Profit Margin</CardTitle>
            </CardHeader>
            <CardContent>
              <ProfitMarginChart data={safeProfitMargin} />
              <Link href="/dashboard/finance" className="text-xs text-primary underline">Drill Down</Link>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-4 lg:grid-cols-4 mb-8">
          {/* Project Portfolio Health KPIs */}
          <Card className="bg-card border-white/5 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg font-bold">Projects On-Time</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-500">{safeSpiMap.on_time ?? '-'}</div>
              <Link href="/dashboard/projects?status=on-time" className="text-xs text-primary underline">Drill Down</Link>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg font-bold">Projects At-Risk</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-orange-500">{safeSpiMap.at_risk ?? '-'}</div>
              <Link href="/dashboard/projects?status=at-risk" className="text-xs text-primary underline">Drill Down</Link>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg font-bold">Projects Delayed</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-500">{safeSpiMap.delayed ?? '-'}</div>
              <Link href="/dashboard/projects?status=delayed" className="text-xs text-primary underline">Drill Down</Link>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg font-bold">Resource Utilization %</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-primary">{safeResourceUtilization.percent ?? '-'}</div>
              <Link href="/dashboard/hr" className="text-xs text-primary underline">Drill Down</Link>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-4 lg:grid-cols-3 mb-8">
          {/* Compliance & Safety KPIs */}
          <Card className="bg-card border-white/5 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg font-bold">Lost Time Incident Rate (LTIR)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${safeSafety.ltir > safeSafety.benchmark ? 'text-red-500' : 'text-green-500'}`}>{safeSafety.ltir ?? '-'}</div>
              <Link href="/dashboard/safety" className="text-xs text-primary underline">Drill Down</Link>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg font-bold">Open Safety Issues</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-orange-500">{safeSafety.open_issues ?? '-'}</div>
              <Link href="/dashboard/safety?status=open" className="text-xs text-primary underline">Drill Down</Link>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg font-bold">Rework Cost %</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-primary">{safeReworkCost.percent ?? '-'}</div>
              <Link href="/dashboard/finance?filter=rework" className="text-xs text-primary underline">Drill Down</Link>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-8 lg:grid-cols-2 mb-8">
          {/* Project Portfolio Map & Trend Chart */}
          <Card className="border-white/5 bg-card">
            <CardHeader>
              <CardTitle className="text-lg font-display">Project Portfolio Map</CardTitle>
            </CardHeader>
            <CardContent>
              {projectMap ? (
                <ProjectPortfolioMap data={safeProjectMap} />
              ) : (
                <div className="h-64 flex items-center justify-center text-muted-foreground">[Map]</div>
              )}
            </CardContent>
          </Card>
          <Card className="border-white/5 bg-card">
            <CardHeader>
              <CardTitle className="text-lg font-display">Budget vs. Actual vs. Earned Value</CardTitle>
            </CardHeader>
            <CardContent>
              {trendChart ? (
                <BudgetTrendChart data={safeTrendChart} />
              ) : (
                <div className="h-64 flex items-center justify-center text-muted-foreground">[Trend Chart]</div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
