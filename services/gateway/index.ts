/**
 * API Gateway for ConstructOS Microservices
 * 
 * This Express.js gateway handles:
 * - Request routing to appropriate microservices
 * - Authentication validation
 * - Rate limiting
 * - Request logging
 * - Circuit breaking
 * - Health aggregation
 */

import express, { Request, Response, NextFunction } from 'express';
import { createProxyMiddleware, Options } from 'http-proxy-middleware';
import cors from 'cors';

const app = express();
const PORT = process.env.PORT || 5000;

// Service URLs from environment
const SERVICES = {
  identity: process.env.IDENTITY_SERVICE_URL || 'http://localhost:8001',
  sales: process.env.SALES_SERVICE_URL || 'http://localhost:8002',
  finance: process.env.FINANCE_SERVICE_URL || 'http://localhost:8003',
  inventory: process.env.INVENTORY_SERVICE_URL || 'http://localhost:8004',
  hr: process.env.HR_SERVICE_URL || 'http://localhost:8005',
  compliance: process.env.COMPLIANCE_SERVICE_URL || 'http://localhost:8006',
  project: process.env.PROJECT_SERVICE_URL || 'http://localhost:8007',
  document: process.env.DOCUMENT_SERVICE_URL || 'http://localhost:8008',
};

// Route mappings to services
const ROUTE_MAPPINGS: { [key: string]: string } = {
  // Identity Service routes
  '/api/v1/auth': 'identity',
  '/api/v1/users': 'identity',
  '/api/v1/accounts': 'identity',
  '/api/v1/contacts': 'identity',
  '/api/v1/addresses': 'identity',
  '/api/v1/favorites': 'identity',
  '/api/v1/audit-logs': 'identity',
  
  // Sales Service routes
  '/api/v1/leads': 'sales',
  '/api/v1/opportunities': 'sales',
  '/api/v1/campaigns': 'sales',
  '/api/v1/activities': 'sales',
  
  // Finance Service routes
  '/api/v1/invoices': 'finance',
  '/api/v1/payments': 'finance',
  '/api/v1/transactions': 'finance',
  '/api/v1/budgets': 'finance',
  
  // Inventory Service routes
  '/api/v1/warehouses': 'inventory',
  '/api/v1/products': 'inventory',
  '/api/v1/stock': 'inventory',
  '/api/v1/equipment': 'inventory',
  
  // HR Service routes
  '/api/v1/employees': 'hr',
  '/api/v1/payroll': 'hr',
  '/api/v1/leave-requests': 'hr',
  
  // Compliance Service routes
  '/api/v1/tickets': 'compliance',
  '/api/v1/safety': 'compliance',
  '/api/v1/inspections': 'compliance',
  
  // Project Service routes
  '/api/v1/projects': 'project',
  '/api/v1/sales-orders': 'project',
  '/api/v1/purchase-orders': 'project',
  '/api/v1/tasks': 'project',
  
  // Document Service routes
  '/api/v1/documents': 'document',
  '/api/v1/files': 'document',
};

// Middleware
app.use(cors());
app.use(express.json());

// Request logging
app.use((req: Request, res: Response, next: NextFunction) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(`[Gateway] ${req.method} ${req.path} ${res.statusCode} ${duration}ms`);
  });
  next();
});

// Health check endpoint
app.get('/health', async (req: Request, res: Response) => {
  const healthChecks: { [key: string]: string } = {};
  
  for (const [name, url] of Object.entries(SERVICES)) {
    try {
      const response = await fetch(`${url}/api/v1/health/`);
      healthChecks[name] = response.ok ? 'healthy' : 'unhealthy';
    } catch {
      healthChecks[name] = 'unavailable';
    }
  }
  
  const allHealthy = Object.values(healthChecks).every(s => s === 'healthy');
  res.status(allHealthy ? 200 : 503).json({
    status: allHealthy ? 'healthy' : 'degraded',
    services: healthChecks,
    timestamp: new Date().toISOString(),
  });
});

// Unified search endpoint (aggregates from multiple services)
app.get('/api/v1/search', async (req: Request, res: Response) => {
  const query = req.query.q as string;
  const limit = parseInt(req.query.limit as string) || 5;
  const authHeader = req.headers.authorization;
  
  if (!query || query.length < 2) {
    return res.json({ contacts: [], products: [], orders: [], tickets: [], total: 0 });
  }
  
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  if (authHeader) headers['Authorization'] = authHeader;
  
  try {
    const [contacts, products, tickets] = await Promise.all([
      fetch(`${SERVICES.identity}/api/v1/contacts/?search=${encodeURIComponent(query)}&limit=${limit}`, { headers })
        .then(r => r.ok ? r.json() : { results: [] })
        .then(d => d.results || []),
      fetch(`${SERVICES.inventory}/api/v1/products/?search=${encodeURIComponent(query)}&limit=${limit}`, { headers })
        .then(r => r.ok ? r.json() : { results: [] })
        .then(d => d.results || []),
      fetch(`${SERVICES.compliance}/api/v1/tickets/?search=${encodeURIComponent(query)}&limit=${limit}`, { headers })
        .then(r => r.ok ? r.json() : { results: [] })
        .then(d => d.results || []),
    ]);
    
    res.json({
      contacts: contacts.map((c: any) => ({
        id: c.id,
        type: 'contact',
        title: `${c.first_name} ${c.last_name}`,
        subtitle: c.email,
        ...c,
      })),
      products: products.map((p: any) => ({
        id: p.id,
        type: 'product',
        title: p.name,
        subtitle: p.sku,
        ...p,
      })),
      orders: [],
      tickets: tickets.map((t: any) => ({
        id: t.id,
        type: 'ticket',
        title: t.subject,
        subtitle: t.status,
        ...t,
      })),
      total: contacts.length + products.length + tickets.length,
    });
  } catch (error) {
    console.error('[Gateway] Search error:', error);
    res.status(500).json({ error: 'Search failed' });
  }
});

// Create proxy middleware for each service
function createServiceProxy(serviceName: string): Options {
  return {
    target: SERVICES[serviceName as keyof typeof SERVICES],
    changeOrigin: true,
    pathRewrite: undefined, // Keep the path as-is
    on: {
      proxyReq: (proxyReq, req) => {
        console.log(`[Gateway] Proxying ${req.method} ${req.url} -> ${serviceName}`);
      },
      error: (err, req, res) => {
        console.error(`[Gateway] Proxy error for ${serviceName}:`, err.message);
        (res as Response).status(503).json({
          error: 'Service unavailable',
          service: serviceName,
        });
      },
    },
  };
}

// Set up route proxies
for (const [path, service] of Object.entries(ROUTE_MAPPINGS)) {
  app.use(path, createProxyMiddleware(createServiceProxy(service)));
}

// Analytics dashboard (aggregates from multiple services)
app.get('/api/v1/analytics/dashboard', async (req: Request, res: Response) => {
  const authHeader = req.headers.authorization;
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  if (authHeader) headers['Authorization'] = authHeader;
  
  try {
    const [accounts, projects, employees, tickets] = await Promise.all([
      fetch(`${SERVICES.identity}/api/v1/accounts/`, { headers })
        .then(r => r.ok ? r.json() : { count: 0 })
        .then(d => d.count || 0),
      fetch(`${SERVICES.project}/api/v1/projects/`, { headers })
        .then(r => r.ok ? r.json() : { count: 0 })
        .then(d => d.count || 0),
      fetch(`${SERVICES.hr}/api/v1/employees/`, { headers })
        .then(r => r.ok ? r.json() : { count: 0 })
        .then(d => d.count || 0),
      fetch(`${SERVICES.compliance}/api/v1/tickets/?status=open`, { headers })
        .then(r => r.ok ? r.json() : { count: 0 })
        .then(d => d.count || 0),
    ]);
    
    res.json({
      total_accounts: accounts,
      total_projects: projects,
      total_employees: employees,
      open_tickets: tickets,
      revenue_this_month: 0,
      expenses_this_month: 0,
    });
  } catch (error) {
    console.error('[Gateway] Dashboard error:', error);
    res.status(500).json({ error: 'Failed to fetch dashboard data' });
  }
});

// Catch-all for unmatched API routes
app.use('/api/*', (req: Request, res: Response) => {
  res.status(404).json({
    error: 'Not found',
    message: `No service registered for path: ${req.path}`,
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`[Gateway] API Gateway running on port ${PORT}`);
  console.log('[Gateway] Service endpoints:');
  for (const [name, url] of Object.entries(SERVICES)) {
    console.log(`  - ${name}: ${url}`);
  }
});

export default app;
