import { z } from "zod";

const powerBIConfigSchema = z.object({
  clientId: z.string().min(1, "Client ID is required"),
  clientSecret: z.string().min(1, "Client Secret is required"),
  tenantId: z.string().min(1, "Tenant ID is required"),
  workspaceId: z.string().min(1, "Workspace ID is required"),
  reportId: z.string().min(1, "Report ID is required"),
});

export type PowerBIConfig = z.infer<typeof powerBIConfigSchema>;

interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

interface EmbedTokenResponse {
  token: string;
  tokenId: string;
  expiration: string;
}

interface EmbedConfig {
  embedUrl: string;
  embedToken: string;
  reportId: string;
  workspaceId: string;
  expiration: string;
}

export class PowerBIService {
  private config: PowerBIConfig;
  private cachedAccessToken: string | null = null;
  private tokenExpiry: Date | null = null;

  constructor() {
    const config = {
      clientId: process.env.POWERBI_CLIENT_ID || "",
      clientSecret: process.env.POWERBI_CLIENT_SECRET || "",
      tenantId: process.env.POWERBI_TENANT_ID || "",
      workspaceId: process.env.POWERBI_WORKSPACE_ID || "",
      reportId: process.env.POWERBI_REPORT_ID || "",
    };

    this.config = config;
  }

  isConfigured(): boolean {
    return !!(
      this.config.clientId &&
      this.config.clientSecret &&
      this.config.tenantId &&
      this.config.workspaceId &&
      this.config.reportId
    );
  }

  getConfiguration(): { configured: boolean; workspaceId?: string; reportId?: string } {
    if (!this.isConfigured()) {
      return { configured: false };
    }
    return {
      configured: true,
      workspaceId: this.config.workspaceId,
      reportId: this.config.reportId,
    };
  }

  private async getAzureADToken(): Promise<string> {
    if (this.cachedAccessToken && this.tokenExpiry && new Date() < this.tokenExpiry) {
      return this.cachedAccessToken;
    }

    const tokenUrl = `https://login.microsoftonline.com/${this.config.tenantId}/oauth2/v2.0/token`;

    const params = new URLSearchParams({
      grant_type: "client_credentials",
      client_id: this.config.clientId,
      client_secret: this.config.clientSecret,
      scope: "https://analysis.windows.net/powerbi/api/.default",
    });

    const response = await fetch(tokenUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: params.toString(),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to obtain Azure AD token: ${response.status} - ${errorText}`);
    }

    const data: TokenResponse = await response.json();
    
    this.cachedAccessToken = data.access_token;
    this.tokenExpiry = new Date(Date.now() + (data.expires_in - 60) * 1000);

    return data.access_token;
  }

  async generateEmbedToken(): Promise<EmbedConfig> {
    if (!this.isConfigured()) {
      throw new Error("Power BI is not configured. Please set the required environment variables.");
    }

    const accessToken = await this.getAzureADToken();

    const embedTokenUrl = `https://api.powerbi.com/v1.0/myorg/groups/${this.config.workspaceId}/reports/${this.config.reportId}/GenerateToken`;

    const response = await fetch(embedTokenUrl, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        accessLevel: "View",
        allowSaveAs: false,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to generate embed token: ${response.status} - ${errorText}`);
    }

    const embedTokenData: EmbedTokenResponse = await response.json();

    const embedUrl = `https://app.powerbi.com/reportEmbed?reportId=${this.config.reportId}&groupId=${this.config.workspaceId}`;

    return {
      embedUrl,
      embedToken: embedTokenData.token,
      reportId: this.config.reportId,
      workspaceId: this.config.workspaceId,
      expiration: embedTokenData.expiration,
    };
  }

  async getReportDetails(): Promise<any> {
    if (!this.isConfigured()) {
      throw new Error("Power BI is not configured.");
    }

    const accessToken = await this.getAzureADToken();

    const reportUrl = `https://api.powerbi.com/v1.0/myorg/groups/${this.config.workspaceId}/reports/${this.config.reportId}`;

    const response = await fetch(reportUrl, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${accessToken}`,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to get report details: ${response.status} - ${errorText}`);
    }

    return await response.json();
  }

  async listReports(): Promise<any[]> {
    if (!this.isConfigured()) {
      throw new Error("Power BI is not configured.");
    }

    const accessToken = await this.getAzureADToken();

    const reportsUrl = `https://api.powerbi.com/v1.0/myorg/groups/${this.config.workspaceId}/reports`;

    const response = await fetch(reportsUrl, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${accessToken}`,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to list reports: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    return data.value || [];
  }
}

export const powerBIService = new PowerBIService();
