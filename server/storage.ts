import { drizzle } from "drizzle-orm/neon-serverless";
import { Pool, neonConfig } from "@neondatabase/serverless";
import { eq, desc, sql } from "drizzle-orm";
import ws from "ws";
import {
  users,
  accounts,
  contacts,
  addresses,
  leads,
  opportunities,
  pipelineStages,
  campaigns,
  mailingLists,
  segments,
  tickets,
  ticketComments,
  slas,
  warehouses,
  products,
  stockItems,
  invoices,
  invoiceLineItems,
  payments,
  generalLedgerEntries,
  employees,
  payrollRecords,
  leaveRequests,
  salesOrders,
  salesOrderLineItems,
  purchaseOrders,
  purchaseOrderLineItems,
  projects,
  transactions,
  equipment,
  safetyInspections,
  clients,
  documents,
  events,
  auditLogs,
  type User,
  type InsertUser,
  type Account,
  type InsertAccount,
  type Contact,
  type InsertContact,
  type Address,
  type InsertAddress,
  type Lead,
  type InsertLead,
  type Opportunity,
  type InsertOpportunity,
  type PipelineStage,
  type InsertPipelineStage,
  type Campaign,
  type InsertCampaign,
  type MailingList,
  type InsertMailingList,
  type Segment,
  type InsertSegment,
  type Ticket,
  type InsertTicket,
  type TicketComment,
  type InsertTicketComment,
  type Sla,
  type InsertSla,
  type Warehouse,
  type InsertWarehouse,
  type Product,
  type InsertProduct,
  type StockItem,
  type InsertStockItem,
  type Invoice,
  type InsertInvoice,
  type InvoiceLineItem,
  type InsertInvoiceLineItem,
  type Payment,
  type InsertPayment,
  type GeneralLedgerEntry,
  type InsertGeneralLedgerEntry,
  type Employee,
  type InsertEmployee,
  type PayrollRecord,
  type InsertPayrollRecord,
  type LeaveRequest,
  type InsertLeaveRequest,
  type SalesOrder,
  type InsertSalesOrder,
  type SalesOrderLineItem,
  type InsertSalesOrderLineItem,
  type PurchaseOrder,
  type InsertPurchaseOrder,
  type PurchaseOrderLineItem,
  type InsertPurchaseOrderLineItem,
  type Project,
  type InsertProject,
  type Transaction,
  type InsertTransaction,
  type Equipment,
  type InsertEquipment,
  type SafetyInspection,
  type InsertSafetyInspection,
  type Client,
  type InsertClient,
  type Document,
  type InsertDocument,
  type Event,
  type InsertEvent,
  type AuditLog,
  type InsertAuditLog,
} from "@shared/schema";

neonConfig.webSocketConstructor = ws;
const pool = new Pool({ connectionString: process.env.DATABASE_URL });
const db = drizzle(pool);

function generateId(prefix: string): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 8);
  return `${prefix}-${timestamp}${random}`.toUpperCase();
}

export interface IStorage {
  // Users
  getUser(id: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;

  // Accounts
  getAccounts(): Promise<Account[]>;
  getAccount(id: string): Promise<Account | undefined>;
  createAccount(account: InsertAccount): Promise<Account>;
  updateAccount(id: string, account: Partial<InsertAccount>): Promise<Account | undefined>;
  deleteAccount(id: string): Promise<boolean>;

  // Contacts
  getContacts(): Promise<Contact[]>;
  getContact(id: string): Promise<Contact | undefined>;
  createContact(contact: InsertContact): Promise<Contact>;
  updateContact(id: string, contact: Partial<InsertContact>): Promise<Contact | undefined>;

  // Leads
  getLeads(): Promise<Lead[]>;
  getLead(id: string): Promise<Lead | undefined>;
  createLead(lead: InsertLead): Promise<Lead>;
  updateLead(id: string, lead: Partial<InsertLead>): Promise<Lead | undefined>;
  convertLead(id: string): Promise<{ contact: Contact; account: Account } | undefined>;

  // Opportunities
  getOpportunities(): Promise<Opportunity[]>;
  getOpportunity(id: string): Promise<Opportunity | undefined>;
  createOpportunity(opportunity: InsertOpportunity): Promise<Opportunity>;
  updateOpportunity(id: string, opportunity: Partial<InsertOpportunity>): Promise<Opportunity | undefined>;

  // Pipeline Stages
  getPipelineStages(): Promise<PipelineStage[]>;
  createPipelineStage(stage: InsertPipelineStage): Promise<PipelineStage>;

  // Campaigns
  getCampaigns(): Promise<Campaign[]>;
  createCampaign(campaign: InsertCampaign): Promise<Campaign>;
  updateCampaign(id: string, campaign: Partial<InsertCampaign>): Promise<Campaign | undefined>;

  // Tickets
  getTickets(): Promise<Ticket[]>;
  getTicket(id: string): Promise<Ticket | undefined>;
  createTicket(ticket: InsertTicket): Promise<Ticket>;
  updateTicket(id: string, ticket: Partial<InsertTicket>): Promise<Ticket | undefined>;
  getTicketComments(ticketId: string): Promise<TicketComment[]>;
  createTicketComment(comment: InsertTicketComment): Promise<TicketComment>;

  // Warehouses
  getWarehouses(): Promise<Warehouse[]>;
  createWarehouse(warehouse: InsertWarehouse): Promise<Warehouse>;

  // Products
  getProducts(): Promise<Product[]>;
  getProduct(id: string): Promise<Product | undefined>;
  createProduct(product: InsertProduct): Promise<Product>;
  updateProduct(id: string, product: Partial<InsertProduct>): Promise<Product | undefined>;

  // Stock Items
  getStockItems(): Promise<StockItem[]>;
  createStockItem(item: InsertStockItem): Promise<StockItem>;
  updateStockItem(id: string, item: Partial<InsertStockItem>): Promise<StockItem | undefined>;

  // Invoices
  getInvoices(): Promise<Invoice[]>;
  getInvoice(id: string): Promise<Invoice | undefined>;
  createInvoice(invoice: InsertInvoice): Promise<Invoice>;
  updateInvoice(id: string, invoice: Partial<InsertInvoice>): Promise<Invoice | undefined>;

  // Payments
  getPayments(): Promise<Payment[]>;
  createPayment(payment: InsertPayment): Promise<Payment>;

  // Employees
  getEmployees(): Promise<Employee[]>;
  getEmployee(id: string): Promise<Employee | undefined>;
  createEmployee(employee: InsertEmployee): Promise<Employee>;
  updateEmployee(id: string, employee: Partial<InsertEmployee>): Promise<Employee | undefined>;

  // Payroll
  getPayrollRecords(): Promise<PayrollRecord[]>;
  createPayrollRecord(record: InsertPayrollRecord): Promise<PayrollRecord>;

  // Leave Requests
  getLeaveRequests(): Promise<LeaveRequest[]>;
  createLeaveRequest(request: InsertLeaveRequest): Promise<LeaveRequest>;
  updateLeaveRequest(id: string, request: Partial<InsertLeaveRequest>): Promise<LeaveRequest | undefined>;

  // Sales Orders
  getSalesOrders(): Promise<SalesOrder[]>;
  getSalesOrder(id: string): Promise<SalesOrder | undefined>;
  createSalesOrder(order: InsertSalesOrder): Promise<SalesOrder>;
  updateSalesOrder(id: string, order: Partial<InsertSalesOrder>): Promise<SalesOrder | undefined>;

  // Purchase Orders
  getPurchaseOrders(): Promise<PurchaseOrder[]>;
  getPurchaseOrder(id: string): Promise<PurchaseOrder | undefined>;
  createPurchaseOrder(order: InsertPurchaseOrder): Promise<PurchaseOrder>;
  updatePurchaseOrder(id: string, order: Partial<InsertPurchaseOrder>): Promise<PurchaseOrder | undefined>;

  // Projects
  getProjects(): Promise<Project[]>;
  getProject(id: string): Promise<Project | undefined>;
  createProject(project: InsertProject): Promise<Project>;
  updateProject(id: string, project: Partial<InsertProject>): Promise<Project | undefined>;
  deleteProject(id: string): Promise<boolean>;

  // Transactions
  getTransactions(): Promise<Transaction[]>;
  getTransactionsByProject(projectId: string): Promise<Transaction[]>;
  createTransaction(transaction: InsertTransaction): Promise<Transaction>;

  // Equipment
  getEquipment(): Promise<Equipment[]>;
  getEquipmentById(id: string): Promise<Equipment | undefined>;
  createEquipment(item: InsertEquipment): Promise<Equipment>;
  updateEquipment(id: string, item: Partial<InsertEquipment>): Promise<Equipment | undefined>;

  // Safety Inspections
  getSafetyInspections(): Promise<SafetyInspection[]>;
  createSafetyInspection(inspection: InsertSafetyInspection): Promise<SafetyInspection>;

  // Clients
  getClients(): Promise<Client[]>;
  getClient(id: string): Promise<Client | undefined>;
  createClient(client: InsertClient): Promise<Client>;
  updateClient(id: string, client: Partial<InsertClient>): Promise<Client | undefined>;

  // Documents
  getDocuments(): Promise<Document[]>;
  getDocumentsByProject(projectId: string): Promise<Document[]>;
  createDocument(document: InsertDocument): Promise<Document>;

  // Dashboard Stats
  getDashboardStats(): Promise<any>;
}

export class DatabaseStorage implements IStorage {
  // ============================================================================
  // USERS
  // ============================================================================
  async getUser(id: string): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.id, id));
    return user;
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.username, username));
    return user;
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const [user] = await db.insert(users).values(insertUser).returning();
    return user;
  }

  // ============================================================================
  // ACCOUNTS
  // ============================================================================
  async getAccounts(): Promise<Account[]> {
    return await db.select().from(accounts).orderBy(desc(accounts.createdAt));
  }

  async getAccount(id: string): Promise<Account | undefined> {
    const [account] = await db.select().from(accounts).where(eq(accounts.id, id));
    return account;
  }

  async createAccount(account: InsertAccount): Promise<Account> {
    const [newAccount] = await db.insert(accounts).values(account).returning();
    return newAccount;
  }

  async updateAccount(id: string, account: Partial<InsertAccount>): Promise<Account | undefined> {
    const [updated] = await db.update(accounts).set({ ...account, updatedAt: new Date() }).where(eq(accounts.id, id)).returning();
    return updated;
  }

  async deleteAccount(id: string): Promise<boolean> {
    const result = await db.delete(accounts).where(eq(accounts.id, id));
    return result.rowCount ? result.rowCount > 0 : false;
  }

  // ============================================================================
  // CONTACTS
  // ============================================================================
  async getContacts(): Promise<Contact[]> {
    return await db.select().from(contacts).orderBy(desc(contacts.createdAt));
  }

  async getContact(id: string): Promise<Contact | undefined> {
    const [contact] = await db.select().from(contacts).where(eq(contacts.id, id));
    return contact;
  }

  async createContact(contact: InsertContact): Promise<Contact> {
    const [newContact] = await db.insert(contacts).values(contact).returning();
    return newContact;
  }

  async updateContact(id: string, contact: Partial<InsertContact>): Promise<Contact | undefined> {
    const [updated] = await db.update(contacts).set({ ...contact, updatedAt: new Date() }).where(eq(contacts.id, id)).returning();
    return updated;
  }

  // ============================================================================
  // LEADS
  // ============================================================================
  async getLeads(): Promise<Lead[]> {
    return await db.select().from(leads).orderBy(desc(leads.createdAt));
  }

  async getLead(id: string): Promise<Lead | undefined> {
    const [lead] = await db.select().from(leads).where(eq(leads.id, id));
    return lead;
  }

  async createLead(lead: InsertLead): Promise<Lead> {
    const [newLead] = await db.insert(leads).values(lead).returning();
    return newLead;
  }

  async updateLead(id: string, lead: Partial<InsertLead>): Promise<Lead | undefined> {
    const [updated] = await db.update(leads).set({ ...lead, updatedAt: new Date() }).where(eq(leads.id, id)).returning();
    return updated;
  }

  async convertLead(id: string): Promise<{ contact: Contact; account: Account } | undefined> {
    const lead = await this.getLead(id);
    if (!lead) return undefined;

    const [account] = await db.insert(accounts).values({
      name: lead.company || `${lead.firstName} ${lead.lastName}`,
      email: lead.email,
      phone: lead.phone,
      type: "customer",
      status: "active",
    }).returning();

    const [contact] = await db.insert(contacts).values({
      firstName: lead.firstName,
      lastName: lead.lastName,
      email: lead.email,
      phone: lead.phone,
      title: lead.title,
      accountId: account.id,
      status: "active",
      source: lead.source,
    }).returning();

    await db.update(leads).set({
      status: "converted",
      convertedAccountId: account.id,
      convertedContactId: contact.id,
      convertedAt: new Date(),
      updatedAt: new Date(),
    }).where(eq(leads.id, id));

    return { contact, account };
  }

  // ============================================================================
  // OPPORTUNITIES
  // ============================================================================
  async getOpportunities(): Promise<Opportunity[]> {
    return await db.select().from(opportunities).orderBy(desc(opportunities.createdAt));
  }

  async getOpportunity(id: string): Promise<Opportunity | undefined> {
    const [opportunity] = await db.select().from(opportunities).where(eq(opportunities.id, id));
    return opportunity;
  }

  async createOpportunity(opportunity: InsertOpportunity): Promise<Opportunity> {
    const [newOpportunity] = await db.insert(opportunities).values(opportunity).returning();
    return newOpportunity;
  }

  async updateOpportunity(id: string, opportunity: Partial<InsertOpportunity>): Promise<Opportunity | undefined> {
    const [updated] = await db.update(opportunities).set({ ...opportunity, updatedAt: new Date() }).where(eq(opportunities.id, id)).returning();
    return updated;
  }

  // ============================================================================
  // PIPELINE STAGES
  // ============================================================================
  async getPipelineStages(): Promise<PipelineStage[]> {
    return await db.select().from(pipelineStages).orderBy(pipelineStages.order);
  }

  async createPipelineStage(stage: InsertPipelineStage): Promise<PipelineStage> {
    const [newStage] = await db.insert(pipelineStages).values(stage).returning();
    return newStage;
  }

  // ============================================================================
  // CAMPAIGNS
  // ============================================================================
  async getCampaigns(): Promise<Campaign[]> {
    return await db.select().from(campaigns).orderBy(desc(campaigns.createdAt));
  }

  async createCampaign(campaign: InsertCampaign): Promise<Campaign> {
    const [newCampaign] = await db.insert(campaigns).values(campaign).returning();
    return newCampaign;
  }

  async updateCampaign(id: string, campaign: Partial<InsertCampaign>): Promise<Campaign | undefined> {
    const [updated] = await db.update(campaigns).set({ ...campaign, updatedAt: new Date() }).where(eq(campaigns.id, id)).returning();
    return updated;
  }

  // ============================================================================
  // TICKETS
  // ============================================================================
  async getTickets(): Promise<Ticket[]> {
    return await db.select().from(tickets).orderBy(desc(tickets.createdAt));
  }

  async getTicket(id: string): Promise<Ticket | undefined> {
    const [ticket] = await db.select().from(tickets).where(eq(tickets.id, id));
    return ticket;
  }

  async createTicket(ticket: InsertTicket): Promise<Ticket> {
    const ticketNumber = generateId("TKT");
    const [newTicket] = await db.insert(tickets).values({ ...ticket, ticketNumber }).returning();
    return newTicket;
  }

  async updateTicket(id: string, ticket: Partial<InsertTicket>): Promise<Ticket | undefined> {
    const updateData: any = { ...ticket, updatedAt: new Date() };
    if (ticket.status === "resolved" && !updateData.resolvedAt) {
      updateData.resolvedAt = new Date();
    }
    if (ticket.status === "closed" && !updateData.closedAt) {
      updateData.closedAt = new Date();
    }
    const [updated] = await db.update(tickets).set(updateData).where(eq(tickets.id, id)).returning();
    return updated;
  }

  async getTicketComments(ticketId: string): Promise<TicketComment[]> {
    return await db.select().from(ticketComments).where(eq(ticketComments.ticketId, ticketId)).orderBy(ticketComments.createdAt);
  }

  async createTicketComment(comment: InsertTicketComment): Promise<TicketComment> {
    const [newComment] = await db.insert(ticketComments).values(comment).returning();
    return newComment;
  }

  // ============================================================================
  // WAREHOUSES
  // ============================================================================
  async getWarehouses(): Promise<Warehouse[]> {
    return await db.select().from(warehouses).orderBy(warehouses.name);
  }

  async createWarehouse(warehouse: InsertWarehouse): Promise<Warehouse> {
    const [newWarehouse] = await db.insert(warehouses).values(warehouse).returning();
    return newWarehouse;
  }

  // ============================================================================
  // PRODUCTS
  // ============================================================================
  async getProducts(): Promise<Product[]> {
    return await db.select().from(products).orderBy(products.name);
  }

  async getProduct(id: string): Promise<Product | undefined> {
    const [product] = await db.select().from(products).where(eq(products.id, id));
    return product;
  }

  async createProduct(product: InsertProduct): Promise<Product> {
    const [newProduct] = await db.insert(products).values(product).returning();
    return newProduct;
  }

  async updateProduct(id: string, product: Partial<InsertProduct>): Promise<Product | undefined> {
    const [updated] = await db.update(products).set({ ...product, updatedAt: new Date() }).where(eq(products.id, id)).returning();
    return updated;
  }

  // ============================================================================
  // STOCK ITEMS
  // ============================================================================
  async getStockItems(): Promise<StockItem[]> {
    return await db.select().from(stockItems).orderBy(stockItems.createdAt);
  }

  async createStockItem(item: InsertStockItem): Promise<StockItem> {
    const [newItem] = await db.insert(stockItems).values({
      ...item,
      availableQuantity: (item.quantity || 0) - (item.reservedQuantity || 0),
    }).returning();
    return newItem;
  }

  async updateStockItem(id: string, item: Partial<InsertStockItem>): Promise<StockItem | undefined> {
    const current = await db.select().from(stockItems).where(eq(stockItems.id, id));
    if (!current.length) return undefined;
    
    const quantity = item.quantity ?? current[0].quantity;
    const reserved = item.reservedQuantity ?? current[0].reservedQuantity;
    
    const [updated] = await db.update(stockItems).set({
      ...item,
      availableQuantity: quantity - reserved,
      updatedAt: new Date(),
    }).where(eq(stockItems.id, id)).returning();
    return updated;
  }

  // ============================================================================
  // INVOICES
  // ============================================================================
  async getInvoices(): Promise<Invoice[]> {
    return await db.select().from(invoices).orderBy(desc(invoices.createdAt));
  }

  async getInvoice(id: string): Promise<Invoice | undefined> {
    const [invoice] = await db.select().from(invoices).where(eq(invoices.id, id));
    return invoice;
  }

  async createInvoice(invoice: InsertInvoice): Promise<Invoice> {
    const count = await db.select({ count: sql`count(*)` }).from(invoices);
    const invoiceNumber = `INV-${String(Number(count[0].count) + 1).padStart(6, "0")}`;
    const [newInvoice] = await db.insert(invoices).values({ ...invoice, invoiceNumber }).returning();
    return newInvoice;
  }

  async updateInvoice(id: string, invoice: Partial<InsertInvoice>): Promise<Invoice | undefined> {
    const [updated] = await db.update(invoices).set({ ...invoice, updatedAt: new Date() }).where(eq(invoices.id, id)).returning();
    return updated;
  }

  // ============================================================================
  // PAYMENTS
  // ============================================================================
  async getPayments(): Promise<Payment[]> {
    return await db.select().from(payments).orderBy(desc(payments.createdAt));
  }

  async createPayment(payment: InsertPayment): Promise<Payment> {
    const count = await db.select({ count: sql`count(*)` }).from(payments);
    const paymentNumber = `PAY-${String(Number(count[0].count) + 1).padStart(6, "0")}`;
    const [newPayment] = await db.insert(payments).values({ ...payment, paymentNumber }).returning();
    
    if (payment.invoiceId) {
      const invoice = await this.getInvoice(payment.invoiceId);
      if (invoice) {
        const newPaidAmount = parseFloat(invoice.paidAmount || "0") + parseFloat(payment.amount);
        const newStatus = newPaidAmount >= parseFloat(invoice.totalAmount) ? "paid" : "partial";
        await this.updateInvoice(payment.invoiceId, { 
          paidAmount: String(newPaidAmount),
          status: newStatus,
        });
      }
    }
    
    return newPayment;
  }

  // ============================================================================
  // EMPLOYEES
  // ============================================================================
  async getEmployees(): Promise<Employee[]> {
    return await db.select().from(employees).orderBy(employees.lastName);
  }

  async getEmployee(id: string): Promise<Employee | undefined> {
    const [employee] = await db.select().from(employees).where(eq(employees.id, id));
    return employee;
  }

  async createEmployee(employee: InsertEmployee): Promise<Employee> {
    const count = await db.select({ count: sql`count(*)` }).from(employees);
    const employeeNumber = `EMP-${String(Number(count[0].count) + 1).padStart(5, "0")}`;
    const [newEmployee] = await db.insert(employees).values({ ...employee, employeeNumber }).returning();
    return newEmployee;
  }

  async updateEmployee(id: string, employee: Partial<InsertEmployee>): Promise<Employee | undefined> {
    const [updated] = await db.update(employees).set({ ...employee, updatedAt: new Date() }).where(eq(employees.id, id)).returning();
    return updated;
  }

  // ============================================================================
  // PAYROLL
  // ============================================================================
  async getPayrollRecords(): Promise<PayrollRecord[]> {
    return await db.select().from(payrollRecords).orderBy(desc(payrollRecords.periodEnd));
  }

  async createPayrollRecord(record: InsertPayrollRecord): Promise<PayrollRecord> {
    const [newRecord] = await db.insert(payrollRecords).values(record).returning();
    return newRecord;
  }

  // ============================================================================
  // LEAVE REQUESTS
  // ============================================================================
  async getLeaveRequests(): Promise<LeaveRequest[]> {
    return await db.select().from(leaveRequests).orderBy(desc(leaveRequests.createdAt));
  }

  async createLeaveRequest(request: InsertLeaveRequest): Promise<LeaveRequest> {
    const [newRequest] = await db.insert(leaveRequests).values(request).returning();
    return newRequest;
  }

  async updateLeaveRequest(id: string, request: Partial<InsertLeaveRequest>): Promise<LeaveRequest | undefined> {
    const updateData: any = { ...request, updatedAt: new Date() };
    if (request.status === "approved" && !updateData.approvedAt) {
      updateData.approvedAt = new Date();
    }
    const [updated] = await db.update(leaveRequests).set(updateData).where(eq(leaveRequests.id, id)).returning();
    return updated;
  }

  // ============================================================================
  // SALES ORDERS
  // ============================================================================
  async getSalesOrders(): Promise<SalesOrder[]> {
    return await db.select().from(salesOrders).orderBy(desc(salesOrders.createdAt));
  }

  async getSalesOrder(id: string): Promise<SalesOrder | undefined> {
    const [order] = await db.select().from(salesOrders).where(eq(salesOrders.id, id));
    return order;
  }

  async createSalesOrder(order: InsertSalesOrder): Promise<SalesOrder> {
    const count = await db.select({ count: sql`count(*)` }).from(salesOrders);
    const orderNumber = `SO-${String(Number(count[0].count) + 1).padStart(6, "0")}`;
    const [newOrder] = await db.insert(salesOrders).values({ ...order, orderNumber }).returning();
    return newOrder;
  }

  async updateSalesOrder(id: string, order: Partial<InsertSalesOrder>): Promise<SalesOrder | undefined> {
    const [updated] = await db.update(salesOrders).set({ ...order, updatedAt: new Date() }).where(eq(salesOrders.id, id)).returning();
    return updated;
  }

  // ============================================================================
  // PURCHASE ORDERS
  // ============================================================================
  async getPurchaseOrders(): Promise<PurchaseOrder[]> {
    return await db.select().from(purchaseOrders).orderBy(desc(purchaseOrders.createdAt));
  }

  async getPurchaseOrder(id: string): Promise<PurchaseOrder | undefined> {
    const [order] = await db.select().from(purchaseOrders).where(eq(purchaseOrders.id, id));
    return order;
  }

  async createPurchaseOrder(order: InsertPurchaseOrder): Promise<PurchaseOrder> {
    const count = await db.select({ count: sql`count(*)` }).from(purchaseOrders);
    const orderNumber = `PO-${String(Number(count[0].count) + 1).padStart(6, "0")}`;
    const [newOrder] = await db.insert(purchaseOrders).values({ ...order, orderNumber }).returning();
    return newOrder;
  }

  async updatePurchaseOrder(id: string, order: Partial<InsertPurchaseOrder>): Promise<PurchaseOrder | undefined> {
    const updateData: any = { ...order, updatedAt: new Date() };
    if (order.status === "approved" && !updateData.approvedAt) {
      updateData.approvedAt = new Date();
    }
    const [updated] = await db.update(purchaseOrders).set(updateData).where(eq(purchaseOrders.id, id)).returning();
    return updated;
  }

  // ============================================================================
  // PROJECTS (Construction)
  // ============================================================================
  async getProjects(): Promise<Project[]> {
    return await db.select().from(projects).orderBy(desc(projects.createdAt));
  }

  async getProject(id: string): Promise<Project | undefined> {
    const [project] = await db.select().from(projects).where(eq(projects.id, id));
    return project;
  }

  async createProject(project: InsertProject): Promise<Project> {
    const id = `PRJ-${String(Date.now()).slice(-6)}`;
    const [newProject] = await db.insert(projects).values({ id, ...project }).returning();
    return newProject;
  }

  async updateProject(id: string, project: Partial<InsertProject>): Promise<Project | undefined> {
    const [updated] = await db.update(projects).set({ ...project, updatedAt: new Date() }).where(eq(projects.id, id)).returning();
    return updated;
  }

  async deleteProject(id: string): Promise<boolean> {
    const result = await db.delete(projects).where(eq(projects.id, id));
    return result.rowCount ? result.rowCount > 0 : false;
  }

  // ============================================================================
  // TRANSACTIONS
  // ============================================================================
  async getTransactions(): Promise<Transaction[]> {
    return await db.select().from(transactions).orderBy(desc(transactions.date));
  }

  async getTransactionsByProject(projectId: string): Promise<Transaction[]> {
    return await db.select().from(transactions).where(eq(transactions.projectId, projectId));
  }

  async createTransaction(transaction: InsertTransaction): Promise<Transaction> {
    const [newTransaction] = await db.insert(transactions).values(transaction).returning();
    return newTransaction;
  }

  // ============================================================================
  // EQUIPMENT
  // ============================================================================
  async getEquipment(): Promise<Equipment[]> {
    return await db.select().from(equipment).orderBy(equipment.name);
  }

  async getEquipmentById(id: string): Promise<Equipment | undefined> {
    const [item] = await db.select().from(equipment).where(eq(equipment.id, id));
    return item;
  }

  async createEquipment(item: InsertEquipment): Promise<Equipment> {
    const id = `EQ-${String(Date.now()).slice(-6)}`;
    const [newEquipment] = await db.insert(equipment).values({ id, ...item }).returning();
    return newEquipment;
  }

  async updateEquipment(id: string, item: Partial<InsertEquipment>): Promise<Equipment | undefined> {
    const [updated] = await db.update(equipment).set({ ...item, updatedAt: new Date() }).where(eq(equipment.id, id)).returning();
    return updated;
  }

  // ============================================================================
  // SAFETY INSPECTIONS
  // ============================================================================
  async getSafetyInspections(): Promise<SafetyInspection[]> {
    return await db.select().from(safetyInspections).orderBy(desc(safetyInspections.date));
  }

  async createSafetyInspection(inspection: InsertSafetyInspection): Promise<SafetyInspection> {
    const [newInspection] = await db.insert(safetyInspections).values(inspection).returning();
    return newInspection;
  }

  // ============================================================================
  // CLIENTS
  // ============================================================================
  async getClients(): Promise<Client[]> {
    return await db.select().from(clients).orderBy(desc(clients.createdAt));
  }

  async getClient(id: string): Promise<Client | undefined> {
    const [client] = await db.select().from(clients).where(eq(clients.id, id));
    return client;
  }

  async createClient(client: InsertClient): Promise<Client> {
    const [newClient] = await db.insert(clients).values(client).returning();
    return newClient;
  }

  async updateClient(id: string, client: Partial<InsertClient>): Promise<Client | undefined> {
    const [updated] = await db.update(clients).set({ ...client, updatedAt: new Date() }).where(eq(clients.id, id)).returning();
    return updated;
  }

  // ============================================================================
  // DOCUMENTS
  // ============================================================================
  async getDocuments(): Promise<Document[]> {
    return await db.select().from(documents).orderBy(desc(documents.uploadedAt));
  }

  async getDocumentsByProject(projectId: string): Promise<Document[]> {
    return await db.select().from(documents).where(eq(documents.projectId, projectId));
  }

  async createDocument(document: InsertDocument): Promise<Document> {
    const [newDocument] = await db.insert(documents).values(document).returning();
    return newDocument;
  }

  // ============================================================================
  // DASHBOARD STATS
  // ============================================================================
  async getDashboardStats(): Promise<any> {
    const [projectStats] = await db.select({
      total: sql`count(*)`,
      inProgress: sql`count(*) filter (where status = 'In Progress')`,
      completed: sql`count(*) filter (where status = 'Completed')`,
      totalBudget: sql`coalesce(sum(budget::numeric), 0)`,
    }).from(projects);

    const [transactionStats] = await db.select({
      totalRevenue: sql`coalesce(sum(amount::numeric) filter (where type = 'income'), 0)`,
      totalExpenses: sql`coalesce(sum(amount::numeric) filter (where type = 'expense' or type is null), 0)`,
    }).from(transactions);

    const [clientStats] = await db.select({
      total: sql`count(*)`,
      active: sql`count(*) filter (where status = 'Active' or status = 'Contract Signed')`,
    }).from(clients);

    const [leadStats] = await db.select({
      total: sql`count(*)`,
      newLeads: sql`count(*) filter (where status = 'new')`,
      converted: sql`count(*) filter (where status = 'converted')`,
    }).from(leads);

    const [ticketStats] = await db.select({
      total: sql`count(*)`,
      open: sql`count(*) filter (where status = 'open' or status = 'in_progress')`,
      resolved: sql`count(*) filter (where status = 'resolved' or status = 'closed')`,
    }).from(tickets);

    const [employeeStats] = await db.select({
      total: sql`count(*)`,
      active: sql`count(*) filter (where status = 'active')`,
    }).from(employees);

    return {
      projects: projectStats,
      transactions: transactionStats,
      clients: clientStats,
      leads: leadStats,
      tickets: ticketStats,
      employees: employeeStats,
    };
  }
}

export const storage = new DatabaseStorage();
