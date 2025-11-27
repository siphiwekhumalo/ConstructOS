import type { Express, Request, Response, NextFunction } from "express";
import { createServer, type Server } from "http";
import { createProxyMiddleware } from "http-proxy-middleware";
import { WebSocketServer, WebSocket } from "ws";

const DJANGO_BACKEND_URL = process.env.DJANGO_BACKEND_URL || "http://127.0.0.1:8000";
const DAPHNE_WS_URL = process.env.DAPHNE_WS_URL || "ws://127.0.0.1:8001";

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

  const wss = new WebSocketServer({ 
    server: httpServer,
    path: '/ws'
  });

  wss.on('connection', (clientWs, req) => {
    const url = req.url || '';
    const targetUrl = `${DAPHNE_WS_URL}${url.replace(/^\/ws/, '/ws')}`;
    
    console.log(`[WebSocket] Client connecting to ${targetUrl}`);
    
    let backendWs: WebSocket | null = null;
    
    try {
      backendWs = new WebSocket(targetUrl);
      
      backendWs.on('open', () => {
        console.log('[WebSocket] Connected to Daphne backend');
      });
      
      backendWs.on('message', (data) => {
        if (clientWs.readyState === WebSocket.OPEN) {
          clientWs.send(data.toString());
        }
      });
      
      backendWs.on('close', (code, reason) => {
        console.log(`[WebSocket] Backend closed: ${code} ${reason}`);
        if (clientWs.readyState === WebSocket.OPEN) {
          clientWs.close(code, reason.toString());
        }
      });
      
      backendWs.on('error', (err) => {
        console.error('[WebSocket] Backend error:', err.message);
        if (clientWs.readyState === WebSocket.OPEN) {
          clientWs.close(1011, 'Backend connection error');
        }
      });
      
      clientWs.on('message', (data) => {
        if (backendWs && backendWs.readyState === WebSocket.OPEN) {
          backendWs.send(data.toString());
        }
      });
      
      clientWs.on('close', (code, reason) => {
        console.log(`[WebSocket] Client closed: ${code}`);
        if (backendWs && backendWs.readyState === WebSocket.OPEN) {
          backendWs.close(code, reason.toString());
        }
      });
      
      clientWs.on('error', (err) => {
        console.error('[WebSocket] Client error:', err.message);
        if (backendWs && backendWs.readyState === WebSocket.OPEN) {
          backendWs.close(1011, 'Client connection error');
        }
      });
      
    } catch (err) {
      console.error('[WebSocket] Failed to connect to backend:', err);
      clientWs.close(1011, 'Failed to connect to backend');
    }
  });

  console.log('[WebSocket] WebSocket proxy ready on /ws path');

  return httpServer;
}
