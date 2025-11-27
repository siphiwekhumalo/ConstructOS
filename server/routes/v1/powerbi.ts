import { Router } from "express";
import { powerBIService } from "../../services/powerbi";

const router = Router();

router.get("/config", async (req, res) => {
  try {
    const config = powerBIService.getConfiguration();
    res.json(config);
  } catch (error) {
    res.status(500).json({ error: "Failed to get Power BI configuration" });
  }
});

router.get("/embed-token", async (req, res) => {
  try {
    if (!powerBIService.isConfigured()) {
      return res.status(400).json({ 
        error: "Power BI is not configured. Please set the required environment variables: POWERBI_CLIENT_ID, POWERBI_CLIENT_SECRET, POWERBI_TENANT_ID, POWERBI_WORKSPACE_ID, POWERBI_REPORT_ID" 
      });
    }

    const embedConfig = await powerBIService.generateEmbedToken();
    res.json(embedConfig);
  } catch (error) {
    console.error("Power BI embed token error:", error);
    res.status(500).json({ 
      error: error instanceof Error ? error.message : "Failed to generate embed token" 
    });
  }
});

router.get("/reports", async (req, res) => {
  try {
    if (!powerBIService.isConfigured()) {
      return res.status(400).json({ error: "Power BI is not configured" });
    }

    const reports = await powerBIService.listReports();
    res.json(reports);
  } catch (error) {
    console.error("Power BI list reports error:", error);
    res.status(500).json({ 
      error: error instanceof Error ? error.message : "Failed to list reports" 
    });
  }
});

router.get("/reports/:reportId", async (req, res) => {
  try {
    if (!powerBIService.isConfigured()) {
      return res.status(400).json({ error: "Power BI is not configured" });
    }

    const report = await powerBIService.getReportDetails();
    res.json(report);
  } catch (error) {
    console.error("Power BI get report error:", error);
    res.status(500).json({ 
      error: error instanceof Error ? error.message : "Failed to get report details" 
    });
  }
});

export default router;
