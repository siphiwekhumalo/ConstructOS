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
  BarChart3,
  UserCog,
  ShoppingCart,
  Headphones,
  Star,
  Brain,
  MessageSquare,
  ChevronDown,
  User,
  Lock
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { GlobalSearch } from "@/components/global-search";
import { useFavorites } from "@/hooks/use-favorites";
import { ThemeToggle } from "@/components/theme-toggle";
import { useAuth } from "@/hooks/use-auth";
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuLabel, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { hasNavPermission, type NavPermission } from "@/lib/rbac-permissions";

const roleColors: Record<string, string> = {
  system_admin: "bg-red-500/10 text-red-500",
  finance_manager: "bg-emerald-500/10 text-emerald-500",
  sales_rep: "bg-blue-500/10 text-blue-500",
  operations_specialist: "bg-amber-500/10 text-amber-500",
  site_manager: "bg-orange-500/10 text-orange-500",
  hr_specialist: "bg-purple-500/10 text-purple-500",
  warehouse_clerk: "bg-cyan-500/10 text-cyan-500",
  field_worker: "bg-lime-500/10 text-lime-500",
  subcontractor: "bg-yellow-500/10 text-yellow-500",
  client: "bg-indigo-500/10 text-indigo-500",
  executive: "bg-pink-500/10 text-pink-500",
};

interface NavItemConfig {
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  href: string;
  permission: NavPermission;
}

const navItems: NavItemConfig[] = [
  { label: "Overview", icon: LayoutDashboard, href: "/dashboard", permission: "dashboard.overview" },
  { label: "Projects", icon: Briefcase, href: "/dashboard/projects", permission: "dashboard.projects" },
  { label: "Documents", icon: FileText, href: "/dashboard/documents", permission: "dashboard.documents" },
  { label: "Finance", icon: Wallet, href: "/dashboard/finance", permission: "dashboard.finance" },
  { label: "Equipment", icon: Truck, href: "/dashboard/equipment", permission: "dashboard.equipment" },
  { label: "Safety", icon: ShieldAlert, href: "/dashboard/safety", permission: "dashboard.safety" },
  { label: "IoT Monitor", icon: Radio, href: "/dashboard/iot", permission: "dashboard.iot" },
  { label: "CRM", icon: Users, href: "/dashboard/crm", permission: "dashboard.crm" },
  { label: "Orders", icon: ShoppingCart, href: "/dashboard/orders", permission: "dashboard.orders" },
  { label: "HR", icon: UserCog, href: "/dashboard/hr", permission: "dashboard.hr" },
  { label: "Support", icon: Headphones, href: "/dashboard/support", permission: "dashboard.support" },
  { label: "Reports", icon: BarChart3, href: "/dashboard/reports", permission: "dashboard.reports" },
  { label: "AI Insights", icon: Brain, href: "/dashboard/ai", permission: "dashboard.ai" },
  { label: "Team Chat", icon: MessageSquare, href: "/dashboard/chat", permission: "dashboard.chat" },
];

interface NavItemProps {
  item: NavItemConfig;
  isActive: boolean;
  hasAccess: boolean;
  userRole?: string;
}

function NavItemComponent({ item, isActive, hasAccess, userRole }: NavItemProps) {
  const content = (
    <div 
      className={cn(
        "flex items-center gap-3 px-4 py-2.5 rounded-sm text-sm font-medium transition-all group relative",
        hasAccess ? "cursor-pointer" : "cursor-not-allowed",
        isActive && hasAccess
          ? "bg-primary/10 text-primary border-l-2 border-primary" 
          : hasAccess
            ? "text-muted-foreground hover:bg-secondary hover:text-foreground"
            : "text-muted-foreground/40 bg-muted/20"
      )}
      data-testid={`nav-item-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
    >
      <item.icon 
        className={cn(
          "h-4 w-4", 
          isActive && hasAccess 
            ? "text-primary" 
            : hasAccess 
              ? "text-muted-foreground group-hover:text-foreground"
              : "text-muted-foreground/40"
        )} 
      />
      <span className={cn(
        hasAccess ? "" : "opacity-50"
      )}>
        {item.label}
      </span>
      {!hasAccess && (
        <Lock className="h-3 w-3 ml-auto text-muted-foreground/40" />
      )}
    </div>
  );

  if (!hasAccess) {
    return (
      <TooltipProvider delayDuration={300}>
        <Tooltip>
          <TooltipTrigger asChild>
            <div>{content}</div>
          </TooltipTrigger>
          <TooltipContent side="right" className="max-w-[200px]">
            <p className="text-xs">
              You don't have access to this feature. Contact your administrator if you need access.
            </p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return (
    <Link href={item.href}>
      {content}
    </Link>
  );
}

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [location, navigate] = useLocation();
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout, isLoading } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const getInitials = (u: typeof user) => {
    if (!u) return 'U';
    const firstName = 'first_name' in u ? u.first_name : u.firstName;
    const lastName = 'last_name' in u ? u.last_name : u.lastName;
    if (firstName && lastName) {
      return `${firstName[0]}${lastName[0]}`.toUpperCase();
    }
    return (u.username?.[0] || 'U').toUpperCase();
  };
  
  const getFullName = (u: typeof user): string => {
    if (!u) return 'Guest';
    if ('full_name' in u && u.full_name) return u.full_name;
    if ('fullName' in u && u.fullName) return u.fullName;
    return u.username || 'Guest';
  };
  
  const getRoleDisplay = (u: typeof user): string => {
    if (!u || !u.role) return '';
    if ('role_display' in u && u.role_display) return String(u.role_display);
    if ('roleDisplay' in u && u.roleDisplay) return String(u.roleDisplay);
    return u.role.replace(/_/g, ' ');
  };

  const userRole = user?.role;

  const accessibleCount = navItems.filter(item => hasNavPermission(userRole, item.permission)).length;
  const totalCount = navItems.length;

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
        "fixed md:sticky top-0 left-0 h-screen w-64 bg-card border-r border-border z-50 transition-transform duration-300 ease-in-out",
        isSidebarOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
      )}>
        <div className="h-16 flex items-center px-6 border-b border-border">
          <div className="h-5 w-5 bg-primary rounded-sm mr-3" />
          <span className="font-display font-bold text-lg tracking-tight">ConstructOS</span>
        </div>

        <div className="p-4 space-y-1 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 180px)' }}>
          {userRole && (
            <div className="px-4 py-2 mb-2">
              <div className="text-[10px] uppercase tracking-wider text-muted-foreground/60 font-medium">
                Access Level
              </div>
              <div className="text-xs text-muted-foreground mt-0.5">
                {accessibleCount} of {totalCount} features
              </div>
            </div>
          )}
          
          {navItems.map((item) => {
            const isActive = location === item.href || 
              (item.href !== '/dashboard' && location.startsWith(item.href));
            const hasAccess = hasNavPermission(userRole, item.permission);
            
            return (
              <NavItemComponent
                key={item.href}
                item={item}
                isActive={isActive}
                hasAccess={hasAccess}
                userRole={userRole}
              />
            );
          })}
        </div>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-border bg-card">
          <Link href="/settings">
             <div className="flex items-center gap-3 px-4 py-2.5 rounded-sm text-sm font-medium text-muted-foreground hover:bg-secondary hover:text-foreground cursor-pointer mb-1">
               <Settings className="h-4 w-4" />
               Settings
             </div>
          </Link>
          <div 
            onClick={handleLogout}
            className="flex items-center gap-3 px-4 py-2.5 rounded-sm text-sm font-medium text-destructive hover:bg-destructive/10 cursor-pointer transition-colors"
            data-testid="button-sidebar-logout"
          >
            <LogOut className="h-4 w-4" />
            Sign Out
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <header className="h-16 border-b border-border flex items-center justify-between px-6 sticky top-0 bg-background/80 backdrop-blur-md z-30">
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

          <div className="flex-1 max-w-xl mx-4 hidden md:block">
            <GlobalSearch />
          </div>

          <div className="flex items-center gap-2">
            <ThemeToggle />
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button 
                  variant="ghost" 
                  className="flex items-center gap-3 pl-4 border-l border-border h-auto py-2 hover:bg-secondary/50"
                  data-testid="button-user-menu"
                >
                  <div className="text-right hidden sm:block">
                    <div className="text-sm font-medium" data-testid="text-user-name">
                      {getFullName(user)}
                    </div>
                    <div className="text-xs text-muted-foreground" data-testid="text-user-email">
                      {user?.email || 'Not logged in'}
                    </div>
                  </div>
                  <div className="h-9 w-9 rounded bg-secondary border border-border flex items-center justify-center">
                    <span className="font-mono font-bold text-xs" data-testid="text-user-initials">
                      {getInitials(user)}
                    </span>
                  </div>
                  <ChevronDown className="h-4 w-4 text-muted-foreground hidden sm:block" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-64">
                <DropdownMenuLabel>
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium">{getFullName(user)}</p>
                    <p className="text-xs text-muted-foreground">{user?.email}</p>
                    {user?.role && (
                      <Badge 
                        variant="secondary" 
                        className={cn("w-fit mt-1 text-xs", roleColors[user.role] || "")}
                        data-testid="badge-user-role"
                      >
                        {getRoleDisplay(user)}
                      </Badge>
                    )}
                    {userRole && (
                      <p className="text-[10px] text-muted-foreground mt-1">
                        Access: {accessibleCount}/{totalCount} features
                      </p>
                    )}
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link href="/dashboard/profile" className="cursor-pointer">
                    <User className="mr-2 h-4 w-4" />
                    Profile
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/settings" className="cursor-pointer">
                    <Settings className="mr-2 h-4 w-4" />
                    Settings
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem 
                  onClick={handleLogout}
                  className="text-destructive focus:text-destructive cursor-pointer"
                  data-testid="button-logout"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Sign Out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        <div className="p-6 md:p-8 max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}
