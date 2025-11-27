import type { Express, Request, Response, NextFunction } from "express";
import { createServer, type Server } from "http";
import { createProxyMiddleware } from "http-proxy-middleware";

const DJANGO_BACKEND_URL = process.env.DJANGO_BACKEND_URL || "http://127.0.0.1:8000";

interface RequestLog {
  method: string;
  path: string;
  statusCode: number;
  duration: number;
  timestamp: string;
}

const requestLogger = (req: Request, res: Response, next: NextFunction) => {
  const start = Date.now();
  const timestamp = new Date().toISOString();

  res.on("finish", () => {
    const log: RequestLog = {
      method: req.method,
      path: req.path,
      statusCode: res.statusCode,
      duration: Date.now() - start,
      timestamp,
    };
    
    if (req.path.startsWith("/api")) {
      console.log(`[API Proxy] ${log.method} ${log.path} ${log.statusCode} ${log.duration}ms`);
    }
  });

  next();
};

export async function registerRoutes(app: Express): Promise<Server> {
  app.use(requestLogger);

  app.get("/health", (req, res) => {
    res.json({ status: "healthy", service: "ConstructOS Gateway" });
  });

  const apiProxy = createProxyMiddleware({
    target: DJANGO_BACKEND_URL,
    changeOrigin: true,
    pathRewrite: (_path, req) => {
      return req.originalUrl || _path;
    },
    on: {
      error: (err, req, res) => {
        console.error('[API Proxy Error]', err.message);
        const serverRes = res as Response;
        if (!serverRes.headersSent) {
          serverRes.status(502).json({ 
            error: "Backend service unavailable",
            detail: "Django backend is not responding. Make sure it's running on port 8000."
          });
        }
      }
    }
  });

  app.use("/api", apiProxy);

  const httpServer = createServer(app);
  return httpServer;
}
