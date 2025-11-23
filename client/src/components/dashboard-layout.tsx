import { Link, useLocation } from "wouter";
import { 
  LayoutDashboard, 
  Briefcase, 
  FileText, 
  Wallet, 
  Truck, 
  ShieldAlert, 
  Radio, 
  Users, 
  Settings, 
  LogOut,
  Menu,
  BarChart3
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useState } from "react";

const navItems = [
  { label: "Overview", icon: LayoutDashboard, href: "/dashboard" },
  { label: "Projects", icon: Briefcase, href: "/dashboard/projects" },
  { label: "Documents", icon: FileText, href: "/dashboard/documents" },
  { label: "Finance", icon: Wallet, href: "/dashboard/finance" },
  { label: "Equipment", icon: Truck, href: "/dashboard/equipment" },
  { label: "Safety", icon: ShieldAlert, href: "/dashboard/safety" },
  { label: "IoT Monitor", icon: Radio, href: "/dashboard/iot" },
  { label: "CRM", icon: Users, href: "/dashboard/crm" },
  { label: "Reports & Analytics", icon: BarChart3, href: "/dashboard/reports" },
];

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();
  const [isSidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background flex">
      {/* Mobile Sidebar Overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={cn(
        "fixed md:sticky top-0 left-0 h-screen w-64 bg-card border-r border-white/5 z-50 transition-transform duration-300 ease-in-out",
        isSidebarOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
      )}>
        <div className="h-16 flex items-center px-6 border-b border-white/5">
          <div className="h-5 w-5 bg-primary rounded-sm mr-3" />
          <span className="font-display font-bold text-lg tracking-tight">ConstructOS</span>
        </div>

        <div className="p-4 space-y-1">
          {navItems.map((item) => {
            const isActive = location === item.href;
            return (
              <Link key={item.href} href={item.href}>
                <div className={cn(
                  "flex items-center gap-3 px-4 py-2.5 rounded-sm text-sm font-medium transition-all cursor-pointer group",
                  isActive 
                    ? "bg-primary/10 text-primary border-l-2 border-primary" 
                    : "text-muted-foreground hover:bg-white/5 hover:text-foreground"
                )}>
                  <item.icon className={cn("h-4 w-4", isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground")} />
                  {item.label}
                </div>
              </Link>
            );
          })}
        </div>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-white/5">
          <Link href="/settings">
             <div className="flex items-center gap-3 px-4 py-2.5 rounded-sm text-sm font-medium text-muted-foreground hover:bg-white/5 hover:text-foreground cursor-pointer mb-1">
               <Settings className="h-4 w-4" />
               Settings
             </div>
          </Link>
          <Link href="/">
             <div className="flex items-center gap-3 px-4 py-2.5 rounded-sm text-sm font-medium text-destructive hover:bg-destructive/10 cursor-pointer">
               <LogOut className="h-4 w-4" />
               Sign Out
             </div>
          </Link>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <header className="h-16 border-b border-white/5 flex items-center justify-between px-6 sticky top-0 bg-background/80 backdrop-blur-md z-30">
          <div className="flex items-center gap-4">
             <Button 
               variant="ghost" 
               size="icon" 
               className="md:hidden"
               onClick={() => setSidebarOpen(!isSidebarOpen)}
             >
               <Menu className="h-5 w-5" />
             </Button>
             <div className="hidden md:flex items-center gap-2 text-sm text-muted-foreground">
               <span className="opacity-50">Dashboard</span>
               <span>/</span>
               <span className="text-foreground font-medium capitalize">
                 {location.split('/').pop() || 'Overview'}
               </span>
             </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3 pl-4 border-l border-white/5">
              <div className="text-right hidden sm:block">
                <div className="text-sm font-medium">Site Manager</div>
                <div className="text-xs text-muted-foreground">admin@constructos.com</div>
              </div>
              <div className="h-9 w-9 rounded bg-secondary border border-white/10 flex items-center justify-center">
                <span className="font-mono font-bold text-xs">SM</span>
              </div>
            </div>
          </div>
        </header>

        <div className="p-6 md:p-8 max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}
