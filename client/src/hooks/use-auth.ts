/**
 * Authentication Hook for Azure AD / Entra ID and Session-based Auth
 * 
 * Provides authentication state, login/logout functions, and role checking.
 * Supports both Azure AD authentication and session-based demo user login.
 */

import { useState, useEffect, useCallback } from "react";
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { InteractionStatus, AccountInfo } from "@azure/msal-browser";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { isAzureADConfigured, loginRequest, type AuthState, type UserInfo } from "../lib/msal-config";
import { setAuthToken } from "../lib/api";

const API_BASE = "/api/v1";

export interface SessionUser {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: string;
  role_display: string;
  user_type: string;
  department: string;
  is_admin: boolean;
  is_executive: boolean;
  is_internal: boolean;
}

export interface SessionAuthData {
  user: SessionUser;
  permissions: Record<string, any>;
  session_token?: string;
}

async function fetchCurrentUser(): Promise<SessionAuthData | null> {
  try {
    const response = await fetch(`${API_BASE}/auth/me/`, {
      credentials: 'include',
    });
    
    if (!response.ok) {
      return null;
    }
    
    return response.json();
  } catch (error) {
    console.error('Failed to fetch current user:', error);
    return null;
  }
}

async function fetchAuthMe(accessToken?: string): Promise<AuthState> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };
  
  if (accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }
  
  const response = await fetch(`${API_BASE}/auth/me/`, { 
    headers,
    credentials: 'include',
  });
  
  if (!response.ok) {
    throw new Error("Failed to fetch auth info");
  }
  
  const data = await response.json();
  
  if (data.user) {
    return {
      authenticated: true,
      user: {
        id: data.user.id,
        username: data.user.username,
        email: data.user.email,
        firstName: data.user.first_name,
        lastName: data.user.last_name,
        fullName: data.user.full_name,
        role: data.user.role,
        roleDisplay: data.user.role_display,
        department: data.user.department,
        isActive: true,
        isAdmin: data.user.is_admin,
        isExecutive: data.user.is_executive,
        isInternal: data.user.is_internal,
      },
      roles: [data.user.role],
      azureAdRoles: [],
      permissions: Object.keys(data.permissions || {}),
    };
  }
  
  return {
    authenticated: data.authenticated || false,
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
  const [sessionUser, setSessionUser] = useState<SessionUser | null>(null);
  const [sessionPermissions, setSessionPermissions] = useState<Record<string, any>>({});
  const [isSessionAuth, setIsSessionAuth] = useState(false);
  
  const account = accounts[0] as AccountInfo | undefined;
  
  useEffect(() => {
    const checkSession = async () => {
      const data = await fetchCurrentUser();
      if (data?.user) {
        setSessionUser(data.user);
        setSessionPermissions(data.permissions || {});
        setIsSessionAuth(true);
      }
    };
    
    if (!isAzureADConfigured || !isMsalAuthenticated) {
      checkSession();
    }
  }, [isMsalAuthenticated]);
  
  const acquireToken = useCallback(async () => {
    if (!isAzureADConfigured || !account) {
      setAuthToken(null);
      return null;
    }
    
    try {
      const response = await instance.acquireTokenSilent({
        ...loginRequest,
        account,
      });
      setAccessToken(response.accessToken);
      setAuthToken(response.accessToken);
      return response.accessToken;
    } catch (error) {
      try {
        const response = await instance.acquireTokenPopup(loginRequest);
        setAccessToken(response.accessToken);
        setAuthToken(response.accessToken);
        return response.accessToken;
      } catch (popupError) {
        console.error("Failed to acquire token:", popupError);
        setAuthToken(null);
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
    queryKey: ["auth", "me", accessToken, isSessionAuth],
    queryFn: () => fetchAuthMe(accessToken || undefined),
    staleTime: 5 * 60 * 1000,
    retry: 1,
    enabled: isMsalAuthenticated || isSessionAuth,
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
  
  const loginWithCredentials = useCallback((data: SessionAuthData) => {
    setSessionUser(data.user);
    setSessionPermissions(data.permissions || {});
    setIsSessionAuth(true);
    queryClient.invalidateQueries({ queryKey: ["auth"] });
  }, [queryClient]);
  
  const logout = useCallback(async () => {
    if (isSessionAuth) {
      try {
        await fetch(`${API_BASE}/auth/logout/`, {
          method: 'POST',
          credentials: 'include',
        });
      } catch (error) {
        console.error("Logout request failed:", error);
      }
      
      setSessionUser(null);
      setSessionPermissions({});
      setIsSessionAuth(false);
      setAccessToken(null);
      setAuthToken(null);
      queryClient.clear();
      return;
    }
    
    if (!isAzureADConfigured) {
      setAccessToken(null);
      setAuthToken(null);
      queryClient.clear();
      return;
    }
    
    try {
      await instance.logoutPopup();
      setAccessToken(null);
      setAuthToken(null);
      queryClient.clear();
    } catch (error) {
      console.error("Logout failed:", error);
    }
  }, [instance, queryClient, isSessionAuth]);
  
  const currentUser = sessionUser || authState?.user;
  const currentRoles = sessionUser ? [sessionUser.role] : (authState?.roles || []);
  const currentPermissions = Object.keys(sessionPermissions).length > 0 
    ? Object.keys(sessionPermissions) 
    : (authState?.permissions || []);
  
  const hasRole = useCallback((role: string): boolean => {
    return currentRoles.includes(role);
  }, [currentRoles]);
  
  const hasAnyRole = useCallback((roles: string[]): boolean => {
    return roles.some(role => currentRoles.includes(role));
  }, [currentRoles]);
  
  const hasPermission = useCallback((permission: string): boolean => {
    if (currentPermissions.includes("all")) return true;
    return currentPermissions.includes(permission);
  }, [currentPermissions]);
  
  const isAdmin = useCallback((): boolean => {
    return hasAnyRole(["system_admin", "admin", "Administrator"]);
  }, [hasAnyRole]);
  
  const isFinance = useCallback((): boolean => {
    return hasAnyRole(["finance_manager", "finance", "Finance_User", "system_admin", "admin"]);
  }, [hasAnyRole]);
  
  const isHR = useCallback((): boolean => {
    return hasAnyRole(["hr_specialist", "hr", "HR_Manager", "system_admin", "admin"]);
  }, [hasAnyRole]);
  
  const isOperations = useCallback((): boolean => {
    return hasAnyRole(["operations_specialist", "operations", "Operations_Specialist", "system_admin", "admin"]);
  }, [hasAnyRole]);
  
  const isSiteManager = useCallback((): boolean => {
    return hasAnyRole(["site_manager", "Site_Manager", "system_admin", "admin"]);
  }, [hasAnyRole]);
  
  const isExecutive = useCallback((): boolean => {
    return hasAnyRole(["executive", "Executive", "system_admin", "admin"]);
  }, [hasAnyRole]);
  
  const isAuthenticated = isSessionAuth || (authState?.authenticated || false);
  
  return {
    isAuthenticated,
    isLoading: isLoading || inProgress !== InteractionStatus.None,
    user: currentUser || null,
    roles: currentRoles,
    permissions: currentPermissions,
    accessToken,
    error,
    
    login,
    loginWithCredentials,
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
    isSessionAuth,
  };
}

export type UseAuthReturn = ReturnType<typeof useAuth>;
