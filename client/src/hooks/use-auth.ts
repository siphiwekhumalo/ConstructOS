/**
 * Authentication Hook for Azure AD / Entra ID
 * 
 * Provides authentication state, login/logout functions, and role checking.
 */

import { useState, useEffect, useCallback } from "react";
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { InteractionStatus, AccountInfo } from "@azure/msal-browser";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { isAzureADConfigured, loginRequest, type AuthState, type UserInfo } from "../lib/msal-config";

const API_BASE = "/api/v1";

async function fetchAuthMe(accessToken?: string): Promise<AuthState> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };
  
  if (accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }
  
  const response = await fetch(`${API_BASE}/auth/me/`, { headers });
  
  if (!response.ok) {
    throw new Error("Failed to fetch auth info");
  }
  
  const data = await response.json();
  
  return {
    authenticated: data.authenticated,
    user: data.user ? {
      id: data.user.id,
      username: data.user.username,
      email: data.user.email,
      firstName: data.user.first_name,
      lastName: data.user.last_name,
      fullName: data.user.full_name,
      role: data.user.role,
      department: data.user.department,
      isActive: data.user.is_active,
    } : null,
    roles: data.roles || [],
    azureAdRoles: data.azure_ad_roles || [],
    permissions: data.permissions || [],
  };
}

export function useAuth() {
  const { instance, accounts, inProgress } = useMsal();
  const isMsalAuthenticated = useIsAuthenticated();
  const queryClient = useQueryClient();
  const [accessToken, setAccessToken] = useState<string | null>(null);
  
  const account = accounts[0] as AccountInfo | undefined;
  
  const acquireToken = useCallback(async () => {
    if (!isAzureADConfigured || !account) {
      return null;
    }
    
    try {
      const response = await instance.acquireTokenSilent({
        ...loginRequest,
        account,
      });
      setAccessToken(response.accessToken);
      return response.accessToken;
    } catch (error) {
      try {
        const response = await instance.acquireTokenPopup(loginRequest);
        setAccessToken(response.accessToken);
        return response.accessToken;
      } catch (popupError) {
        console.error("Failed to acquire token:", popupError);
        return null;
      }
    }
  }, [instance, account]);
  
  useEffect(() => {
    if (isAzureADConfigured && isMsalAuthenticated && account) {
      acquireToken();
    }
  }, [isMsalAuthenticated, account, acquireToken]);
  
  const {
    data: authState,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["auth", "me", accessToken],
    queryFn: () => fetchAuthMe(accessToken || undefined),
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });
  
  const login = useCallback(async () => {
    if (!isAzureADConfigured) {
      console.warn("Azure AD not configured. Set VITE_AZURE_AD_CLIENT_ID and VITE_AZURE_AD_TENANT_ID.");
      return;
    }
    
    try {
      await instance.loginPopup(loginRequest);
      await refetch();
    } catch (error) {
      console.error("Login failed:", error);
    }
  }, [instance, refetch]);
  
  const logout = useCallback(async () => {
    if (!isAzureADConfigured) {
      setAccessToken(null);
      queryClient.clear();
      return;
    }
    
    try {
      await instance.logoutPopup();
      setAccessToken(null);
      queryClient.clear();
    } catch (error) {
      console.error("Logout failed:", error);
    }
  }, [instance, queryClient]);
  
  const hasRole = useCallback((role: string): boolean => {
    if (!authState?.authenticated) return false;
    return authState.roles.includes(role);
  }, [authState]);
  
  const hasAnyRole = useCallback((roles: string[]): boolean => {
    if (!authState?.authenticated) return false;
    return roles.some(role => authState.roles.includes(role));
  }, [authState]);
  
  const hasPermission = useCallback((permission: string): boolean => {
    if (!authState?.authenticated) return false;
    if (authState.permissions.includes("all")) return true;
    return authState.permissions.includes(permission);
  }, [authState]);
  
  const isAdmin = useCallback((): boolean => {
    return hasAnyRole(["admin", "Administrator"]);
  }, [hasAnyRole]);
  
  const isFinance = useCallback((): boolean => {
    return hasAnyRole(["finance", "Finance_User", "admin"]);
  }, [hasAnyRole]);
  
  const isHR = useCallback((): boolean => {
    return hasAnyRole(["hr", "HR_Manager", "admin"]);
  }, [hasAnyRole]);
  
  const isOperations = useCallback((): boolean => {
    return hasAnyRole(["operations", "Operations_Specialist", "admin"]);
  }, [hasAnyRole]);
  
  const isSiteManager = useCallback((): boolean => {
    return hasAnyRole(["site_manager", "Site_Manager", "admin"]);
  }, [hasAnyRole]);
  
  const isExecutive = useCallback((): boolean => {
    return hasAnyRole(["executive", "Executive", "admin"]);
  }, [hasAnyRole]);
  
  return {
    isAuthenticated: authState?.authenticated || false,
    isLoading: isLoading || inProgress !== InteractionStatus.None,
    user: authState?.user || null,
    roles: authState?.roles || [],
    permissions: authState?.permissions || [],
    accessToken,
    error,
    
    login,
    logout,
    acquireToken,
    refetch,
    
    hasRole,
    hasAnyRole,
    hasPermission,
    
    isAdmin,
    isFinance,
    isHR,
    isOperations,
    isSiteManager,
    isExecutive,
    
    isAzureADConfigured,
  };
}

export type UseAuthReturn = ReturnType<typeof useAuth>;
