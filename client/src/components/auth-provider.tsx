/**
 * Authentication Provider Component
 * 
 * Wraps the application with MSAL provider for Azure AD authentication.
 * Also provides an AuthContext for components that need auth state.
 */

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { MsalProvider } from "@azure/msal-react";
import { PublicClientApplication } from "@azure/msal-browser";
import { initializeMsal, isAzureADConfigured } from "../lib/msal-config";

interface AuthProviderProps {
  children: ReactNode;
}

const MsalInstanceContext = createContext<PublicClientApplication | null>(null);

export function useMsalInstance() {
  return useContext(MsalInstanceContext);
}

function MsalWrapper({ children, instance }: { children: ReactNode; instance: PublicClientApplication }) {
  return (
    <MsalProvider instance={instance}>
      <MsalInstanceContext.Provider value={instance}>
        {children}
      </MsalInstanceContext.Provider>
    </MsalProvider>
  );
}

function NoAuthWrapper({ children }: { children: ReactNode }) {
  return (
    <MsalInstanceContext.Provider value={null}>
      {children}
    </MsalInstanceContext.Provider>
  );
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [msalInstance, setMsalInstance] = useState<PublicClientApplication | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  
  useEffect(() => {
    async function initialize() {
      if (!isAzureADConfigured) {
        setIsInitialized(true);
        return;
      }
      
      try {
        const instance = await initializeMsal();
        setMsalInstance(instance);
        setIsInitialized(true);
      } catch (err) {
        console.error("Failed to initialize MSAL:", err);
        setError(err instanceof Error ? err : new Error("Failed to initialize authentication"));
        setIsInitialized(true);
      }
    }
    
    initialize();
  }, []);
  
  if (!isInitialized) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-4">
        <div className="text-destructive mb-4">Authentication initialization failed</div>
        <p className="text-muted-foreground text-sm">{error.message}</p>
      </div>
    );
  }
  
  if (!isAzureADConfigured || !msalInstance) {
    return <NoAuthWrapper>{children}</NoAuthWrapper>;
  }
  
  return <MsalWrapper instance={msalInstance}>{children}</MsalWrapper>;
}
