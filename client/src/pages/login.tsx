/**
 * Login Page
 * 
 * Provides login options:
 * 1. Microsoft Entra ID (Azure AD) for production
 * 2. Demo user quick login for testing/development
 */

import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { Building2, Shield, Users, BarChart3, User, ChevronRight, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";

interface DemoUser {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  role: string;
  role_display: string;
  user_type: string;
  department: string;
}

const ROLE_COLORS: Record<string, string> = {
  system_admin: 'bg-red-500',
  finance_manager: 'bg-green-500',
  sales_rep: 'bg-blue-500',
  operations_specialist: 'bg-orange-500',
  site_manager: 'bg-yellow-500',
  hr_specialist: 'bg-purple-500',
  warehouse_clerk: 'bg-cyan-500',
  field_worker: 'bg-gray-500',
  subcontractor: 'bg-pink-500',
  client: 'bg-indigo-500',
  executive: 'bg-amber-500',
};

const ROLE_DESCRIPTIONS: Record<string, string> = {
  system_admin: 'Full system access and configuration',
  finance_manager: 'Financial data, auditing, and payments',
  sales_rep: 'CRM, leads, and client relationships',
  operations_specialist: 'Inventory, logistics, and procurement',
  site_manager: 'Project execution and safety compliance',
  hr_specialist: 'Employee records and payroll',
  warehouse_clerk: 'Inventory at assigned locations',
  field_worker: 'Own timecard and assigned tasks',
  subcontractor: 'Own purchase orders and invoices',
  client: 'Own project data and progress',
  executive: 'Read-only global access for oversight',
};

export default function LoginPage() {
  const [, setLocation] = useLocation();
  const { isAuthenticated, isLoading, login, loginWithCredentials, isAzureADConfigured } = useAuth();
  const { toast } = useToast();
  
  const [demoUsers, setDemoUsers] = useState<DemoUser[]>([]);
  const [loadingDemoUsers, setLoadingDemoUsers] = useState(true);
  const [loggingIn, setLoggingIn] = useState(false);
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  
  useEffect(() => {
    if (isAuthenticated) {
      setLocation("/dashboard");
    }
  }, [isAuthenticated, setLocation]);
  
  useEffect(() => {
    fetchDemoUsers();
  }, []);
  
  const fetchDemoUsers = async () => {
    try {
      const response = await fetch('/api/v1/auth/demo-users/');
      if (response.ok) {
        const data = await response.json();
        setDemoUsers(data.demo_users || []);
      }
    } catch (error) {
      console.error('Failed to fetch demo users:', error);
    } finally {
      setLoadingDemoUsers(false);
    }
  };
  
  const handleQuickLogin = async (role: string) => {
    setLoggingIn(true);
    setSelectedRole(role);
    
    try {
      const response = await fetch('/api/v1/auth/quick-login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role }),
      });
      
      if (response.ok) {
        const data = await response.json();
        if (loginWithCredentials) {
          loginWithCredentials(data);
        }
        toast({
          title: "Login successful",
          description: `Logged in as ${data.user.full_name} (${data.user.role_display})`,
        });
        setLocation("/dashboard");
      } else {
        const error = await response.json();
        toast({
          title: "Login failed",
          description: error.error || 'An error occurred',
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Login failed",
        description: 'Network error. Please try again.',
        variant: "destructive",
      });
    } finally {
      setLoggingIn(false);
      setSelectedRole(null);
    }
  };
  
  const handleCredentialLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoggingIn(true);
    
    try {
      const response = await fetch('/api/v1/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      
      if (response.ok) {
        const data = await response.json();
        if (loginWithCredentials) {
          loginWithCredentials(data);
        }
        toast({
          title: "Login successful",
          description: `Welcome back, ${data.user.full_name}!`,
        });
        setLocation("/dashboard");
      } else {
        const error = await response.json();
        toast({
          title: "Login failed",
          description: error.error || 'Invalid credentials',
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Login failed",
        description: 'Network error. Please try again.',
        variant: "destructive",
      });
    } finally {
      setLoggingIn(false);
    }
  };
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  const features = [
    {
      icon: Building2,
      title: "Project Management",
      description: "Track construction projects, milestones, and budgets",
    },
    {
      icon: Shield,
      title: "Safety Compliance",
      description: "Manage safety inspections and compliance documentation",
    },
    {
      icon: Users,
      title: "CRM & HR",
      description: "Customer relationships, employee management, and payroll",
    },
    {
      icon: BarChart3,
      title: "Analytics",
      description: "Real-time dashboards and performance reporting",
    },
  ];
  
  const internalUsers = demoUsers.filter(u => u.user_type === 'internal');
  const externalUsers = demoUsers.filter(u => u.user_type === 'external');
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted" data-testid="login-page">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-8">
            <div className="flex items-center justify-center gap-3 mb-4">
              <Building2 className="h-12 w-12 text-primary" />
              <h1 className="text-4xl font-bold">ConstructOS</h1>
            </div>
            <p className="text-xl text-muted-foreground">
              Construction Management Platform
            </p>
          </div>
          
          <Card className="mb-8">
            <CardHeader className="text-center pb-2">
              <CardTitle>Sign In</CardTitle>
              <CardDescription>
                Choose a login method below
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="demo" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="demo" data-testid="tab-demo-login">
                    Demo Users
                  </TabsTrigger>
                  <TabsTrigger value="credentials" data-testid="tab-credentials-login">
                    {isAzureADConfigured ? "Microsoft / Password" : "Password"}
                  </TabsTrigger>
                </TabsList>
                
                <TabsContent value="demo" className="mt-4">
                  <div className="space-y-4">
                    <p className="text-sm text-muted-foreground text-center">
                      Click on a user to instantly log in and explore their access level
                    </p>
                    
                    {loadingDemoUsers ? (
                      <div className="flex justify-center py-8">
                        <Loader2 className="h-6 w-6 animate-spin" />
                      </div>
                    ) : (
                      <div className="space-y-4">
                        <div>
                          <h3 className="text-sm font-semibold mb-2 text-muted-foreground">
                            Internal Staff
                          </h3>
                          <ScrollArea className="h-[280px]">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                              {internalUsers.map((user) => (
                                <Button
                                  key={user.username}
                                  variant="outline"
                                  className="h-auto p-3 justify-start text-left"
                                  onClick={() => handleQuickLogin(user.role)}
                                  disabled={loggingIn}
                                  data-testid={`button-login-${user.role}`}
                                >
                                  <div className="flex items-center gap-3 w-full">
                                    <div className={`w-10 h-10 rounded-full ${ROLE_COLORS[user.role]} flex items-center justify-center text-white font-semibold text-sm`}>
                                      {user.first_name[0]}{user.last_name[0]}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                      <div className="font-medium truncate">
                                        {user.first_name} {user.last_name}
                                      </div>
                                      <div className="text-xs text-muted-foreground truncate">
                                        {user.role_display}
                                      </div>
                                    </div>
                                    {loggingIn && selectedRole === user.role ? (
                                      <Loader2 className="h-4 w-4 animate-spin" />
                                    ) : (
                                      <ChevronRight className="h-4 w-4 text-muted-foreground" />
                                    )}
                                  </div>
                                </Button>
                              ))}
                            </div>
                          </ScrollArea>
                        </div>
                        
                        <div>
                          <h3 className="text-sm font-semibold mb-2 text-muted-foreground">
                            External Users
                          </h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                            {externalUsers.map((user) => (
                              <Button
                                key={user.username}
                                variant="outline"
                                className="h-auto p-3 justify-start text-left"
                                onClick={() => handleQuickLogin(user.role)}
                                disabled={loggingIn}
                                data-testid={`button-login-${user.role}`}
                              >
                                <div className="flex items-center gap-3 w-full">
                                  <div className={`w-10 h-10 rounded-full ${ROLE_COLORS[user.role]} flex items-center justify-center text-white font-semibold text-sm`}>
                                    {user.first_name[0]}{user.last_name[0]}
                                  </div>
                                  <div className="flex-1 min-w-0">
                                    <div className="font-medium truncate">
                                      {user.first_name} {user.last_name}
                                    </div>
                                    <div className="text-xs text-muted-foreground truncate">
                                      {user.role_display}
                                    </div>
                                  </div>
                                  {loggingIn && selectedRole === user.role ? (
                                    <Loader2 className="h-4 w-4 animate-spin" />
                                  ) : (
                                    <ChevronRight className="h-4 w-4 text-muted-foreground" />
                                  )}
                                </div>
                              </Button>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </TabsContent>
                
                <TabsContent value="credentials" className="mt-4">
                  <div className="space-y-4 max-w-sm mx-auto">
                    {isAzureADConfigured && (
                      <>
                        <Button
                          size="lg"
                          onClick={login}
                          className="w-full gap-2"
                          data-testid="button-login-microsoft"
                        >
                          <svg className="h-5 w-5" viewBox="0 0 21 21" fill="currentColor">
                            <rect x="1" y="1" width="9" height="9" />
                            <rect x="11" y="1" width="9" height="9" />
                            <rect x="1" y="11" width="9" height="9" />
                            <rect x="11" y="11" width="9" height="9" />
                          </svg>
                          Sign in with Microsoft
                        </Button>
                        
                        <div className="relative">
                          <div className="absolute inset-0 flex items-center">
                            <span className="w-full border-t" />
                          </div>
                          <div className="relative flex justify-center text-xs uppercase">
                            <span className="bg-background px-2 text-muted-foreground">
                              Or continue with password
                            </span>
                          </div>
                        </div>
                      </>
                    )}
                    
                    <form onSubmit={handleCredentialLogin} className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="username">Username or Email</Label>
                        <Input
                          id="username"
                          type="text"
                          value={username}
                          onChange={(e) => setUsername(e.target.value)}
                          placeholder="Enter username or email"
                          required
                          data-testid="input-username"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="password">Password</Label>
                        <Input
                          id="password"
                          type="password"
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          placeholder="Enter password"
                          required
                          data-testid="input-password"
                        />
                      </div>
                      <Button
                        type="submit"
                        className="w-full"
                        disabled={loggingIn}
                        data-testid="button-login-submit"
                      >
                        {loggingIn ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Signing in...
                          </>
                        ) : (
                          'Sign In'
                        )}
                      </Button>
                    </form>
                    
                    <p className="text-xs text-center text-muted-foreground">
                      Demo password for all users: <code className="bg-muted px-1 rounded">demo123</code>
                    </p>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {features.map((feature) => (
              <Card key={feature.title} className="bg-card/50">
                <CardContent className="flex items-start gap-4 p-4">
                  <feature.icon className="h-8 w-8 text-primary shrink-0 mt-1" />
                  <div>
                    <h3 className="font-semibold">{feature.title}</h3>
                    <p className="text-sm text-muted-foreground">{feature.description}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          
          <Card className="bg-card/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Role-Based Access Control (RBAC)</CardTitle>
              <CardDescription>
                Each role has specific permissions based on the principle of least privilege
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                {Object.entries(ROLE_DESCRIPTIONS).map(([role, description]) => (
                  <div key={role} className="flex items-start gap-2 p-2 rounded-lg hover:bg-muted/50">
                    <Badge className={`${ROLE_COLORS[role]} text-white text-xs shrink-0`}>
                      {role.replace(/_/g, ' ')}
                    </Badge>
                    <span className="text-xs text-muted-foreground">{description}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
