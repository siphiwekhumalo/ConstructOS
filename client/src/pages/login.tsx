/**
 * Login Page
 * 
 * Allows users to sign in with Microsoft Entra ID (Azure AD).
 */

import { useEffect } from "react";
import { useLocation } from "wouter";
import { Building2, Shield, Users, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/use-auth";

export default function LoginPage() {
  const [, setLocation] = useLocation();
  const { isAuthenticated, isLoading, login, isAzureADConfigured } = useAuth();
  
  useEffect(() => {
    if (isAuthenticated) {
      setLocation("/dashboard");
    }
  }, [isAuthenticated, setLocation]);
  
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
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted" data-testid="login-page">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <div className="flex items-center justify-center gap-3 mb-4">
              <Building2 className="h-12 w-12 text-primary" />
              <h1 className="text-4xl font-bold">ConstructOS</h1>
            </div>
            <p className="text-xl text-muted-foreground">
              Construction Management Platform
            </p>
          </div>
          
          <Card className="mb-8">
            <CardHeader className="text-center">
              <CardTitle>Sign In</CardTitle>
              <CardDescription>
                {isAzureADConfigured
                  ? "Sign in with your organization's Microsoft account"
                  : "Azure AD authentication is not configured. Contact your administrator."}
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col items-center gap-4">
              {isAzureADConfigured ? (
                <Button
                  size="lg"
                  onClick={login}
                  className="gap-2"
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
              ) : (
                <div className="text-center">
                  <p className="text-sm text-muted-foreground mb-4">
                    To enable Azure AD authentication, set the following environment variables:
                  </p>
                  <code className="block bg-muted p-3 rounded text-xs mb-2">
                    VITE_AZURE_AD_CLIENT_ID=your-client-id
                  </code>
                  <code className="block bg-muted p-3 rounded text-xs">
                    VITE_AZURE_AD_TENANT_ID=your-tenant-id
                  </code>
                  <Button
                    variant="outline"
                    className="mt-4"
                    onClick={() => setLocation("/dashboard")}
                    data-testid="button-continue-without-auth"
                  >
                    Continue without authentication (Demo Mode)
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
          
          <div className="mt-8 text-center">
            <h2 className="text-lg font-semibold mb-2">Role-Based Access Control</h2>
            <p className="text-sm text-muted-foreground max-w-2xl mx-auto">
              ConstructOS uses Microsoft Entra ID for secure authentication with role-based access.
              Your access level (Finance, HR, Operations, or Site Manager) determines which features
              you can use.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
