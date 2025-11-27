import { DashboardLayout } from "@/components/dashboard-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { 
  Brain, 
  TrendingUp, 
  AlertTriangle, 
  Target, 
  Wrench, 
  Package, 
  Banknote,
  Activity,
  RefreshCw,
  CheckCircle2,
  Clock,
  Zap
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import {
  getAIHealth,
  getCreditRiskPrediction,
  getLeadScore,
  getProjectDelayPrediction,
  getMaintenanceRiskPrediction,
  getDemandForecast,
  getCashFlowForecast,
  getAccounts,
  getLeads,
  getProjects,
  getEquipment,
  getProducts,
} from "@/lib/api";
import { format } from "date-fns";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from "recharts";
import { formatCurrency, formatCurrencyCompact } from "@/lib/currency";

function RiskBadge({ level }: { level: string }) {
  const colors: Record<string, string> = {
    low: "bg-green-500/10 text-green-500 border-green-500/20",
    medium: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
    high: "bg-orange-500/10 text-orange-500 border-orange-500/20",
    critical: "bg-red-500/10 text-red-500 border-red-500/20",
  };
  return (
    <span className={`px-2 py-1 rounded text-xs font-medium border ${colors[level] || colors.medium}`}>
      {level.toUpperCase()}
    </span>
  );
}

function PriorityBadge({ priority }: { priority: string }) {
  const colors: Record<string, string> = {
    hot: "bg-red-500/10 text-red-500 border-red-500/20",
    warm: "bg-orange-500/10 text-orange-500 border-orange-500/20",
    qualified: "bg-blue-500/10 text-blue-500 border-blue-500/20",
    cold: "bg-gray-500/10 text-gray-500 border-gray-500/20",
  };
  return (
    <span className={`px-2 py-1 rounded text-xs font-medium border ${colors[priority] || colors.qualified}`}>
      {priority.toUpperCase()}
    </span>
  );
}

function ModelCard({ 
  name, 
  accuracy, 
  version, 
  icon: Icon 
}: { 
  name: string; 
  accuracy: number; 
  version: string;
  icon: React.ElementType;
}) {
  return (
    <div className="flex items-center gap-3 p-3 bg-secondary/30 rounded-sm border border-white/5">
      <div className="h-10 w-10 rounded bg-primary/10 flex items-center justify-center">
        <Icon className="h-5 w-5 text-primary" />
      </div>
      <div className="flex-1">
        <div className="text-sm font-medium">{name}</div>
        <div className="text-xs text-muted-foreground">v{version}</div>
      </div>
      <div className="text-right">
        <div className="text-sm font-mono font-bold text-primary">{(accuracy * 100).toFixed(0)}%</div>
        <div className="text-xs text-muted-foreground">accuracy</div>
      </div>
    </div>
  );
}

export default function DashboardAI() {
  const [selectedCustomer, setSelectedCustomer] = useState<string>("");
  const [selectedLead, setSelectedLead] = useState<string>("");
  const [selectedProject, setSelectedProject] = useState<string>("");
  const [selectedEquipment, setSelectedEquipment] = useState<string>("");
  const [selectedProduct, setSelectedProduct] = useState<string>("");

  const { data: aiHealth, isLoading: healthLoading, refetch: refetchHealth } = useQuery({
    queryKey: ["ai-health"],
    queryFn: getAIHealth,
  });

  const { data: accounts } = useQuery({ queryKey: ["accounts"], queryFn: getAccounts });
  const { data: leads } = useQuery({ queryKey: ["leads"], queryFn: getLeads });
  const { data: projects } = useQuery({ queryKey: ["projects"], queryFn: getProjects });
  const { data: equipment } = useQuery({ queryKey: ["equipment"], queryFn: getEquipment });
  const { data: products } = useQuery({ queryKey: ["products"], queryFn: getProducts });

  const { data: creditRisk, isLoading: creditLoading, refetch: refetchCredit, error: creditError } = useQuery({
    queryKey: ["credit-risk", selectedCustomer],
    queryFn: () => getCreditRiskPrediction(selectedCustomer),
    enabled: Boolean(selectedCustomer),
  });

  const { data: leadScore, isLoading: leadLoading, refetch: refetchLead, error: leadError } = useQuery({
    queryKey: ["lead-score", selectedLead],
    queryFn: () => getLeadScore(selectedLead),
    enabled: Boolean(selectedLead),
  });

  const { data: projectDelay, isLoading: projectLoading, refetch: refetchProject, error: projectError } = useQuery({
    queryKey: ["project-delay", selectedProject],
    queryFn: () => getProjectDelayPrediction(selectedProject),
    enabled: Boolean(selectedProject),
  });

  const { data: maintenanceRisk, isLoading: maintenanceLoading, refetch: refetchMaintenance, error: maintenanceError } = useQuery({
    queryKey: ["maintenance-risk", selectedEquipment],
    queryFn: () => getMaintenanceRiskPrediction(selectedEquipment),
    enabled: Boolean(selectedEquipment),
  });

  const { data: demandForecast, isLoading: demandLoading, refetch: refetchDemand, error: demandError } = useQuery({
    queryKey: ["demand-forecast", selectedProduct],
    queryFn: () => getDemandForecast(selectedProduct),
    enabled: Boolean(selectedProduct),
  });

  const { data: cashFlow, isLoading: cashFlowLoading, refetch: refetchCashFlow, error: cashFlowError } = useQuery({
    queryKey: ["cashflow-forecast"],
    queryFn: () => getCashFlowForecast(30),
  });

  const modelCount = Object.keys(aiHealth?.models || {}).length;
  const avgAccuracy = modelCount > 0
    ? (Object.values(aiHealth?.models || {}).reduce((sum, m) => sum + m.accuracy, 0) / modelCount * 100).toFixed(0)
    : "0";

  const modelIcons: Record<string, React.ElementType> = {
    credit_risk: DollarSign,
    cashflow: TrendingUp,
    lead_scoring: Target,
    project_delay: Clock,
    maintenance: Wrench,
    demand_forecast: Package,
  };

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground" data-testid="text-page-title">
              AI Predictions Dashboard
            </h1>
            <p className="text-muted-foreground mt-1">
              Machine learning insights for smarter decisions across finance, sales, operations, and maintenance.
            </p>
          </div>
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              className="gap-2 border-white/10" 
              onClick={() => refetchHealth()}
              data-testid="button-refresh-models"
            >
              <RefreshCw className="h-4 w-4" /> Refresh Models
            </Button>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card className="bg-card border-white/5">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">AI Status</CardTitle>
              <Brain className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                {aiHealth?.status === "healthy" ? (
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                ) : (
                  <AlertTriangle className="h-5 w-5 text-yellow-500" />
                )}
                <span className="text-2xl font-bold font-display capitalize">
                  {healthLoading ? "Loading..." : aiHealth?.status || "Unknown"}
                </span>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {Object.keys(aiHealth?.models || {}).length} models active
              </p>
            </CardContent>
          </Card>

          <Card className="bg-card border-white/5">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Avg Accuracy</CardTitle>
              <Activity className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold font-display">
                {avgAccuracy}%
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {modelCount > 0 ? `across ${modelCount} prediction models` : "no models online"}
              </p>
            </CardContent>
          </Card>

          <Card className="bg-card border-white/5">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Cash Flow Forecast</CardTitle>
              <TrendingUp className="h-4 w-4 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold font-display text-green-500">
                +${((cashFlow?.summary?.net_cash_flow || 0) / 1000).toFixed(0)}K
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                predicted 30-day net flow
              </p>
            </CardContent>
          </Card>

          <Card className="bg-card border-white/5">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Credit Risk</CardTitle>
              <Zap className="h-4 w-4 text-orange-500" />
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold font-display">
                  {creditRisk?.risk_score?.toFixed(0) || "--"}
                </span>
                {creditRisk && <RiskBadge level={creditRisk.risk_level} />}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {creditRisk ? "current risk score" : "select a customer to analyze"}
              </p>
            </CardContent>
          </Card>
        </div>

        <Card className="border-white/5 bg-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-primary" />
              Active ML Models
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
              {aiHealth?.models && Object.entries(aiHealth.models).map(([key, model]) => (
                <ModelCard
                  key={key}
                  name={model.model_name}
                  accuracy={model.accuracy}
                  version={model.model_version}
                  icon={modelIcons[key] || Brain}
                />
              ))}
            </div>
          </CardContent>
        </Card>

        <Tabs defaultValue="credit-risk" className="space-y-6">
          <TabsList className="bg-secondary/50 border border-white/5">
            <TabsTrigger value="credit-risk" className="data-[state=active]:bg-primary/20" data-testid="tab-credit-risk">
              Credit Risk
            </TabsTrigger>
            <TabsTrigger value="lead-scoring" className="data-[state=active]:bg-primary/20" data-testid="tab-lead-scoring">
              Lead Scoring
            </TabsTrigger>
            <TabsTrigger value="project-delay" className="data-[state=active]:bg-primary/20" data-testid="tab-project-delay">
              Project Delay
            </TabsTrigger>
            <TabsTrigger value="maintenance" className="data-[state=active]:bg-primary/20" data-testid="tab-maintenance">
              Maintenance
            </TabsTrigger>
            <TabsTrigger value="demand" className="data-[state=active]:bg-primary/20" data-testid="tab-demand">
              Demand Forecast
            </TabsTrigger>
            <TabsTrigger value="cashflow" className="data-[state=active]:bg-primary/20" data-testid="tab-cashflow">
              Cash Flow
            </TabsTrigger>
          </TabsList>

          <TabsContent value="credit-risk" className="space-y-6">
            <div className="grid gap-6 lg:grid-cols-2">
              <Card className="border-white/5 bg-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <DollarSign className="h-5 w-5 text-primary" />
                    Credit Risk Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Select Customer</Label>
                    <div className="flex gap-2">
                      <select
                        className="flex-1 bg-background border border-white/10 rounded-sm px-3 py-2 text-sm"
                        value={selectedCustomer}
                        onChange={(e) => setSelectedCustomer(e.target.value)}
                        data-testid="select-customer"
                      >
                        <option value="">-- Select a Customer --</option>
                        {accounts?.map((acc) => (
                          <option key={acc.id} value={acc.id}>{acc.name}</option>
                        ))}
                      </select>
                      <Button onClick={() => refetchCredit()} disabled={creditLoading || !selectedCustomer} data-testid="button-predict-credit">
                        {creditLoading ? "Analyzing..." : "Predict"}
                      </Button>
                    </div>
                  </div>

                  {creditRisk && (
                    <div className="space-y-4 pt-4 border-t border-white/5">
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Risk Score</span>
                        <div className="flex items-center gap-2">
                          <span className="text-2xl font-mono font-bold">{creditRisk.risk_score.toFixed(1)}</span>
                          <RiskBadge level={creditRisk.risk_level} />
                        </div>
                      </div>
                      <Progress value={creditRisk.risk_score} className="h-2" />
                      <div className="grid grid-cols-2 gap-4">
                        <div className="p-3 bg-secondary/30 rounded-sm">
                          <div className="text-xs text-muted-foreground">Confidence</div>
                          <div className="font-mono font-bold">{(creditRisk.confidence * 100).toFixed(0)}%</div>
                        </div>
                        <div className="p-3 bg-secondary/30 rounded-sm">
                          <div className="text-xs text-muted-foreground">Recommended Terms</div>
                          <div className="font-mono font-bold">{creditRisk.recommended_payment_terms.replace('_', ' ')}</div>
                        </div>
                      </div>
                      <div className="p-3 bg-secondary/30 rounded-sm">
                        <div className="text-xs text-muted-foreground">Recommended Credit Limit</div>
                        <div className="font-mono font-bold text-lg">${creditRisk.recommended_credit_limit.toLocaleString()}</div>
                      </div>
                      {creditRisk.factors.length > 0 && (
                        <div className="space-y-2">
                          <div className="text-sm font-medium">Risk Factors</div>
                          {creditRisk.factors.map((factor, i) => (
                            <div key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
                              <AlertTriangle className="h-4 w-4 text-orange-500" />
                              {factor}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card className="border-white/5 bg-card">
                <CardHeader>
                  <CardTitle>Model Information</CardTitle>
                </CardHeader>
                <CardContent>
                  {creditRisk?.model_info && (
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="p-3 bg-secondary/30 rounded-sm">
                          <div className="text-xs text-muted-foreground">Model Name</div>
                          <div className="font-medium">{creditRisk.model_info.model_name}</div>
                        </div>
                        <div className="p-3 bg-secondary/30 rounded-sm">
                          <div className="text-xs text-muted-foreground">Version</div>
                          <div className="font-mono">{creditRisk.model_info.model_version}</div>
                        </div>
                        <div className="p-3 bg-secondary/30 rounded-sm">
                          <div className="text-xs text-muted-foreground">Accuracy</div>
                          <div className="font-mono text-green-500">{(creditRisk.model_info.accuracy * 100).toFixed(0)}%</div>
                        </div>
                        <div className="p-3 bg-secondary/30 rounded-sm">
                          <div className="text-xs text-muted-foreground">Predicted At</div>
                          <div className="font-mono text-xs">{format(new Date(creditRisk.predicted_at), 'HH:mm:ss')}</div>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="lead-scoring" className="space-y-6">
            <div className="grid gap-6 lg:grid-cols-2">
              <Card className="border-white/5 bg-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5 text-primary" />
                    Lead Scoring
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Select Lead</Label>
                    <div className="flex gap-2">
                      <select
                        className="flex-1 bg-background border border-white/10 rounded-sm px-3 py-2 text-sm"
                        value={selectedLead}
                        onChange={(e) => setSelectedLead(e.target.value)}
                        data-testid="select-lead"
                      >
                        <option value="">-- Select a Lead --</option>
                        {leads?.map((lead) => (
                          <option key={lead.id} value={lead.id}>{lead.company || lead.firstName}</option>
                        ))}
                      </select>
                      <Button onClick={() => refetchLead()} disabled={leadLoading || !selectedLead} data-testid="button-predict-lead">
                        {leadLoading ? "Scoring..." : "Score"}
                      </Button>
                    </div>
                  </div>

                  {leadScore && (
                    <div className="space-y-4 pt-4 border-t border-white/5">
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Lead Score</span>
                        <div className="flex items-center gap-2">
                          <span className="text-3xl font-mono font-bold">{leadScore.score}</span>
                          <PriorityBadge priority={leadScore.priority} />
                        </div>
                      </div>
                      <Progress value={leadScore.score} className="h-2" />
                      <div className="grid grid-cols-2 gap-4">
                        <div className="p-3 bg-secondary/30 rounded-sm">
                          <div className="text-xs text-muted-foreground">Conversion Probability</div>
                          <div className="font-mono font-bold text-lg">{(leadScore.conversion_probability * 100).toFixed(0)}%</div>
                        </div>
                        <div className="p-3 bg-secondary/30 rounded-sm">
                          <div className="text-xs text-muted-foreground">Priority</div>
                          <div className="font-mono font-bold capitalize">{leadScore.priority}</div>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card className="border-white/5 bg-card">
                <CardHeader>
                  <CardTitle>Recommended Actions</CardTitle>
                </CardHeader>
                <CardContent>
                  {leadScore?.recommended_actions && leadScore.recommended_actions.length > 0 ? (
                    <div className="space-y-2">
                      {leadScore.recommended_actions.map((action, i) => (
                        <div key={i} className="flex items-center gap-2 p-2 bg-secondary/30 rounded-sm">
                          <CheckCircle2 className="h-4 w-4 text-primary" />
                          <span className="text-sm">{action}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-muted-foreground text-center py-4">
                      No specific recommendations for this lead
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="project-delay" className="space-y-6">
            <div className="grid gap-6 lg:grid-cols-2">
              <Card className="border-white/5 bg-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="h-5 w-5 text-primary" />
                    Project Delay Prediction
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Select Project</Label>
                    <div className="flex gap-2">
                      <select
                        className="flex-1 bg-background border border-white/10 rounded-sm px-3 py-2 text-sm"
                        value={selectedProject}
                        onChange={(e) => setSelectedProject(e.target.value)}
                        data-testid="select-project"
                      >
                        <option value="">-- Select a Project --</option>
                        {projects?.map((proj) => (
                          <option key={proj.id} value={proj.id}>{proj.name}</option>
                        ))}
                      </select>
                      <Button onClick={() => refetchProject()} disabled={projectLoading || !selectedProject} data-testid="button-predict-project">
                        {projectLoading ? "Predicting..." : "Predict"}
                      </Button>
                    </div>
                  </div>

                  {projectDelay && (
                    <div className="space-y-4 pt-4 border-t border-white/5">
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Delay Probability</span>
                        <div className="flex items-center gap-2">
                          <span className="text-2xl font-mono font-bold">{(projectDelay.delay_probability * 100).toFixed(0)}%</span>
                          <RiskBadge level={projectDelay.risk_level} />
                        </div>
                      </div>
                      <Progress value={projectDelay.delay_probability * 100} className="h-2" />
                      <div className="p-4 bg-secondary/30 rounded-sm text-center">
                        <div className="text-xs text-muted-foreground">Expected Delay</div>
                        <div className="text-3xl font-mono font-bold mt-1">{projectDelay.expected_delay_days} days</div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card className="border-white/5 bg-card">
                <CardHeader>
                  <CardTitle>Risk Factors & Mitigations</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {projectDelay?.risk_factors && projectDelay.risk_factors.length > 0 && (
                    <div className="space-y-2">
                      <div className="text-sm font-medium text-orange-500">Risk Factors</div>
                      {projectDelay.risk_factors.map((factor, i) => (
                        <div key={i} className="flex items-center gap-2 text-sm p-2 bg-orange-500/10 rounded-sm">
                          <AlertTriangle className="h-4 w-4 text-orange-500" />
                          {factor}
                        </div>
                      ))}
                    </div>
                  )}
                  {projectDelay?.mitigation_suggestions && projectDelay.mitigation_suggestions.length > 0 && (
                    <div className="space-y-2">
                      <div className="text-sm font-medium text-green-500">Mitigation Suggestions</div>
                      {projectDelay.mitigation_suggestions.map((sug, i) => (
                        <div key={i} className="flex items-center gap-2 text-sm p-2 bg-green-500/10 rounded-sm">
                          <CheckCircle2 className="h-4 w-4 text-green-500" />
                          {sug}
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="maintenance" className="space-y-6">
            <div className="grid gap-6 lg:grid-cols-2">
              <Card className="border-white/5 bg-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Wrench className="h-5 w-5 text-primary" />
                    Predictive Maintenance
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Select Equipment</Label>
                    <div className="flex gap-2">
                      <select
                        className="flex-1 bg-background border border-white/10 rounded-sm px-3 py-2 text-sm"
                        value={selectedEquipment}
                        onChange={(e) => setSelectedEquipment(e.target.value)}
                        data-testid="select-equipment"
                      >
                        <option value="">-- Select Equipment --</option>
                        {equipment?.map((eq) => (
                          <option key={eq.id} value={eq.id}>{eq.name}</option>
                        ))}
                      </select>
                      <Button onClick={() => refetchMaintenance()} disabled={maintenanceLoading || !selectedEquipment} data-testid="button-predict-maintenance">
                        {maintenanceLoading ? "Analyzing..." : "Analyze"}
                      </Button>
                    </div>
                  </div>

                  {maintenanceRisk && (
                    <div className="space-y-4 pt-4 border-t border-white/5">
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Failure Probability</span>
                        <div className="flex items-center gap-2">
                          <span className="text-2xl font-mono font-bold">{(maintenanceRisk.failure_probability * 100).toFixed(1)}%</span>
                          <RiskBadge level={maintenanceRisk.risk_level} />
                        </div>
                      </div>
                      <Progress value={maintenanceRisk.failure_probability * 100} className="h-2" />
                      <div className="grid grid-cols-2 gap-4">
                        <div className="p-3 bg-secondary/30 rounded-sm">
                          <div className="text-xs text-muted-foreground">Remaining Life</div>
                          <div className="font-mono font-bold">{maintenanceRisk.estimated_remaining_life_days} days</div>
                        </div>
                        <div className="p-3 bg-secondary/30 rounded-sm">
                          <div className="text-xs text-muted-foreground">Est. Downtime</div>
                          <div className="font-mono font-bold">{maintenanceRisk.estimated_downtime_hours}h</div>
                        </div>
                      </div>
                      <div className="p-3 bg-primary/10 rounded-sm border border-primary/20">
                        <div className="text-xs text-muted-foreground">Recommended Maintenance</div>
                        <div className="font-medium">{maintenanceRisk.maintenance_type}</div>
                        <div className="text-sm text-primary mt-1">
                          Schedule by: {format(new Date(maintenanceRisk.recommended_maintenance_date), 'MMM dd, yyyy')}
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card className="border-white/5 bg-card">
                <CardHeader>
                  <CardTitle>Parts & Preparation</CardTitle>
                </CardHeader>
                <CardContent>
                  {maintenanceRisk?.parts_needed && maintenanceRisk.parts_needed.length > 0 ? (
                    <div className="space-y-2">
                      <div className="text-sm font-medium">Required Parts</div>
                      {maintenanceRisk.parts_needed.map((part, i) => (
                        <div key={i} className="flex items-center gap-2 p-2 bg-secondary/30 rounded-sm">
                          <Package className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">{part}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-muted-foreground text-center py-4">
                      No special parts required for this maintenance
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="demand" className="space-y-6">
            <div className="grid gap-6 lg:grid-cols-3">
              <Card className="border-white/5 bg-card lg:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Package className="h-5 w-5 text-primary" />
                    Demand Forecast
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Select Product</Label>
                    <div className="flex gap-2">
                      <select
                        className="flex-1 bg-background border border-white/10 rounded-sm px-3 py-2 text-sm"
                        value={selectedProduct}
                        onChange={(e) => setSelectedProduct(e.target.value)}
                        data-testid="select-product"
                      >
                        <option value="">-- Select a Product --</option>
                        {products?.map((prod) => (
                          <option key={prod.id} value={prod.id}>{prod.name}</option>
                        ))}
                      </select>
                      <Button onClick={() => refetchDemand()} disabled={demandLoading || !selectedProduct} data-testid="button-predict-demand">
                        {demandLoading ? "Forecasting..." : "Forecast"}
                      </Button>
                    </div>
                  </div>

                  {demandForecast?.forecast && (
                    <div className="h-64 mt-4">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={demandForecast.forecast.slice(0, 14)}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                          <XAxis 
                            dataKey="date" 
                            tickFormatter={(date) => format(new Date(date), 'MM/dd')}
                            stroke="#666"
                          />
                          <YAxis stroke="#666" />
                          <Tooltip 
                            contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
                            labelFormatter={(date) => format(new Date(date), 'MMM dd, yyyy')}
                          />
                          <Area 
                            type="monotone" 
                            dataKey="confidence_upper" 
                            stackId="1"
                            stroke="transparent"
                            fill="#3b82f6"
                            fillOpacity={0.1}
                          />
                          <Area 
                            type="monotone" 
                            dataKey="predicted_demand" 
                            stackId="2"
                            stroke="#3b82f6" 
                            fill="#3b82f6"
                            fillOpacity={0.3}
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card className="border-white/5 bg-card">
                <CardHeader>
                  <CardTitle>Inventory Recommendations</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {demandForecast && (
                    <>
                      <div className="p-3 bg-secondary/30 rounded-sm">
                        <div className="text-xs text-muted-foreground">Current Stock</div>
                        <div className="font-mono font-bold text-lg">{demandForecast.current_stock}</div>
                      </div>
                      <div className="p-3 bg-secondary/30 rounded-sm">
                        <div className="text-xs text-muted-foreground">Reorder Point</div>
                        <div className="font-mono font-bold text-lg">{demandForecast.reorder_point}</div>
                      </div>
                      <div className="p-3 bg-primary/10 rounded-sm border border-primary/20">
                        <div className="text-xs text-muted-foreground">Suggested Order Qty</div>
                        <div className="font-mono font-bold text-2xl text-primary">{demandForecast.suggested_order_quantity}</div>
                      </div>
                      {demandForecast.stockout_risk_date && (
                        <div className="p-3 bg-red-500/10 rounded-sm border border-red-500/20">
                          <div className="text-xs text-red-400">Stockout Risk Date</div>
                          <div className="font-mono font-bold text-red-500">
                            {format(new Date(demandForecast.stockout_risk_date), 'MMM dd, yyyy')}
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="cashflow" className="space-y-6">
            <Card className="border-white/5 bg-card">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-primary" />
                  30-Day Cash Flow Forecast
                </CardTitle>
                <Button onClick={() => refetchCashFlow()} disabled={cashFlowLoading} variant="outline" className="gap-2">
                  <RefreshCw className="h-4 w-4" />
                  Refresh
                </Button>
              </CardHeader>
              <CardContent>
                {cashFlow?.forecast && (
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={cashFlow.forecast.slice(0, 14)}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                        <XAxis 
                          dataKey="date" 
                          tickFormatter={(date) => format(new Date(date), 'MM/dd')}
                          stroke="#666"
                        />
                        <YAxis 
                          stroke="#666"
                          tickFormatter={(val) => formatCurrencyCompact(val)}
                        />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
                          labelFormatter={(date) => format(new Date(date), 'MMM dd, yyyy')}
                          formatter={(value: number) => [formatCurrency(value), '']}
                        />
                        <Line 
                          type="monotone" 
                          dataKey="predicted_inflow" 
                          stroke="#22c55e" 
                          name="Inflow"
                          strokeWidth={2}
                        />
                        <Line 
                          type="monotone" 
                          dataKey="predicted_outflow" 
                          stroke="#ef4444" 
                          name="Outflow"
                          strokeWidth={2}
                        />
                        <Line 
                          type="monotone" 
                          dataKey="net_cash_flow" 
                          stroke="#3b82f6" 
                          name="Net"
                          strokeWidth={2}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </CardContent>
            </Card>

            {cashFlow?.summary && (
              <div className="grid gap-4 md:grid-cols-4">
                <Card className="bg-card border-white/5">
                  <CardContent className="pt-6">
                    <div className="text-sm text-muted-foreground">Total Predicted Inflow</div>
                    <div className="text-2xl font-bold font-display text-green-500">
                      {formatCurrencyCompact(cashFlow.summary.total_predicted_inflow)}
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-card border-white/5">
                  <CardContent className="pt-6">
                    <div className="text-sm text-muted-foreground">Total Predicted Outflow</div>
                    <div className="text-2xl font-bold font-display text-red-500">
                      {formatCurrencyCompact(cashFlow.summary.total_predicted_outflow)}
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-card border-white/5">
                  <CardContent className="pt-6">
                    <div className="text-sm text-muted-foreground">Net Cash Flow</div>
                    <div className="text-2xl font-bold font-display text-blue-500">
                      +{formatCurrencyCompact(cashFlow.summary.net_cash_flow)}
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-card border-white/5">
                  <CardContent className="pt-6">
                    <div className="text-sm text-muted-foreground">Avg Daily Balance</div>
                    <div className="text-2xl font-bold font-display">
                      {formatCurrencyCompact(cashFlow.summary.average_daily_balance)}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
