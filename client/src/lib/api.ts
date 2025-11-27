import type { 
  Project, InsertProject, Equipment, Client, Transaction, Document, SafetyInspection,
  Lead, InsertLead, Opportunity, InsertOpportunity, Account, InsertAccount, 
  Contact, InsertContact, Campaign, InsertCampaign, Ticket, InsertTicket,
  Product, InsertProduct, StockItem, Invoice, InsertInvoice, Payment, InsertPayment,
  Employee, InsertEmployee, PayrollRecord, LeaveRequest, InsertLeaveRequest,
  SalesOrder, InsertSalesOrder, PurchaseOrder, InsertPurchaseOrder
} from "@shared/schema";

const API_BASE = "/api/v1";

let authToken: string | null = null;

export function setAuthToken(token: string | null) {
  authToken = token;
}

export function getAuthToken(): string | null {
  return authToken;
}

function getAuthHeaders(): HeadersInit {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };
  
  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }
  
  return headers;
}

async function authFetch(url: string, options: RequestInit = {}): Promise<Response> {
  return fetch(url, {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...(options.headers || {}),
    },
  });
}

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("Authentication required");
    }
    if (response.status === 403) {
      throw new Error("Access denied - insufficient permissions");
    }
    const error = await response.json().catch(() => ({ error: "Request failed" }));
    throw new Error(error.error || error.detail || "Request failed");
  }
  return response.json();
}

async function handleListResponse<T>(response: Response): Promise<T[]> {
  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("Authentication required");
    }
    if (response.status === 403) {
      throw new Error("Access denied - insufficient permissions");
    }
    const error = await response.json().catch(() => ({ error: "Request failed" }));
    throw new Error(error.error || error.detail || "Request failed");
  }
  const data = await response.json();
  if (data && typeof data === 'object' && 'results' in data) {
    return (data as PaginatedResponse<T>).results;
  }
  return data as T[];
}

export interface ProjectMetrics {
  total_projects: number;
  active_projects: number;
  on_track_count: number;
  at_risk_count: number;
  delayed_count: number;
  total_budget: string;
  total_actual_cost: string;
  overall_cost_variance: string;
  avg_progress: number;
}

export interface ProjectDetailMetrics {
  project_id: string;
  project_name: string;
  progress: {
    actual: number;
    planned: number;
    variance: number;
  };
  budget: {
    budgeted: number;
    actual: number;
    variance: number;
    variance_percent: number;
  };
  milestone: {
    name: string | null;
    date: string | null;
    days_remaining: number | null;
  };
  issues: {
    open_inspections: number;
  };
  financials: {
    total_expenses: number;
    total_income: number;
    transaction_count: number;
  };
  health_status: 'on_track' | 'at_risk' | 'delayed';
}

export interface CashflowDataPoint {
  date: string;
  amount: string;
  cumulative: string;
}

export interface ProjectCashflow {
  project_id: string;
  project_name: string;
  period: { start: string; end: string };
  data: CashflowDataPoint[];
}

export interface ExtendedProject extends Project {
  plannedProgress?: number;
  actualCost?: string;
  nextMilestoneDate?: string;
  nextMilestoneName?: string;
  progress_variance?: number;
  cost_variance?: number;
  health_status?: 'on_track' | 'at_risk' | 'delayed';
  days_until_milestone?: number | null;
  open_issues_count?: number;
}

export async function getProjects(): Promise<ExtendedProject[]> {
  const response = await authFetch(`${API_BASE}/projects/`);
  return handleListResponse(response);
}

export async function getProjectsSummary(): Promise<ProjectMetrics> {
  const response = await authFetch(`${API_BASE}/projects/summary/`);
  return handleResponse(response);
}

export async function getProjectMetrics(projectId: string): Promise<ProjectDetailMetrics> {
  const response = await authFetch(`${API_BASE}/projects/${projectId}/metrics/`);
  return handleResponse(response);
}

export async function getProjectCashflow(projectId: string): Promise<ProjectCashflow> {
  const response = await authFetch(`${API_BASE}/projects/${projectId}/cashflow/`);
  return handleResponse(response);
}

export async function createProject(project: InsertProject): Promise<Project> {
  const response = await authFetch(`${API_BASE}/projects/`, {
    method: "POST",
    body: JSON.stringify(project),
  });
  return handleResponse(response);
}

export async function updateProject(id: string, updates: Partial<InsertProject>): Promise<Project> {
  const response = await authFetch(`${API_BASE}/projects/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(updates),
  });
  return handleResponse(response);
}

export async function deleteProject(id: string): Promise<void> {
  const response = await authFetch(`${API_BASE}/projects/${id}/`, { method: "DELETE" });
  if (!response.ok) throw new Error("Failed to delete project");
}

export async function getEquipment(): Promise<Equipment[]> {
  const response = await authFetch(`${API_BASE}/equipment/`);
  return handleListResponse(response);
}

export async function getClients(): Promise<Client[]> {
  const response = await authFetch(`${API_BASE}/clients/`);
  return handleListResponse(response);
}

export async function getTransactions(): Promise<Transaction[]> {
  const response = await authFetch(`${API_BASE}/transactions/`);
  return handleListResponse(response);
}

export async function getDocuments(): Promise<Document[]> {
  const response = await authFetch(`${API_BASE}/documents/`);
  return handleListResponse(response);
}

export async function getSafetyInspections(): Promise<SafetyInspection[]> {
  const response = await authFetch(`${API_BASE}/safety/inspections/`);
  return handleListResponse(response);
}

export async function getLeads(): Promise<Lead[]> {
  const response = await authFetch(`${API_BASE}/leads/`);
  return handleListResponse(response);
}

export async function createLead(lead: InsertLead): Promise<Lead> {
  const response = await authFetch(`${API_BASE}/leads/`, {
    method: "POST",
    body: JSON.stringify(lead),
  });
  return handleResponse(response);
}

export async function updateLead(id: string, updates: Partial<InsertLead>): Promise<Lead> {
  const response = await authFetch(`${API_BASE}/leads/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(updates),
  });
  return handleResponse(response);
}

export async function convertLead(id: string): Promise<{ contact: Contact; account: Account }> {
  const response = await authFetch(`${API_BASE}/leads/${id}/convert/`, { method: "POST" });
  return handleResponse(response);
}

export async function getOpportunities(): Promise<Opportunity[]> {
  const response = await authFetch(`${API_BASE}/opportunities/`);
  return handleListResponse(response);
}

export async function createOpportunity(opportunity: InsertOpportunity): Promise<Opportunity> {
  const response = await authFetch(`${API_BASE}/opportunities/`, {
    method: "POST",
    body: JSON.stringify(opportunity),
  });
  return handleResponse(response);
}

export async function updateOpportunity(id: string, updates: Partial<InsertOpportunity>): Promise<Opportunity> {
  const response = await authFetch(`${API_BASE}/opportunities/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(updates),
  });
  return handleResponse(response);
}

export async function getAccounts(): Promise<Account[]> {
  const response = await authFetch(`${API_BASE}/accounts/`);
  return handleListResponse(response);
}

export async function createAccount(account: InsertAccount): Promise<Account> {
  const response = await authFetch(`${API_BASE}/accounts/`, {
    method: "POST",
    body: JSON.stringify(account),
  });
  return handleResponse(response);
}

export async function getContacts(): Promise<Contact[]> {
  const response = await authFetch(`${API_BASE}/contacts/`);
  return handleListResponse(response);
}

export async function createContact(contact: InsertContact): Promise<Contact> {
  const response = await authFetch(`${API_BASE}/contacts/`, {
    method: "POST",
    body: JSON.stringify(contact),
  });
  return handleResponse(response);
}

export async function getCampaigns(): Promise<Campaign[]> {
  const response = await authFetch(`${API_BASE}/campaigns/`);
  return handleListResponse(response);
}

export async function createCampaign(campaign: InsertCampaign): Promise<Campaign> {
  const response = await authFetch(`${API_BASE}/campaigns/`, {
    method: "POST",
    body: JSON.stringify(campaign),
  });
  return handleResponse(response);
}

export async function getTickets(): Promise<Ticket[]> {
  const response = await authFetch(`${API_BASE}/tickets/`);
  return handleListResponse(response);
}

export async function createTicket(ticket: InsertTicket): Promise<Ticket> {
  const response = await authFetch(`${API_BASE}/tickets/`, {
    method: "POST",
    body: JSON.stringify(ticket),
  });
  return handleResponse(response);
}

export async function updateTicket(id: string, updates: Partial<InsertTicket>): Promise<Ticket> {
  const response = await authFetch(`${API_BASE}/tickets/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(updates),
  });
  return handleResponse(response);
}

export async function getProducts(): Promise<Product[]> {
  const response = await authFetch(`${API_BASE}/products/`);
  return handleListResponse(response);
}

export async function createProduct(product: InsertProduct): Promise<Product> {
  const response = await authFetch(`${API_BASE}/products/`, {
    method: "POST",
    body: JSON.stringify(product),
  });
  return handleResponse(response);
}

export async function getStockItems(): Promise<StockItem[]> {
  const response = await authFetch(`${API_BASE}/stock/`);
  return handleListResponse(response);
}

export async function getInvoices(): Promise<Invoice[]> {
  const response = await authFetch(`${API_BASE}/invoices/`);
  return handleListResponse(response);
}

export async function createInvoice(invoice: InsertInvoice): Promise<Invoice> {
  const response = await authFetch(`${API_BASE}/invoices/`, {
    method: "POST",
    body: JSON.stringify(invoice),
  });
  return handleResponse(response);
}

export async function getPayments(): Promise<Payment[]> {
  const response = await authFetch(`${API_BASE}/payments/`);
  return handleListResponse(response);
}

export async function createPayment(payment: InsertPayment): Promise<Payment> {
  const response = await authFetch(`${API_BASE}/payments/`, {
    method: "POST",
    body: JSON.stringify(payment),
  });
  return handleResponse(response);
}

export async function getEmployees(): Promise<Employee[]> {
  const response = await authFetch(`${API_BASE}/employees/`);
  return handleListResponse(response);
}

export async function createEmployee(employee: InsertEmployee): Promise<Employee> {
  const response = await authFetch(`${API_BASE}/employees/`, {
    method: "POST",
    body: JSON.stringify(employee),
  });
  return handleResponse(response);
}

export async function updateEmployee(id: string, updates: Partial<InsertEmployee>): Promise<Employee> {
  const response = await authFetch(`${API_BASE}/employees/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(updates),
  });
  return handleResponse(response);
}

export async function getPayrollRecords(): Promise<PayrollRecord[]> {
  const response = await authFetch(`${API_BASE}/payroll/`);
  return handleListResponse(response);
}

export async function getLeaveRequests(): Promise<LeaveRequest[]> {
  const response = await authFetch(`${API_BASE}/leave-requests/`);
  return handleListResponse(response);
}

export async function createLeaveRequest(request: InsertLeaveRequest): Promise<LeaveRequest> {
  const response = await authFetch(`${API_BASE}/leave-requests/`, {
    method: "POST",
    body: JSON.stringify(request),
  });
  return handleResponse(response);
}

export async function getSalesOrders(): Promise<SalesOrder[]> {
  const response = await authFetch(`${API_BASE}/sales-orders/`);
  return handleListResponse(response);
}

export async function createSalesOrder(order: InsertSalesOrder): Promise<SalesOrder> {
  const response = await authFetch(`${API_BASE}/sales-orders/`, {
    method: "POST",
    body: JSON.stringify(order),
  });
  return handleResponse(response);
}

export async function updateSalesOrder(id: string, updates: Partial<InsertSalesOrder>): Promise<SalesOrder> {
  const response = await authFetch(`${API_BASE}/sales-orders/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(updates),
  });
  return handleResponse(response);
}

export async function getPurchaseOrders(): Promise<PurchaseOrder[]> {
  const response = await authFetch(`${API_BASE}/purchase-orders/`);
  return handleListResponse(response);
}

export async function createPurchaseOrder(order: InsertPurchaseOrder): Promise<PurchaseOrder> {
  const response = await authFetch(`${API_BASE}/purchase-orders/`, {
    method: "POST",
    body: JSON.stringify(order),
  });
  return handleResponse(response);
}

export async function updatePurchaseOrder(id: string, updates: Partial<InsertPurchaseOrder>): Promise<PurchaseOrder> {
  const response = await authFetch(`${API_BASE}/purchase-orders/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(updates),
  });
  return handleResponse(response);
}

export async function getDashboardStats(): Promise<any> {
  const response = await authFetch(`${API_BASE}/analytics/dashboard/`);
  return handleResponse(response);
}

export interface SearchResult {
  id: string;
  type: 'contact' | 'product' | 'order' | 'ticket';
  title: string;
  subtitle: string;
  [key: string]: any;
}

export interface SearchResults {
  contacts: SearchResult[];
  products: SearchResult[];
  orders: SearchResult[];
  tickets: SearchResult[];
  total: number;
}

export async function globalSearch(query: string, limit = 5): Promise<SearchResults> {
  const response = await authFetch(`${API_BASE}/search/?q=${encodeURIComponent(query)}&limit=${limit}`);
  return handleResponse(response);
}

export interface AccountLookupResult {
  id: string;
  name: string;
  account_number: string;
  type: string;
  payment_terms: string;
  credit_limit: string | null;
  billing_address: {
    street: string | null;
    city: string | null;
    state: string | null;
    postal_code: string | null;
    country: string | null;
  } | null;
}

export async function lookupAccounts(term: string, limit = 10): Promise<AccountLookupResult[]> {
  const response = await authFetch(`${API_BASE}/accounts/lookup/?term=${encodeURIComponent(term)}&limit=${limit}`);
  return handleResponse(response);
}

export interface ProductLookupResult {
  id: string;
  sku: string;
  name: string;
  description: string;
  category: string;
  unit: string;
  unit_price: string;
  cost_price: string | null;
  stock: {
    quantity: number;
    in_stock: boolean;
    status: 'in_stock' | 'low_stock' | 'out_of_stock';
    reorder_level: number;
  };
}

export async function lookupProducts(term: string, limit = 10, warehouseId?: string): Promise<ProductLookupResult[]> {
  let url = `${API_BASE}/products/lookup/?term=${encodeURIComponent(term)}&limit=${limit}`;
  if (warehouseId) url += `&warehouse_id=${warehouseId}`;
  const response = await authFetch(url);
  return handleResponse(response);
}

export interface AccountRelatedData {
  open_tickets: Array<{
    id: string;
    ticket_number: string;
    subject: string;
    status: string;
    priority: string;
    created_at: string;
  }>;
  open_tickets_count: number;
  recent_invoices: Array<{
    id: string;
    invoice_number: string;
    status: string;
    total_amount: string;
    due_date: string | null;
    created_at: string;
  }>;
  total_invoices: number;
  contacts: Array<{
    id: string;
    name: string;
    email: string;
    title: string;
    is_primary: boolean;
  }>;
  total_contacts: number;
}

export async function getAccountRelated(accountId: string): Promise<AccountRelatedData> {
  const response = await authFetch(`${API_BASE}/accounts/${accountId}/related/`);
  return handleResponse(response);
}

export interface Favorite {
  id: string;
  user: string;
  entity_type: string;
  entity_id: string;
  entity_title: string;
  entity_subtitle: string | null;
  created_at: string;
}

export async function getFavorites(userId?: string): Promise<Favorite[]> {
  let url = `${API_BASE}/favorites/`;
  if (userId) url += `?user_id=${userId}`;
  const response = await authFetch(url);
  return handleListResponse(response);
}

export async function addFavorite(favorite: Omit<Favorite, 'id' | 'created_at'>): Promise<Favorite> {
  const response = await authFetch(`${API_BASE}/favorites/`, {
    method: "POST",
    body: JSON.stringify(favorite),
  });
  return handleResponse(response);
}

export async function removeFavorite(id: string): Promise<void> {
  const response = await authFetch(`${API_BASE}/favorites/${id}/`, { method: "DELETE" });
  if (!response.ok) throw new Error("Failed to remove favorite");
}

export interface AIHealthResponse {
  status: string;
  models: Record<string, {
    model_name: string;
    model_version: string;
    trained_at: string;
    accuracy: number;
  }>;
}

export interface CreditRiskPrediction {
  customer_id: string;
  customer_name: string | null;
  risk_score: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  confidence: number;
  factors: string[];
  recommended_payment_terms: string;
  recommended_credit_limit: number;
  model_info: { model_name: string; model_version: string; trained_at: string; accuracy: number };
  predicted_at: string;
}

export interface LeadScorePrediction {
  lead_id: string;
  lead_name: string | null;
  score: number;
  conversion_probability: number;
  priority: 'hot' | 'warm' | 'qualified' | 'cold';
  factors: string[];
  recommended_actions: string[];
  model_info: { model_name: string; model_version: string; trained_at: string; accuracy: number };
  predicted_at: string;
}

export interface ProjectDelayPrediction {
  project_id: string;
  project_name: string | null;
  delay_probability: number;
  expected_delay_days: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  risk_factors: string[];
  mitigation_suggestions: string[];
  model_info: { model_name: string; model_version: string; trained_at: string; accuracy: number };
  predicted_at: string;
}

export interface MaintenanceRiskPrediction {
  equipment_id: string;
  equipment_name: string | null;
  failure_probability: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  estimated_remaining_life_days: number;
  recommended_maintenance_date: string;
  maintenance_type: string;
  estimated_downtime_hours: number;
  parts_needed: string[];
  model_info: { model_name: string; model_version: string; trained_at: string; accuracy: number };
  predicted_at: string;
}

export interface DemandForecastPrediction {
  product_id: string;
  product_name: string | null;
  warehouse_id: string | null;
  forecast: Array<{
    date: string;
    predicted_demand: number;
    confidence_lower: number;
    confidence_upper: number;
  }>;
  current_stock: number;
  reorder_point: number;
  suggested_order_quantity: number;
  stockout_risk_date: string | null;
  model_info: { model_name: string; model_version: string; trained_at: string; accuracy: number };
  predicted_at: string;
}

export interface CashFlowForecast {
  forecast: Array<{
    date: string;
    predicted_inflow: number;
    predicted_outflow: number;
    net_cash_flow: number;
    confidence_lower: number;
    confidence_upper: number;
  }>;
  summary: {
    total_predicted_inflow: number;
    total_predicted_outflow: number;
    net_cash_flow: number;
    average_daily_balance: number;
  };
  model_info: { model_name: string; model_version: string; trained_at: string; accuracy: number };
  predicted_at: string;
}

export async function getAIHealth(): Promise<AIHealthResponse> {
  const response = await authFetch(`${API_BASE}/ai/health/`);
  return handleResponse(response);
}

export async function getCreditRiskPrediction(customerId: string): Promise<CreditRiskPrediction> {
  const response = await authFetch(`${API_BASE}/ai/credit-risk/predict/${customerId}/`);
  return handleResponse(response);
}

export async function getLeadScore(leadId: string): Promise<LeadScorePrediction> {
  const response = await authFetch(`${API_BASE}/ai/leads/score/${leadId}/`);
  return handleResponse(response);
}

export async function getProjectDelayPrediction(projectId: string): Promise<ProjectDelayPrediction> {
  const response = await authFetch(`${API_BASE}/ai/projects/delay-risk/${projectId}/`);
  return handleResponse(response);
}

export async function getMaintenanceRiskPrediction(equipmentId: string): Promise<MaintenanceRiskPrediction> {
  const response = await authFetch(`${API_BASE}/ai/equipment/maintenance-risk/${equipmentId}/`);
  return handleResponse(response);
}

export async function getDemandForecast(productId: string): Promise<DemandForecastPrediction> {
  const response = await authFetch(`${API_BASE}/ai/inventory/demand-forecast/${productId}/`);
  return handleResponse(response);
}

export async function getCashFlowForecast(daysAhead: number = 30): Promise<CashFlowForecast> {
  const response = await authFetch(`${API_BASE}/ai/cashflow/forecast/`, {
    method: "POST",
    body: JSON.stringify({ days_ahead: daysAhead }),
  });
  return handleResponse(response);
}
