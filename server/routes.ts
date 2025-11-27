import type { Express, Request, Response, NextFunction } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { seedDatabase } from "./seed";
import v1Routes from "./routes/v1";
import {
  insertProjectSchema,
  insertTransactionSchema,
  insertEquipmentSchema,
  insertSafetyInspectionSchema,
  insertClientSchema,
  insertDocumentSchema,
  insertAccountSchema,
  insertContactSchema,
  insertAddressSchema,
  insertLeadSchema,
  insertOpportunitySchema,
  insertPipelineStageSchema,
  insertCampaignSchema,
  insertMailingListSchema,
  insertSegmentSchema,
  insertTicketSchema,
  insertTicketCommentSchema,
  insertSlaSchema,
  insertWarehouseSchema,
  insertProductSchema,
  insertStockItemSchema,
  insertInvoiceSchema,
  insertPaymentSchema,
  insertEmployeeSchema,
  insertPayrollRecordSchema,
  insertLeaveRequestSchema,
  insertSalesOrderSchema,
  insertPurchaseOrderSchema,
} from "@shared/schema";

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
      console.log(`[API] ${log.method} ${log.path} ${log.statusCode} ${log.duration}ms`);
    }
  });

  next();
};

export async function registerRoutes(app: Express): Promise<Server> {
  app.use(requestLogger);

  if (process.env.NODE_ENV === "development") {
    await seedDatabase().catch(console.error);
  }

  app.use("/api/v1", v1Routes);

  // ============================================================================
  // CRM: ACCOUNTS API
  // ============================================================================
  app.get("/api/v1/accounts", async (req, res) => {
    try {
      const accounts = await storage.getAccounts();
      res.json(accounts);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch accounts" });
    }
  });

  app.get("/api/v1/accounts/:id", async (req, res) => {
    try {
      const account = await storage.getAccount(req.params.id);
      if (!account) return res.status(404).json({ error: "Account not found" });
      res.json(account);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch account" });
    }
  });

  app.post("/api/v1/accounts", async (req, res) => {
    try {
      const validated = insertAccountSchema.parse(req.body);
      const account = await storage.createAccount(validated);
      res.status(201).json(account);
    } catch (error) {
      res.status(400).json({ error: "Invalid account data" });
    }
  });

  app.patch("/api/v1/accounts/:id", async (req, res) => {
    try {
      const account = await storage.updateAccount(req.params.id, req.body);
      if (!account) return res.status(404).json({ error: "Account not found" });
      res.json(account);
    } catch (error) {
      res.status(400).json({ error: "Failed to update account" });
    }
  });

  app.delete("/api/v1/accounts/:id", async (req, res) => {
    try {
      const success = await storage.deleteAccount(req.params.id);
      if (!success) return res.status(404).json({ error: "Account not found" });
      res.status(204).send();
    } catch (error) {
      res.status(500).json({ error: "Failed to delete account" });
    }
  });

  // ============================================================================
  // CRM: CONTACTS API
  // ============================================================================
  app.get("/api/v1/contacts", async (req, res) => {
    try {
      const contacts = await storage.getContacts();
      res.json(contacts);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch contacts" });
    }
  });

  app.get("/api/v1/contacts/:id", async (req, res) => {
    try {
      const contact = await storage.getContact(req.params.id);
      if (!contact) return res.status(404).json({ error: "Contact not found" });
      res.json(contact);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch contact" });
    }
  });

  app.post("/api/v1/contacts", async (req, res) => {
    try {
      const validated = insertContactSchema.parse(req.body);
      const contact = await storage.createContact(validated);
      res.status(201).json(contact);
    } catch (error) {
      res.status(400).json({ error: "Invalid contact data" });
    }
  });

  app.patch("/api/v1/contacts/:id", async (req, res) => {
    try {
      const contact = await storage.updateContact(req.params.id, req.body);
      if (!contact) return res.status(404).json({ error: "Contact not found" });
      res.json(contact);
    } catch (error) {
      res.status(400).json({ error: "Failed to update contact" });
    }
  });

  // ============================================================================
  // CRM: LEADS API
  // ============================================================================
  app.get("/api/v1/leads", async (req, res) => {
    try {
      const leads = await storage.getLeads();
      res.json(leads);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch leads" });
    }
  });

  app.get("/api/v1/leads/:id", async (req, res) => {
    try {
      const lead = await storage.getLead(req.params.id);
      if (!lead) return res.status(404).json({ error: "Lead not found" });
      res.json(lead);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch lead" });
    }
  });

  app.post("/api/v1/leads", async (req, res) => {
    try {
      const validated = insertLeadSchema.parse(req.body);
      const lead = await storage.createLead(validated);
      res.status(201).json(lead);
    } catch (error) {
      res.status(400).json({ error: "Invalid lead data" });
    }
  });

  app.patch("/api/v1/leads/:id", async (req, res) => {
    try {
      const lead = await storage.updateLead(req.params.id, req.body);
      if (!lead) return res.status(404).json({ error: "Lead not found" });
      res.json(lead);
    } catch (error) {
      res.status(400).json({ error: "Failed to update lead" });
    }
  });

  app.post("/api/v1/leads/:id/convert", async (req, res) => {
    try {
      const result = await storage.convertLead(req.params.id);
      if (!result) return res.status(404).json({ error: "Lead not found" });
      res.json(result);
    } catch (error) {
      res.status(500).json({ error: "Failed to convert lead" });
    }
  });

  // ============================================================================
  // CRM: OPPORTUNITIES API
  // ============================================================================
  app.get("/api/v1/opportunities", async (req, res) => {
    try {
      const opportunities = await storage.getOpportunities();
      res.json(opportunities);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch opportunities" });
    }
  });

  app.get("/api/v1/opportunities/:id", async (req, res) => {
    try {
      const opportunity = await storage.getOpportunity(req.params.id);
      if (!opportunity) return res.status(404).json({ error: "Opportunity not found" });
      res.json(opportunity);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch opportunity" });
    }
  });

  app.post("/api/v1/opportunities", async (req, res) => {
    try {
      const validated = insertOpportunitySchema.parse(req.body);
      const opportunity = await storage.createOpportunity(validated);
      res.status(201).json(opportunity);
    } catch (error) {
      res.status(400).json({ error: "Invalid opportunity data" });
    }
  });

  app.patch("/api/v1/opportunities/:id", async (req, res) => {
    try {
      const opportunity = await storage.updateOpportunity(req.params.id, req.body);
      if (!opportunity) return res.status(404).json({ error: "Opportunity not found" });
      res.json(opportunity);
    } catch (error) {
      res.status(400).json({ error: "Failed to update opportunity" });
    }
  });

  // ============================================================================
  // CRM: PIPELINE STAGES API
  // ============================================================================
  app.get("/api/v1/pipeline-stages", async (req, res) => {
    try {
      const stages = await storage.getPipelineStages();
      res.json(stages);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch pipeline stages" });
    }
  });

  app.post("/api/v1/pipeline-stages", async (req, res) => {
    try {
      const validated = insertPipelineStageSchema.parse(req.body);
      const stage = await storage.createPipelineStage(validated);
      res.status(201).json(stage);
    } catch (error) {
      res.status(400).json({ error: "Invalid pipeline stage data" });
    }
  });

  // ============================================================================
  // CRM: CAMPAIGNS API
  // ============================================================================
  app.get("/api/v1/campaigns", async (req, res) => {
    try {
      const campaigns = await storage.getCampaigns();
      res.json(campaigns);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch campaigns" });
    }
  });

  app.post("/api/v1/campaigns", async (req, res) => {
    try {
      const validated = insertCampaignSchema.parse(req.body);
      const campaign = await storage.createCampaign(validated);
      res.status(201).json(campaign);
    } catch (error) {
      res.status(400).json({ error: "Invalid campaign data" });
    }
  });

  app.patch("/api/v1/campaigns/:id", async (req, res) => {
    try {
      const campaign = await storage.updateCampaign(req.params.id, req.body);
      if (!campaign) return res.status(404).json({ error: "Campaign not found" });
      res.json(campaign);
    } catch (error) {
      res.status(400).json({ error: "Failed to update campaign" });
    }
  });

  // ============================================================================
  // CRM: SUPPORT TICKETS API
  // ============================================================================
  app.get("/api/v1/tickets", async (req, res) => {
    try {
      const tickets = await storage.getTickets();
      res.json(tickets);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch tickets" });
    }
  });

  app.get("/api/v1/tickets/:id", async (req, res) => {
    try {
      const ticket = await storage.getTicket(req.params.id);
      if (!ticket) return res.status(404).json({ error: "Ticket not found" });
      res.json(ticket);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch ticket" });
    }
  });

  app.post("/api/v1/tickets", async (req, res) => {
    try {
      const validated = insertTicketSchema.parse(req.body);
      const ticket = await storage.createTicket(validated);
      res.status(201).json(ticket);
    } catch (error) {
      res.status(400).json({ error: "Invalid ticket data" });
    }
  });

  app.patch("/api/v1/tickets/:id", async (req, res) => {
    try {
      const ticket = await storage.updateTicket(req.params.id, req.body);
      if (!ticket) return res.status(404).json({ error: "Ticket not found" });
      res.json(ticket);
    } catch (error) {
      res.status(400).json({ error: "Failed to update ticket" });
    }
  });

  app.get("/api/v1/tickets/:id/comments", async (req, res) => {
    try {
      const comments = await storage.getTicketComments(req.params.id);
      res.json(comments);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch comments" });
    }
  });

  app.post("/api/v1/tickets/:id/comments", async (req, res) => {
    try {
      const validated = insertTicketCommentSchema.parse({ ...req.body, ticketId: req.params.id });
      const comment = await storage.createTicketComment(validated);
      res.status(201).json(comment);
    } catch (error) {
      res.status(400).json({ error: "Invalid comment data" });
    }
  });

  // ============================================================================
  // ERP: WAREHOUSES API
  // ============================================================================
  app.get("/api/v1/warehouses", async (req, res) => {
    try {
      const warehouses = await storage.getWarehouses();
      res.json(warehouses);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch warehouses" });
    }
  });

  app.post("/api/v1/warehouses", async (req, res) => {
    try {
      const validated = insertWarehouseSchema.parse(req.body);
      const warehouse = await storage.createWarehouse(validated);
      res.status(201).json(warehouse);
    } catch (error) {
      res.status(400).json({ error: "Invalid warehouse data" });
    }
  });

  // ============================================================================
  // ERP: PRODUCTS API
  // ============================================================================
  app.get("/api/v1/products", async (req, res) => {
    try {
      const products = await storage.getProducts();
      res.json(products);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch products" });
    }
  });

  app.get("/api/v1/products/:id", async (req, res) => {
    try {
      const product = await storage.getProduct(req.params.id);
      if (!product) return res.status(404).json({ error: "Product not found" });
      res.json(product);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch product" });
    }
  });

  app.post("/api/v1/products", async (req, res) => {
    try {
      const validated = insertProductSchema.parse(req.body);
      const product = await storage.createProduct(validated);
      res.status(201).json(product);
    } catch (error) {
      res.status(400).json({ error: "Invalid product data" });
    }
  });

  app.patch("/api/v1/products/:id", async (req, res) => {
    try {
      const product = await storage.updateProduct(req.params.id, req.body);
      if (!product) return res.status(404).json({ error: "Product not found" });
      res.json(product);
    } catch (error) {
      res.status(400).json({ error: "Failed to update product" });
    }
  });

  // ============================================================================
  // ERP: STOCK ITEMS API
  // ============================================================================
  app.get("/api/v1/stock", async (req, res) => {
    try {
      const stock = await storage.getStockItems();
      res.json(stock);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch stock items" });
    }
  });

  app.post("/api/v1/stock", async (req, res) => {
    try {
      const validated = insertStockItemSchema.parse(req.body);
      const item = await storage.createStockItem(validated);
      res.status(201).json(item);
    } catch (error) {
      res.status(400).json({ error: "Invalid stock item data" });
    }
  });

  app.patch("/api/v1/stock/:id", async (req, res) => {
    try {
      const item = await storage.updateStockItem(req.params.id, req.body);
      if (!item) return res.status(404).json({ error: "Stock item not found" });
      res.json(item);
    } catch (error) {
      res.status(400).json({ error: "Failed to update stock item" });
    }
  });

  // ============================================================================
  // ERP: INVOICES API
  // ============================================================================
  app.get("/api/v1/invoices", async (req, res) => {
    try {
      const invoices = await storage.getInvoices();
      res.json(invoices);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch invoices" });
    }
  });

  app.get("/api/v1/invoices/:id", async (req, res) => {
    try {
      const invoice = await storage.getInvoice(req.params.id);
      if (!invoice) return res.status(404).json({ error: "Invoice not found" });
      res.json(invoice);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch invoice" });
    }
  });

  app.post("/api/v1/invoices", async (req, res) => {
    try {
      const validated = insertInvoiceSchema.parse(req.body);
      const invoice = await storage.createInvoice(validated);
      res.status(201).json(invoice);
    } catch (error) {
      res.status(400).json({ error: "Invalid invoice data" });
    }
  });

  app.patch("/api/v1/invoices/:id", async (req, res) => {
    try {
      const invoice = await storage.updateInvoice(req.params.id, req.body);
      if (!invoice) return res.status(404).json({ error: "Invoice not found" });
      res.json(invoice);
    } catch (error) {
      res.status(400).json({ error: "Failed to update invoice" });
    }
  });

  // ============================================================================
  // ERP: PAYMENTS API
  // ============================================================================
  app.get("/api/v1/payments", async (req, res) => {
    try {
      const payments = await storage.getPayments();
      res.json(payments);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch payments" });
    }
  });

  app.post("/api/v1/payments", async (req, res) => {
    try {
      const validated = insertPaymentSchema.parse(req.body);
      const payment = await storage.createPayment(validated);
      res.status(201).json(payment);
    } catch (error) {
      res.status(400).json({ error: "Invalid payment data" });
    }
  });

  // ============================================================================
  // ERP: EMPLOYEES API
  // ============================================================================
  app.get("/api/v1/employees", async (req, res) => {
    try {
      const employees = await storage.getEmployees();
      res.json(employees);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch employees" });
    }
  });

  app.get("/api/v1/employees/:id", async (req, res) => {
    try {
      const employee = await storage.getEmployee(req.params.id);
      if (!employee) return res.status(404).json({ error: "Employee not found" });
      res.json(employee);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch employee" });
    }
  });

  app.post("/api/v1/employees", async (req, res) => {
    try {
      const validated = insertEmployeeSchema.parse(req.body);
      const employee = await storage.createEmployee(validated);
      res.status(201).json(employee);
    } catch (error) {
      res.status(400).json({ error: "Invalid employee data" });
    }
  });

  app.patch("/api/v1/employees/:id", async (req, res) => {
    try {
      const employee = await storage.updateEmployee(req.params.id, req.body);
      if (!employee) return res.status(404).json({ error: "Employee not found" });
      res.json(employee);
    } catch (error) {
      res.status(400).json({ error: "Failed to update employee" });
    }
  });

  // ============================================================================
  // ERP: PAYROLL API
  // ============================================================================
  app.get("/api/v1/payroll", async (req, res) => {
    try {
      const records = await storage.getPayrollRecords();
      res.json(records);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch payroll records" });
    }
  });

  app.post("/api/v1/payroll", async (req, res) => {
    try {
      const validated = insertPayrollRecordSchema.parse(req.body);
      const record = await storage.createPayrollRecord(validated);
      res.status(201).json(record);
    } catch (error) {
      res.status(400).json({ error: "Invalid payroll data" });
    }
  });

  // ============================================================================
  // ERP: LEAVE REQUESTS API
  // ============================================================================
  app.get("/api/v1/leave-requests", async (req, res) => {
    try {
      const requests = await storage.getLeaveRequests();
      res.json(requests);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch leave requests" });
    }
  });

  app.post("/api/v1/leave-requests", async (req, res) => {
    try {
      const validated = insertLeaveRequestSchema.parse(req.body);
      const request = await storage.createLeaveRequest(validated);
      res.status(201).json(request);
    } catch (error) {
      res.status(400).json({ error: "Invalid leave request data" });
    }
  });

  app.patch("/api/v1/leave-requests/:id", async (req, res) => {
    try {
      const request = await storage.updateLeaveRequest(req.params.id, req.body);
      if (!request) return res.status(404).json({ error: "Leave request not found" });
      res.json(request);
    } catch (error) {
      res.status(400).json({ error: "Failed to update leave request" });
    }
  });

  // ============================================================================
  // ERP: SALES ORDERS API
  // ============================================================================
  app.get("/api/v1/sales-orders", async (req, res) => {
    try {
      const orders = await storage.getSalesOrders();
      res.json(orders);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch sales orders" });
    }
  });

  app.get("/api/v1/sales-orders/:id", async (req, res) => {
    try {
      const order = await storage.getSalesOrder(req.params.id);
      if (!order) return res.status(404).json({ error: "Sales order not found" });
      res.json(order);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch sales order" });
    }
  });

  app.post("/api/v1/sales-orders", async (req, res) => {
    try {
      const validated = insertSalesOrderSchema.parse(req.body);
      const order = await storage.createSalesOrder(validated);
      res.status(201).json(order);
    } catch (error) {
      res.status(400).json({ error: "Invalid sales order data" });
    }
  });

  app.patch("/api/v1/sales-orders/:id", async (req, res) => {
    try {
      const order = await storage.updateSalesOrder(req.params.id, req.body);
      if (!order) return res.status(404).json({ error: "Sales order not found" });
      res.json(order);
    } catch (error) {
      res.status(400).json({ error: "Failed to update sales order" });
    }
  });

  // ============================================================================
  // ERP: PURCHASE ORDERS API
  // ============================================================================
  app.get("/api/v1/purchase-orders", async (req, res) => {
    try {
      const orders = await storage.getPurchaseOrders();
      res.json(orders);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch purchase orders" });
    }
  });

  app.get("/api/v1/purchase-orders/:id", async (req, res) => {
    try {
      const order = await storage.getPurchaseOrder(req.params.id);
      if (!order) return res.status(404).json({ error: "Purchase order not found" });
      res.json(order);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch purchase order" });
    }
  });

  app.post("/api/v1/purchase-orders", async (req, res) => {
    try {
      const validated = insertPurchaseOrderSchema.parse(req.body);
      const order = await storage.createPurchaseOrder(validated);
      res.status(201).json(order);
    } catch (error) {
      res.status(400).json({ error: "Invalid purchase order data" });
    }
  });

  app.patch("/api/v1/purchase-orders/:id", async (req, res) => {
    try {
      const order = await storage.updatePurchaseOrder(req.params.id, req.body);
      if (!order) return res.status(404).json({ error: "Purchase order not found" });
      res.json(order);
    } catch (error) {
      res.status(400).json({ error: "Failed to update purchase order" });
    }
  });

  // ============================================================================
  // CONSTRUCTION: PROJECTS API (Legacy compatibility)
  // ============================================================================
  app.get("/api/v1/projects", async (req, res) => {
    try {
      const projects = await storage.getProjects();
      res.json(projects);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch projects" });
    }
  });

  app.get("/api/v1/projects/:id", async (req, res) => {
    try {
      const project = await storage.getProject(req.params.id);
      if (!project) return res.status(404).json({ error: "Project not found" });
      res.json(project);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch project" });
    }
  });

  app.post("/api/v1/projects", async (req, res) => {
    try {
      const validated = insertProjectSchema.parse(req.body);
      const project = await storage.createProject(validated);
      res.status(201).json(project);
    } catch (error) {
      res.status(400).json({ error: "Invalid project data" });
    }
  });

  app.patch("/api/v1/projects/:id", async (req, res) => {
    try {
      const project = await storage.updateProject(req.params.id, req.body);
      if (!project) return res.status(404).json({ error: "Project not found" });
      res.json(project);
    } catch (error) {
      res.status(400).json({ error: "Failed to update project" });
    }
  });

  app.delete("/api/v1/projects/:id", async (req, res) => {
    try {
      const success = await storage.deleteProject(req.params.id);
      if (!success) return res.status(404).json({ error: "Project not found" });
      res.status(204).send();
    } catch (error) {
      res.status(500).json({ error: "Failed to delete project" });
    }
  });

  // ============================================================================
  // CONSTRUCTION: TRANSACTIONS API
  // ============================================================================
  app.get("/api/v1/transactions", async (req, res) => {
    try {
      const transactions = await storage.getTransactions();
      res.json(transactions);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch transactions" });
    }
  });

  app.post("/api/v1/transactions", async (req, res) => {
    try {
      const validated = insertTransactionSchema.parse(req.body);
      const transaction = await storage.createTransaction(validated);
      res.status(201).json(transaction);
    } catch (error) {
      res.status(400).json({ error: "Invalid transaction data" });
    }
  });

  // ============================================================================
  // CONSTRUCTION: EQUIPMENT API
  // ============================================================================
  app.get("/api/v1/equipment", async (req, res) => {
    try {
      const equipmentList = await storage.getEquipment();
      res.json(equipmentList);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch equipment" });
    }
  });

  app.post("/api/v1/equipment", async (req, res) => {
    try {
      const validated = insertEquipmentSchema.parse(req.body);
      const item = await storage.createEquipment(validated);
      res.status(201).json(item);
    } catch (error) {
      res.status(400).json({ error: "Invalid equipment data" });
    }
  });

  app.patch("/api/v1/equipment/:id", async (req, res) => {
    try {
      const item = await storage.updateEquipment(req.params.id, req.body);
      if (!item) return res.status(404).json({ error: "Equipment not found" });
      res.json(item);
    } catch (error) {
      res.status(400).json({ error: "Failed to update equipment" });
    }
  });

  // ============================================================================
  // CONSTRUCTION: SAFETY INSPECTIONS API
  // ============================================================================
  app.get("/api/v1/safety/inspections", async (req, res) => {
    try {
      const inspections = await storage.getSafetyInspections();
      res.json(inspections);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch inspections" });
    }
  });

  app.post("/api/v1/safety/inspections", async (req, res) => {
    try {
      const validated = insertSafetyInspectionSchema.parse(req.body);
      const inspection = await storage.createSafetyInspection(validated);
      res.status(201).json(inspection);
    } catch (error) {
      res.status(400).json({ error: "Invalid inspection data" });
    }
  });

  // ============================================================================
  // CONSTRUCTION: CLIENTS API (Legacy)
  // ============================================================================
  app.get("/api/v1/clients", async (req, res) => {
    try {
      const clientsList = await storage.getClients();
      res.json(clientsList);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch clients" });
    }
  });

  app.post("/api/v1/clients", async (req, res) => {
    try {
      const validated = insertClientSchema.parse(req.body);
      const client = await storage.createClient(validated);
      res.status(201).json(client);
    } catch (error) {
      res.status(400).json({ error: "Invalid client data" });
    }
  });

  app.patch("/api/v1/clients/:id", async (req, res) => {
    try {
      const client = await storage.updateClient(req.params.id, req.body);
      if (!client) return res.status(404).json({ error: "Client not found" });
      res.json(client);
    } catch (error) {
      res.status(400).json({ error: "Failed to update client" });
    }
  });

  // ============================================================================
  // CONSTRUCTION: DOCUMENTS API
  // ============================================================================
  app.get("/api/v1/documents", async (req, res) => {
    try {
      const docs = await storage.getDocuments();
      res.json(docs);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch documents" });
    }
  });

  app.post("/api/v1/documents", async (req, res) => {
    try {
      const validated = insertDocumentSchema.parse(req.body);
      const document = await storage.createDocument(validated);
      res.status(201).json(document);
    } catch (error) {
      res.status(400).json({ error: "Invalid document data" });
    }
  });

  // ============================================================================
  // ANALYTICS: DASHBOARD STATS
  // ============================================================================
  app.get("/api/v1/analytics/dashboard", async (req, res) => {
    try {
      const stats = await storage.getDashboardStats();
      res.json(stats);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch dashboard stats" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
