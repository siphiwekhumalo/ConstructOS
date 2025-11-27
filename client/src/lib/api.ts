import type { 
  Project, InsertProject, Equipment, Client, Transaction, Document, SafetyInspection,
  Lead, InsertLead, Opportunity, InsertOpportunity, Account, InsertAccount, 
  Contact, InsertContact, Campaign, InsertCampaign, Ticket, InsertTicket,
  Product, InsertProduct, StockItem, Invoice, InsertInvoice, Payment, InsertPayment,
  Employee, InsertEmployee, PayrollRecord, LeaveRequest, InsertLeaveRequest,
  SalesOrder, InsertSalesOrder, PurchaseOrder, InsertPurchaseOrder
} from "@shared/schema";

const API_BASE = "/api/v1";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Request failed" }));
    throw new Error(error.error || error.detail || "Request failed");
  }
  return response.json();
}

export async function getProjects(): Promise<Project[]> {
  const response = await fetch(`${API_BASE}/projects/`);
  return handleResponse(response);
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
  return handleResponse(response);
}

export async function getClients(): Promise<Client[]> {
  const response = await fetch(`${API_BASE}/clients/`);
  return handleResponse(response);
}

export async function getTransactions(): Promise<Transaction[]> {
  const response = await fetch(`${API_BASE}/transactions/`);
  return handleResponse(response);
}

export async function getDocuments(): Promise<Document[]> {
  const response = await fetch(`${API_BASE}/documents/`);
  return handleResponse(response);
}

export async function getSafetyInspections(): Promise<SafetyInspection[]> {
  const response = await fetch(`${API_BASE}/safety/inspections/`);
  return handleResponse(response);
}

export async function getLeads(): Promise<Lead[]> {
  const response = await fetch(`${API_BASE}/leads/`);
  return handleResponse(response);
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
  return handleResponse(response);
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
  return handleResponse(response);
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
  return handleResponse(response);
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
  return handleResponse(response);
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
  return handleResponse(response);
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
  return handleResponse(response);
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
  return handleResponse(response);
}

export async function getInvoices(): Promise<Invoice[]> {
  const response = await fetch(`${API_BASE}/invoices/`);
  return handleResponse(response);
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
  return handleResponse(response);
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
  return handleResponse(response);
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
  return handleResponse(response);
}

export async function getLeaveRequests(): Promise<LeaveRequest[]> {
  const response = await fetch(`${API_BASE}/leave-requests/`);
  return handleResponse(response);
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
  return handleResponse(response);
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
  return handleResponse(response);
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
