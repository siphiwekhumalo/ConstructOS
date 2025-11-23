import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import Home from "@/pages/home";
import DashboardOverview from "@/pages/dashboard/overview";
import DashboardProjects from "@/pages/dashboard/projects";
import DashboardDocuments from "@/pages/dashboard/documents";
import DashboardFinance from "@/pages/dashboard/finance";
import DashboardEquipment from "@/pages/dashboard/equipment";
import DashboardSafety from "@/pages/dashboard/safety";
import DashboardIoT from "@/pages/dashboard/iot";
import DashboardCRM from "@/pages/dashboard/crm";
import NotFound from "@/pages/not-found";

function Router() {
  return (
    <Switch>
      <Route path="/" component={Home} />
      <Route path="/dashboard" component={DashboardOverview} />
      <Route path="/dashboard/projects" component={DashboardProjects} />
      <Route path="/dashboard/documents" component={DashboardDocuments} />
      <Route path="/dashboard/finance" component={DashboardFinance} />
      <Route path="/dashboard/equipment" component={DashboardEquipment} />
      <Route path="/dashboard/safety" component={DashboardSafety} />
      <Route path="/dashboard/iot" component={DashboardIoT} />
      <Route path="/dashboard/crm" component={DashboardCRM} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Router />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
