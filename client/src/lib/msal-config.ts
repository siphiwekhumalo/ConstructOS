/**
 * Microsoft Authentication Library (MSAL) Configuration
 * 
 * Configure Azure AD / Entra ID authentication for ConstructOS.
 * Required environment variables:
 * - VITE_AZURE_AD_CLIENT_ID: The Application (client) ID from Azure portal
 * - VITE_AZURE_AD_TENANT_ID: The Directory (tenant) ID from Azure portal
 */

import { Configuration, LogLevel, PublicClientApplication } from "@azure/msal-browser";

const clientId = import.meta.env.VITE_AZURE_AD_CLIENT_ID || "";
const tenantId = import.meta.env.VITE_AZURE_AD_TENANT_ID || "";

export const isAzureADConfigured = !!(clientId && tenantId);

export const msalConfig: Configuration = {
  auth: {
    clientId,
    authority: `https://login.microsoftonline.com/${tenantId}`,
    redirectUri: window.location.origin,
    postLogoutRedirectUri: window.location.origin,
    navigateToLoginRequestUrl: true,
  },
  cache: {
    cacheLocation: "sessionStorage",
    storeAuthStateInCookie: false,
  },
  system: {
    loggerOptions: {
      loggerCallback: (level, message, containsPii) => {
        if (containsPii) return;
        switch (level) {
          case LogLevel.Error:
            console.error(message);
            break;
          case LogLevel.Warning:
            console.warn(message);
            break;
          case LogLevel.Info:
            if (import.meta.env.DEV) console.info(message);
            break;
        }
      },
      piiLoggingEnabled: false,
      logLevel: import.meta.env.DEV ? LogLevel.Warning : LogLevel.Error,
    },
  },
};

export const loginRequest = {
  scopes: [`api://${clientId}/access_as_user`],
};

export const graphScopes = {
  scopes: ["User.Read"],
};

export const apiScopes = {
  scopes: [`api://${clientId}/access_as_user`],
};

let msalInstance: PublicClientApplication | null = null;

export function getMsalInstance(): PublicClientApplication | null {
  if (!isAzureADConfigured) {
    return null;
  }
  
  if (!msalInstance) {
    msalInstance = new PublicClientApplication(msalConfig);
  }
  
  return msalInstance;
}

export async function initializeMsal(): Promise<PublicClientApplication | null> {
  const instance = getMsalInstance();
  if (instance) {
    await instance.initialize();
    await instance.handleRedirectPromise();
  }
  return instance;
}

export interface UserInfo {
  id: string;
  username: string;
  email: string;
  firstName: string | null;
  lastName: string | null;
  fullName: string;
  role: string;
  department: string | null;
  isActive: boolean;
}

export interface AuthState {
  authenticated: boolean;
  user: UserInfo | null;
  roles: string[];
  azureAdRoles: string[];
  permissions: string[];
}
