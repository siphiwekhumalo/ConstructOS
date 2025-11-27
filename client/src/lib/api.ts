import type { 
  Project, InsertProject, Equipment, Client, Transaction, Document, SafetyInspection,
  Lead, InsertLead, Opportunity, InsertOpportunity, Account, InsertAccount, 
  Contact, InsertContact, Campaign, InsertCampaign, Ticket, InsertTicket,
  Product, InsertProduct, StockItem, Invoice, InsertInvoice, Payment, InsertPayment,
  Employee, InsertEmployee, PayrollRecord, LeaveRequest, InsertLeaveRequest,
  SalesOrder, InsertSalesOrder, PurchaseOrder, InsertPurchaseOrder
} from "@shared/schema";

const API_BASE = "/api/v1";

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Request failed" }));
    throw new Error(error.error || error.detail || "Request failed");
  }
  return response.json();
}

async function handleListResponse<T>(response: Response): Promise<T[]> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Request failed" }));
    throw new Error(error.error || error.detail || "Request failed");
  }
  const data = await response.json();
  if (data && typeof data === 'object' && 'results' in data) {
    return (data as PaginatedResponse<T>).results;
  }
  return data as T[];
}

export async function getProjects(): Promise<Project[]> {
  const response = await fetch(`${API_BASE}/projects/`);
  return handleListResponse(response);
}

export async function createProject(project: InsertProject): Promise<Project> {
  const response = await fetch(`${API_BASE}/projects/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(project),
  });
  return handleResponse(response);
}

export async function updateProject(id: string, updates: Partial<InsertProject>): Promise<Project> {
  const response = await fetch(`${API_BASE}/projects/${id}/`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updates),
  });
  return handleResponse(response);
}

export async function deleteProject(id: string): Promise<void> {
  const response = await fetch(`${API_BASE}/projects/${id}/`, { method: "DELETE" });
  if (!response.ok) throw new Error("Failed to delete project");
}

export async function getEquipment(): Promise<Equipment[]> {
  const response = await fetch(`${API_BASE}/equipment/`);
  return handleListResponse(response);
}

export async function getClients(): Promise<Client[]> {
  const response = await fetch(`${API_BASE}/clients/`);
  return handleListResponse(response);
}

export async function getTransactions(): Promise<Transaction[]> {
  const response = await fetch(`${API_BASE}/transactions/`);
  return handleListResponse(response);
}

export async function getDocuments(): Promise<Document[]> {
  const response = await fetch(`${API_BASE}/documents/`);
  return handleListResponse(response);
}

export async function getSafetyInspections(): Promise<SafetyInspection[]> {
  const response = await fetch(`${API_BASE}/safety/inspections/`);
  return handleListResponse(response);
}

export async function getLeads(): Promise<Lead[]> {
  const response = await fetch(`${API_BASE}/leads/`);
  return handleListResponse(response);
}

export async function createLead(lead: InsertLead): Promise<Lead> {
  const response = await fetch(`${API_BASE}/leads/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(lead),
  });
  return handleResponse(response);
}

export async function updateLead(id: string, updates: Partial<InsertLead>): Promise<Lead> {
  const response = await fetch(`${API_BASE}/leads/${id}/`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updates),
  });
  return handleResponse(response);
}

export async function convertLead(id: string): Promise<{ contact: Contact; account: Account }> {
  const response = await fetch(`${API_BASE}/leads/${id}/convert/`, { method: "POST" });
  return handleResponse(response);
}

export async function getOpportunities(): Promise<Opportunity[]> {
  const response = await fetch(`${API_BASE}/opportunities/`);
  return handleListResponse(response);
}

export async function createOpportunity(opportunity: InsertOpportunity): Promise<Opportunity> {
  const response = await fetch(`${API_BASE}/opportunities/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(opportunity),
  });
  return handleResponse(response);
}

export async function updateOpportunity(id: string, updates: Partial<InsertOpportunity>): Promise<Opportunity> {
  const response = await fetch(`${API_BASE}/opportunities/${id}/`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updates),
  });
  return handleResponse(response);
}

export async function getAccounts(): Promise<Account[]> {
  const response = await fetch(`${API_BASE}/accounts/`);
  return handleListResponse(response);
}

export async function createAccount(account: InsertAccount): Promise<Account> {
  const response = await fetch(`${API_BASE}/accounts/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(account),
  });
  return handleResponse(response);
}

export async function getContacts(): Promise<Contact[]> {
  const response = await fetch(`${API_BASE}/contacts/`);
  return handleListResponse(response);
}

export async function createContact(contact: InsertContact): Promise<Contact> {
  const response = await fetch(`${API_BASE}/contacts/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(contact),
  });
  return handleResponse(response);
}

export async function getCampaigns(): Promise<Campaign[]> {
  const response = await fetch(`${API_BASE}/campaigns/`);
  return handleListResponse(response);
}

export async function createCampaign(campaign: InsertCampaign): Promise<Campaign> {
  const response = await fetch(`${API_BASE}/campaigns/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(campaign),
  });
  return handleResponse(response);
}

export async function getTickets(): Promise<Ticket[]> {
  const response = await fetch(`${API_BASE}/tickets/`);
  return handleListResponse(response);
}

export async function createTicket(ticket: InsertTicket): Promise<Ticket> {
  const response = await fetch(`${API_BASE}/tickets/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(ticket),
  });
  return handleResponse(response);
}

export async function updateTicket(id: string, updates: Partial<InsertTicket>): Promise<Ticket> {
  const response = await fetch(`${API_BASE}/tickets/${id}/`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updates),
  });
  return handleResponse(response);
}

export async function getProducts(): Promise<Product[]> {
  const response = await fetch(`${API_BASE}/products/`);
  return handleListResponse(response);
}

export async function createProduct(product: InsertProduct): Promise<Product> {
  const response = await fetch(`${API_BASE}/products/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(product),
  });
  return handleResponse(response);
}

export async function getStockItems(): Promise<StockItem[]> {
  const response = await fetch(`${API_BASE}/stock/`);
  return handleListResponse(response);
}

export async function getInvoices(): Promise<Invoice[]> {
  const response = await fetch(`${API_BASE}/invoices/`);
  return handleListResponse(response);
}

export async function createInvoice(invoice: InsertInvoice): Promise<Invoice> {
  const response = await fetch(`${API_BASE}/invoices/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(invoice),
  });
  return handleResponse(response);
}

export async function getPayments(): Promise<Payment[]> {
  const response = await fetch(`${API_BASE}/payments/`);
  return handleListResponse(response);
}

export async function createPayment(payment: InsertPayment): Promise<Payment> {
  const response = await fetch(`${API_BASE}/payments/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payment),
  });
  return handleResponse(response);
}

export async function getEmployees(): Promise<Employee[]> {
  const response = await fetch(`${API_BASE}/employees/`);
  return handleListResponse(response);
}

export async function createEmployee(employee: InsertEmployee): Promise<Employee> {
  const response = await fetch(`${API_BASE}/employees/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(employee),
  });
  return handleResponse(response);
}

export async function updateEmployee(id: string, updates: Partial<InsertEmployee>): Promise<Employee> {
  const response = await fetch(`${API_BASE}/employees/${id}/`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updates),
  });
  return handleResponse(response);
}

export async function getPayrollRecords(): Promise<PayrollRecord[]> {
  const response = await fetch(`${API_BASE}/payroll/`);
  return handleListResponse(response);
}

export async function getLeaveRequests(): Promise<LeaveRequest[]> {
  const response = await fetch(`${API_BASE}/leave-requests/`);
  return handleListResponse(response);
}

export async function createLeaveRequest(request: InsertLeaveRequest): Promise<LeaveRequest> {
  const response = await fetch(`${API_BASE}/leave-requests/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  return handleResponse(response);
}

export async function getSalesOrders(): Promise<SalesOrder[]> {
  const response = await fetch(`${API_BASE}/sales-orders/`);
  return handleListResponse(response);
}

export async function createSalesOrder(order: InsertSalesOrder): Promise<SalesOrder> {
  const response = await fetch(`${API_BASE}/sales-orders/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(order),
  });
  return handleResponse(response);
}

export async function updateSalesOrder(id: string, updates: Partial<InsertSalesOrder>): Promise<SalesOrder> {
  const response = await fetch(`${API_BASE}/sales-orders/${id}/`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updates),
  });
  return handleResponse(response);
}

export async function getPurchaseOrders(): Promise<PurchaseOrder[]> {
  const response = await fetch(`${API_BASE}/purchase-orders/`);
  return handleListResponse(response);
}

export async function createPurchaseOrder(order: InsertPurchaseOrder): Promise<PurchaseOrder> {
  const response = await fetch(`${API_BASE}/purchase-orders/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(order),
  });
  return handleResponse(response);
}

export async function updatePurchaseOrder(id: string, updates: Partial<InsertPurchaseOrder>): Promise<PurchaseOrder> {
  const response = await fetch(`${API_BASE}/purchase-orders/${id}/`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updates),
  });
  return handleResponse(response);
}

export async function getDashboardStats(): Promise<any> {
  const response = await fetch(`${API_BASE}/analytics/dashboard/`);
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
  const response = await fetch(`${API_BASE}/search/?q=${encodeURIComponent(query)}&limit=${limit}`);
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
  const response = await fetch(`${API_BASE}/accounts/lookup/?term=${encodeURIComponent(term)}&limit=${limit}`);
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
  const response = await fetch(url);
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
  const response = await fetch(`${API_BASE}/accounts/${accountId}/related/`);
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
  const response = await fetch(url);
  return handleListResponse(response);
}

export async function addFavorite(favorite: Omit<Favorite, 'id' | 'created_at'>): Promise<Favorite> {
  const response = await fetch(`${API_BASE}/favorites/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(favorite),
  });
  return handleResponse(response);
}

export async function removeFavorite(id: string): Promise<void> {
  const response = await fetch(`${API_BASE}/favorites/${id}/`, { method: "DELETE" });
  if (!response.ok) throw new Error("Failed to remove favorite");
}
