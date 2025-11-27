/**
 * Route Guard Component
 * 
 * Protects routes based on authentication status and user roles.
 */

import { type ReactNode } from "react";
import { useAuth } from "../hooks/use-auth";
import { Redirect } from "wouter";

interface RouteGuardProps {
  children: ReactNode;
  requireAuth?: boolean;
  allowedRoles?: string[];
  fallback?: ReactNode;
  redirectTo?: string;
}

export function RouteGuard({
  children,
  requireAuth = false,
  allowedRoles,
  fallback,
  redirectTo = "/login",
}: RouteGuardProps) {
  const { isAuthenticated, isLoading, hasAnyRole, isAzureADConfigured } = useAuth();
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[200px]" data-testid="route-guard-loading">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  if (!isAzureADConfigured) {
    return <>{children}</>;
  }
  
  if (requireAuth && !isAuthenticated) {
    if (fallback) {
      return <>{fallback}</>;
    }
    return <Redirect to={redirectTo} />;
  }
  
  if (allowedRoles && allowedRoles.length > 0) {
    if (!isAuthenticated) {
      if (fallback) {
        return <>{fallback}</>;
      }
      return <Redirect to={redirectTo} />;
    }
    
    if (!hasAnyRole(allowedRoles)) {
      return (
        <div className="flex flex-col items-center justify-center min-h-[200px] p-4" data-testid="access-denied">
          <h2 className="text-xl font-semibold text-destructive mb-2">Access Denied</h2>
          <p className="text-muted-foreground text-center">
            You don't have permission to access this page.
          </p>
          <p className="text-sm text-muted-foreground mt-2">
            Required roles: {allowedRoles.join(", ")}
          </p>
        </div>
      );
    }
  }
  
  return <>{children}</>;
}

export function FinanceRoute({ children }: { children: ReactNode }) {
  return (
    <RouteGuard allowedRoles={["finance", "Finance_User", "admin", "Administrator", "executive"]}>
      {children}
    </RouteGuard>
  );
}

export function HRRoute({ children }: { children: ReactNode }) {
  return (
    <RouteGuard allowedRoles={["hr", "HR_Manager", "admin", "Administrator", "executive"]}>
      {children}
    </RouteGuard>
  );
}

export function OperationsRoute({ children }: { children: ReactNode }) {
  return (
    <RouteGuard allowedRoles={["operations", "Operations_Specialist", "admin", "Administrator", "executive"]}>
      {children}
    </RouteGuard>
  );
}

export function SiteManagerRoute({ children }: { children: ReactNode }) {
  return (
    <RouteGuard allowedRoles={["site_manager", "Site_Manager", "operations", "admin", "Administrator", "executive"]}>
      {children}
    </RouteGuard>
  );
}

export function AdminRoute({ children }: { children: ReactNode }) {
  return (
    <RouteGuard allowedRoles={["admin", "Administrator"]}>
      {children}
    </RouteGuard>
  );
}
