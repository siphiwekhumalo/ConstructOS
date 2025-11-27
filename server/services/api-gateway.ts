import { Request, Response, NextFunction } from "express";

interface RateLimitConfig {
  windowMs: number;
  maxRequests: number;
}

interface RateLimitEntry {
  count: number;
  resetAt: number;
}

interface RequestLog {
  id: string;
  timestamp: Date;
  method: string;
  path: string;
  statusCode: number;
  responseTimeMs: number;
  ip?: string;
  userId?: string;
  userAgent?: string;
}

const rateLimitStore = new Map<string, RateLimitEntry>();
const requestLogs: RequestLog[] = [];
const maxLogSize = 10000;

const defaultRateLimits: Record<string, RateLimitConfig> = {
  default: { windowMs: 60 * 1000, maxRequests: 100 },
  auth: { windowMs: 15 * 60 * 1000, maxRequests: 10 },
  api: { windowMs: 60 * 1000, maxRequests: 200 },
  export: { windowMs: 60 * 1000, maxRequests: 10 },
  powerbi: { windowMs: 60 * 1000, maxRequests: 30 },
};

function getRateLimitKey(req: Request, identifier: string): string {
  const ip = req.ip || req.socket.remoteAddress || "unknown";
  const userId = (req as any).session?.userId;
  return `${identifier}:${userId || ip}`;
}

export function rateLimit(identifier: string = "default") {
  const config = defaultRateLimits[identifier] || defaultRateLimits.default;
  
  return (req: Request, res: Response, next: NextFunction): void => {
    const key = getRateLimitKey(req, identifier);
    const now = Date.now();
    
    let entry = rateLimitStore.get(key);
    
    if (!entry || entry.resetAt <= now) {
      entry = {
        count: 1,
        resetAt: now + config.windowMs,
      };
      rateLimitStore.set(key, entry);
    } else {
      entry.count++;
    }
    
    const remaining = Math.max(0, config.maxRequests - entry.count);
    const resetIn = Math.ceil((entry.resetAt - now) / 1000);
    
    res.setHeader("X-RateLimit-Limit", config.maxRequests.toString());
    res.setHeader("X-RateLimit-Remaining", remaining.toString());
    res.setHeader("X-RateLimit-Reset", resetIn.toString());
    
    if (entry.count > config.maxRequests) {
      res.status(429).json({
        error: "Too many requests",
        retryAfter: resetIn,
      });
      return;
    }
    
    next();
  };
}

export function requestLogger(req: Request, res: Response, next: NextFunction): void {
  const startTime = Date.now();
  const requestId = `req-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`;
  
  (req as any).requestId = requestId;
  
  res.on("finish", () => {
    const responseTime = Date.now() - startTime;
    
    const log: RequestLog = {
      id: requestId,
      timestamp: new Date(),
      method: req.method,
      path: req.path,
      statusCode: res.statusCode,
      responseTimeMs: responseTime,
      ip: req.ip || req.socket.remoteAddress,
      userId: (req as any).session?.userId,
      userAgent: req.get("user-agent"),
    };
    
    requestLogs.push(log);
    if (requestLogs.length > maxLogSize) {
      requestLogs.shift();
    }
    
    const statusColor = res.statusCode >= 500 ? "31" : res.statusCode >= 400 ? "33" : "32";
    console.log(`[API] ${req.method} ${req.path} \x1b[${statusColor}m${res.statusCode}\x1b[0m ${responseTime}ms`);
  });
  
  next();
}

export function securityHeaders(req: Request, res: Response, next: NextFunction): void {
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("X-Frame-Options", "DENY");
  res.setHeader("X-XSS-Protection", "1; mode=block");
  res.setHeader("Referrer-Policy", "strict-origin-when-cross-origin");
  res.setHeader("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.powerbi.com wss:;");
  next();
}

export function corsHandler(allowedOrigins: string[] = ["*"]) {
  return (req: Request, res: Response, next: NextFunction): void => {
    const origin = req.get("origin") || "";
    
    if (allowedOrigins.includes("*") || allowedOrigins.includes(origin)) {
      res.setHeader("Access-Control-Allow-Origin", origin || "*");
      res.setHeader("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS");
      res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With");
      res.setHeader("Access-Control-Allow-Credentials", "true");
      res.setHeader("Access-Control-Max-Age", "86400");
    }
    
    if (req.method === "OPTIONS") {
      res.status(204).end();
      return;
    }
    
    next();
  };
}

export function healthCheck(req: Request, res: Response): void {
  res.json({
    status: "healthy",
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    version: "1.0.0",
  });
}

export function getRequestLogs(options: {
  limit?: number;
  method?: string;
  path?: string;
  statusCode?: number;
  fromDate?: Date;
  toDate?: Date;
} = {}): RequestLog[] {
  let logs = requestLogs;
  
  if (options.method) {
    logs = logs.filter(l => l.method === options.method);
  }
  if (options.path) {
    const pathFilter = options.path;
    logs = logs.filter(l => l.path.includes(pathFilter));
  }
  if (options.statusCode) {
    logs = logs.filter(l => l.statusCode === options.statusCode);
  }
  if (options.fromDate) {
    logs = logs.filter(l => l.timestamp >= options.fromDate!);
  }
  if (options.toDate) {
    logs = logs.filter(l => l.timestamp <= options.toDate!);
  }
  
  return logs.slice(-(options.limit || 100));
}

export function getApiMetrics(): {
  totalRequests: number;
  avgResponseTime: number;
  errorRate: number;
  requestsByMethod: Record<string, number>;
  requestsByStatus: Record<string, number>;
} {
  const total = requestLogs.length;
  if (total === 0) {
    return {
      totalRequests: 0,
      avgResponseTime: 0,
      errorRate: 0,
      requestsByMethod: {},
      requestsByStatus: {},
    };
  }
  
  const totalTime = requestLogs.reduce((sum, l) => sum + l.responseTimeMs, 0);
  const errorCount = requestLogs.filter(l => l.statusCode >= 400).length;
  
  const byMethod: Record<string, number> = {};
  const byStatus: Record<string, number> = {};
  
  for (const log of requestLogs) {
    byMethod[log.method] = (byMethod[log.method] || 0) + 1;
    const statusGroup = `${Math.floor(log.statusCode / 100)}xx`;
    byStatus[statusGroup] = (byStatus[statusGroup] || 0) + 1;
  }
  
  return {
    totalRequests: total,
    avgResponseTime: Math.round(totalTime / total),
    errorRate: Math.round((errorCount / total) * 100) / 100,
    requestsByMethod: byMethod,
    requestsByStatus: byStatus,
  };
}

export function cleanupRateLimits(): void {
  const now = Date.now();
  const entries = Array.from(rateLimitStore.entries());
  for (const [key, entry] of entries) {
    if (entry.resetAt <= now) {
      rateLimitStore.delete(key);
    }
  }
}

setInterval(cleanupRateLimits, 60 * 1000);
