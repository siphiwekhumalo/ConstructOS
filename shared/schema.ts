import { sql } from "drizzle-orm";
import { pgTable, text, varchar, integer, decimal, timestamp, uuid, boolean, date } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// ============================================================================
// CORE AUTHENTICATION & USERS
// ============================================================================

export const users = pgTable("users", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  username: text("username").notNull().unique(),
  email: text("email").notNull().unique(),
  password: text("password").notNull(),
  firstName: text("first_name"),
  lastName: text("last_name"),
  role: text("role").notNull().default("user"),
  department: text("department"),
  isActive: boolean("is_active").notNull().default(true),
  lastLogin: timestamp("last_login"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertUserSchema = createInsertSchema(users).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  lastLogin: true,
});
export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;

// ============================================================================
// CRM: CONTACT SERVICE - Accounts, Contacts, Addresses
// ============================================================================

export const accounts = pgTable("accounts", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  name: text("name").notNull(),
  industry: text("industry"),
  website: text("website"),
  phone: text("phone"),
  email: text("email"),
  type: text("type").notNull().default("customer"),
  status: text("status").notNull().default("active"),
  annualRevenue: decimal("annual_revenue", { precision: 15, scale: 2 }),
  employeeCount: integer("employee_count"),
  description: text("description"),
  ownerId: varchar("owner_id").references(() => users.id),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertAccountSchema = createInsertSchema(accounts).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});
export type InsertAccount = z.infer<typeof insertAccountSchema>;
export type Account = typeof accounts.$inferSelect;

export const contacts = pgTable("contacts", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  firstName: text("first_name").notNull(),
  lastName: text("last_name").notNull(),
  email: text("email").notNull(),
  phone: text("phone"),
  mobile: text("mobile"),
  title: text("title"),
  department: text("department"),
  accountId: varchar("account_id").references(() => accounts.id),
  status: text("status").notNull().default("active"),
  source: text("source"),
  ownerId: varchar("owner_id").references(() => users.id),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertContactSchema = createInsertSchema(contacts).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});
export type InsertContact = z.infer<typeof insertContactSchema>;
export type Contact = typeof contacts.$inferSelect;

export const addresses = pgTable("addresses", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  street: text("street").notNull(),
  city: text("city").notNull(),
  state: text("state"),
  postalCode: text("postal_code"),
  country: text("country").notNull(),
  type: text("type").notNull().default("billing"),
  accountId: varchar("account_id").references(() => accounts.id),
  contactId: varchar("contact_id").references(() => contacts.id),
  isPrimary: boolean("is_primary").notNull().default(false),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertAddressSchema = createInsertSchema(addresses).omit({
  id: true,
  createdAt: true,
});
export type InsertAddress = z.infer<typeof insertAddressSchema>;
export type Address = typeof addresses.$inferSelect;

// ============================================================================
// CRM: SALES SERVICE - Leads, Opportunities, Pipeline Stages
// ============================================================================

export const pipelineStages = pgTable("pipeline_stages", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  name: text("name").notNull(),
  order: integer("order").notNull(),
  probability: integer("probability").notNull().default(0),
  color: text("color").notNull().default("#3B82F6"),
  isActive: boolean("is_active").notNull().default(true),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertPipelineStageSchema = createInsertSchema(pipelineStages).omit({
  id: true,
  createdAt: true,
});
export type InsertPipelineStage = z.infer<typeof insertPipelineStageSchema>;
export type PipelineStage = typeof pipelineStages.$inferSelect;

export const leads = pgTable("leads", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  firstName: text("first_name").notNull(),
  lastName: text("last_name").notNull(),
  email: text("email").notNull(),
  phone: text("phone"),
  company: text("company"),
  title: text("title"),
  source: text("source"),
  status: text("status").notNull().default("new"),
  rating: text("rating"),
  estimatedValue: decimal("estimated_value", { precision: 15, scale: 2 }),
  description: text("description"),
  ownerId: varchar("owner_id").references(() => users.id),
  convertedContactId: varchar("converted_contact_id").references(() => contacts.id),
  convertedAccountId: varchar("converted_account_id").references(() => accounts.id),
  convertedAt: timestamp("converted_at"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertLeadSchema = createInsertSchema(leads).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  convertedAt: true,
});
export type InsertLead = z.infer<typeof insertLeadSchema>;
export type Lead = typeof leads.$inferSelect;

export const opportunities = pgTable("opportunities", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  name: text("name").notNull(),
  accountId: varchar("account_id").references(() => accounts.id),
  contactId: varchar("contact_id").references(() => contacts.id),
  stageId: varchar("stage_id").references(() => pipelineStages.id),
  amount: decimal("amount", { precision: 15, scale: 2 }).notNull(),
  probability: integer("probability").notNull().default(0),
  closeDate: timestamp("close_date"),
  type: text("type"),
  source: text("source"),
  description: text("description"),
  status: text("status").notNull().default("open"),
  ownerId: varchar("owner_id").references(() => users.id),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertOpportunitySchema = createInsertSchema(opportunities).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});
export type InsertOpportunity = z.infer<typeof insertOpportunitySchema>;
export type Opportunity = typeof opportunities.$inferSelect;

// ============================================================================
// CRM: MARKETING SERVICE - Campaigns, Mailing Lists, Segments
// ============================================================================

export const campaigns = pgTable("campaigns", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  name: text("name").notNull(),
  type: text("type").notNull(),
  status: text("status").notNull().default("draft"),
  startDate: timestamp("start_date"),
  endDate: timestamp("end_date"),
  budget: decimal("budget", { precision: 12, scale: 2 }),
  actualCost: decimal("actual_cost", { precision: 12, scale: 2 }),
  expectedRevenue: decimal("expected_revenue", { precision: 15, scale: 2 }),
  actualRevenue: decimal("actual_revenue", { precision: 15, scale: 2 }),
  description: text("description"),
  targetAudience: text("target_audience"),
  ownerId: varchar("owner_id").references(() => users.id),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertCampaignSchema = createInsertSchema(campaigns).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});
export type InsertCampaign = z.infer<typeof insertCampaignSchema>;
export type Campaign = typeof campaigns.$inferSelect;

export const mailingLists = pgTable("mailing_lists", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  name: text("name").notNull(),
  description: text("description"),
  memberCount: integer("member_count").notNull().default(0),
  isActive: boolean("is_active").notNull().default(true),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertMailingListSchema = createInsertSchema(mailingLists).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});
export type InsertMailingList = z.infer<typeof insertMailingListSchema>;
export type MailingList = typeof mailingLists.$inferSelect;

export const segments = pgTable("segments", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  name: text("name").notNull(),
  description: text("description"),
  criteria: text("criteria"),
  memberCount: integer("member_count").notNull().default(0),
  isActive: boolean("is_active").notNull().default(true),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertSegmentSchema = createInsertSchema(segments).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});
export type InsertSegment = z.infer<typeof insertSegmentSchema>;
export type Segment = typeof segments.$inferSelect;

// ============================================================================
// CRM: SUPPORT SERVICE - Tickets, Comments, SLAs
// ============================================================================

export const slas = pgTable("slas", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  name: text("name").notNull(),
  description: text("description"),
  responseTimeHours: integer("response_time_hours").notNull(),
  resolutionTimeHours: integer("resolution_time_hours").notNull(),
  priority: text("priority").notNull(),
  isActive: boolean("is_active").notNull().default(true),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertSlaSchema = createInsertSchema(slas).omit({
  id: true,
  createdAt: true,
});
export type InsertSla = z.infer<typeof insertSlaSchema>;
export type Sla = typeof slas.$inferSelect;

export const tickets = pgTable("tickets", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  ticketNumber: text("ticket_number").notNull().unique(),
  subject: text("subject").notNull(),
  description: text("description"),
  status: text("status").notNull().default("open"),
  priority: text("priority").notNull().default("medium"),
  type: text("type"),
  source: text("source"),
  accountId: varchar("account_id").references(() => accounts.id),
  contactId: varchar("contact_id").references(() => contacts.id),
  assignedToId: varchar("assigned_to_id").references(() => users.id),
  slaId: varchar("sla_id").references(() => slas.id),
  dueDate: timestamp("due_date"),
  resolvedAt: timestamp("resolved_at"),
  closedAt: timestamp("closed_at"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertTicketSchema = createInsertSchema(tickets).omit({
  id: true,
  ticketNumber: true,
  createdAt: true,
  updatedAt: true,
  resolvedAt: true,
  closedAt: true,
});
export type InsertTicket = z.infer<typeof insertTicketSchema>;
export type Ticket = typeof tickets.$inferSelect;

export const ticketComments = pgTable("ticket_comments", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  ticketId: varchar("ticket_id").references(() => tickets.id).notNull(),
  authorId: varchar("author_id").references(() => users.id),
  content: text("content").notNull(),
  isInternal: boolean("is_internal").notNull().default(false),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertTicketCommentSchema = createInsertSchema(ticketComments).omit({
  id: true,
  createdAt: true,
});
export type InsertTicketComment = z.infer<typeof insertTicketCommentSchema>;
export type TicketComment = typeof ticketComments.$inferSelect;

// ============================================================================
// ERP: INVENTORY SERVICE - Products, Stock Items, Warehouses
// ============================================================================

export const warehouses = pgTable("warehouses", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  name: text("name").notNull(),
  code: text("code").notNull().unique(),
  address: text("address"),
  city: text("city"),
  country: text("country"),
  capacity: integer("capacity"),
  managerId: varchar("manager_id").references(() => users.id),
  isActive: boolean("is_active").notNull().default(true),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertWarehouseSchema = createInsertSchema(warehouses).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});
export type InsertWarehouse = z.infer<typeof insertWarehouseSchema>;
export type Warehouse = typeof warehouses.$inferSelect;

export const products = pgTable("products", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  sku: text("sku").notNull().unique(),
  name: text("name").notNull(),
  description: text("description"),
  category: text("category"),
  unitPrice: decimal("unit_price", { precision: 12, scale: 2 }).notNull(),
  costPrice: decimal("cost_price", { precision: 12, scale: 2 }),
  unit: text("unit").notNull().default("each"),
  reorderLevel: integer("reorder_level").default(10),
  reorderQuantity: integer("reorder_quantity").default(50),
  isActive: boolean("is_active").notNull().default(true),
  imageUrl: text("image_url"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertProductSchema = createInsertSchema(products).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});
export type InsertProduct = z.infer<typeof insertProductSchema>;
export type Product = typeof products.$inferSelect;

export const stockItems = pgTable("stock_items", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  productId: varchar("product_id").references(() => products.id).notNull(),
  warehouseId: varchar("warehouse_id").references(() => warehouses.id).notNull(),
  quantity: integer("quantity").notNull().default(0),
  reservedQuantity: integer("reserved_quantity").notNull().default(0),
  availableQuantity: integer("available_quantity").notNull().default(0),
  location: text("location"),
  lastCountedAt: timestamp("last_counted_at"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertStockItemSchema = createInsertSchema(stockItems).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});
export type InsertStockItem = z.infer<typeof insertStockItemSchema>;
export type StockItem = typeof stockItems.$inferSelect;

// ============================================================================
// ERP: FINANCE SERVICE - Invoices, Payments, General Ledger
// ============================================================================

export const invoices = pgTable("invoices", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  invoiceNumber: text("invoice_number").notNull().unique(),
  accountId: varchar("account_id").references(() => accounts.id),
  contactId: varchar("contact_id").references(() => contacts.id),
  status: text("status").notNull().default("draft"),
  issueDate: timestamp("issue_date").notNull().defaultNow(),
  dueDate: timestamp("due_date").notNull(),
  subtotal: decimal("subtotal", { precision: 15, scale: 2 }).notNull(),
  taxAmount: decimal("tax_amount", { precision: 15, scale: 2 }).notNull().default("0"),
  totalAmount: decimal("total_amount", { precision: 15, scale: 2 }).notNull(),
  paidAmount: decimal("paid_amount", { precision: 15, scale: 2 }).notNull().default("0"),
  currency: text("currency").notNull().default("USD"),
  notes: text("notes"),
  terms: text("terms"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertInvoiceSchema = createInsertSchema(invoices).omit({
  id: true,
  invoiceNumber: true,
  createdAt: true,
  updatedAt: true,
});
export type InsertInvoice = z.infer<typeof insertInvoiceSchema>;
export type Invoice = typeof invoices.$inferSelect;

export const invoiceLineItems = pgTable("invoice_line_items", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  invoiceId: varchar("invoice_id").references(() => invoices.id).notNull(),
  productId: varchar("product_id").references(() => products.id),
  description: text("description").notNull(),
  quantity: decimal("quantity", { precision: 12, scale: 2 }).notNull(),
  unitPrice: decimal("unit_price", { precision: 12, scale: 2 }).notNull(),
  discount: decimal("discount", { precision: 5, scale: 2 }).default("0"),
  taxRate: decimal("tax_rate", { precision: 5, scale: 2 }).default("0"),
  totalAmount: decimal("total_amount", { precision: 15, scale: 2 }).notNull(),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertInvoiceLineItemSchema = createInsertSchema(invoiceLineItems).omit({
  id: true,
  createdAt: true,
});
export type InsertInvoiceLineItem = z.infer<typeof insertInvoiceLineItemSchema>;
export type InvoiceLineItem = typeof invoiceLineItems.$inferSelect;

export const payments = pgTable("payments", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  paymentNumber: text("payment_number").notNull().unique(),
  invoiceId: varchar("invoice_id").references(() => invoices.id),
  accountId: varchar("account_id").references(() => accounts.id),
  amount: decimal("amount", { precision: 15, scale: 2 }).notNull(),
  currency: text("currency").notNull().default("USD"),
  method: text("method").notNull(),
  status: text("status").notNull().default("pending"),
  paymentDate: timestamp("payment_date").notNull().defaultNow(),
  reference: text("reference"),
  notes: text("notes"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertPaymentSchema = createInsertSchema(payments).omit({
  id: true,
  paymentNumber: true,
  createdAt: true,
  updatedAt: true,
});
export type InsertPayment = z.infer<typeof insertPaymentSchema>;
export type Payment = typeof payments.$inferSelect;

export const generalLedgerEntries = pgTable("general_ledger_entries", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  entryNumber: text("entry_number").notNull().unique(),
  date: timestamp("date").notNull().defaultNow(),
  accountCode: text("account_code").notNull(),
  accountName: text("account_name").notNull(),
  description: text("description"),
  debit: decimal("debit", { precision: 15, scale: 2 }).notNull().default("0"),
  credit: decimal("credit", { precision: 15, scale: 2 }).notNull().default("0"),
  balance: decimal("balance", { precision: 15, scale: 2 }).notNull().default("0"),
  reference: text("reference"),
  invoiceId: varchar("invoice_id").references(() => invoices.id),
  paymentId: varchar("payment_id").references(() => payments.id),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertGeneralLedgerEntrySchema = createInsertSchema(generalLedgerEntries).omit({
  id: true,
  entryNumber: true,
  createdAt: true,
});
export type InsertGeneralLedgerEntry = z.infer<typeof insertGeneralLedgerEntrySchema>;
export type GeneralLedgerEntry = typeof generalLedgerEntries.$inferSelect;

// ============================================================================
// ERP: HR SERVICE - Employees, Payroll, Leave Requests
// ============================================================================

export const employees = pgTable("employees", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  employeeNumber: text("employee_number").notNull().unique(),
  userId: varchar("user_id").references(() => users.id),
  firstName: text("first_name").notNull(),
  lastName: text("last_name").notNull(),
  email: text("email").notNull(),
  phone: text("phone"),
  department: text("department"),
  position: text("position"),
  managerId: varchar("manager_id"),
  hireDate: timestamp("hire_date").notNull(),
  terminationDate: timestamp("termination_date"),
  salary: decimal("salary", { precision: 12, scale: 2 }),
  salaryFrequency: text("salary_frequency").default("monthly"),
  status: text("status").notNull().default("active"),
  address: text("address"),
  city: text("city"),
  country: text("country"),
  emergencyContact: text("emergency_contact"),
  emergencyPhone: text("emergency_phone"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertEmployeeSchema = createInsertSchema(employees).omit({
  id: true,
  employeeNumber: true,
  createdAt: true,
  updatedAt: true,
});
export type InsertEmployee = z.infer<typeof insertEmployeeSchema>;
export type Employee = typeof employees.$inferSelect;

export const payrollRecords = pgTable("payroll_records", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  employeeId: varchar("employee_id").references(() => employees.id).notNull(),
  periodStart: timestamp("period_start").notNull(),
  periodEnd: timestamp("period_end").notNull(),
  baseSalary: decimal("base_salary", { precision: 12, scale: 2 }).notNull(),
  overtime: decimal("overtime", { precision: 12, scale: 2 }).default("0"),
  bonus: decimal("bonus", { precision: 12, scale: 2 }).default("0"),
  deductions: decimal("deductions", { precision: 12, scale: 2 }).default("0"),
  taxAmount: decimal("tax_amount", { precision: 12, scale: 2 }).default("0"),
  netPay: decimal("net_pay", { precision: 12, scale: 2 }).notNull(),
  status: text("status").notNull().default("pending"),
  paidDate: timestamp("paid_date"),
  notes: text("notes"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertPayrollRecordSchema = createInsertSchema(payrollRecords).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});
export type InsertPayrollRecord = z.infer<typeof insertPayrollRecordSchema>;
export type PayrollRecord = typeof payrollRecords.$inferSelect;

export const leaveRequests = pgTable("leave_requests", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  employeeId: varchar("employee_id").references(() => employees.id).notNull(),
  type: text("type").notNull(),
  startDate: timestamp("start_date").notNull(),
  endDate: timestamp("end_date").notNull(),
  totalDays: decimal("total_days", { precision: 5, scale: 1 }).notNull(),
  reason: text("reason"),
  status: text("status").notNull().default("pending"),
  approvedById: varchar("approved_by_id").references(() => users.id),
  approvedAt: timestamp("approved_at"),
  notes: text("notes"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertLeaveRequestSchema = createInsertSchema(leaveRequests).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  approvedAt: true,
});
export type InsertLeaveRequest = z.infer<typeof insertLeaveRequestSchema>;
export type LeaveRequest = typeof leaveRequests.$inferSelect;

// ============================================================================
// ERP: ORDER SERVICE - Sales Orders, Purchase Orders, Line Items
// ============================================================================

export const salesOrders = pgTable("sales_orders", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  orderNumber: text("order_number").notNull().unique(),
  accountId: varchar("account_id").references(() => accounts.id),
  contactId: varchar("contact_id").references(() => contacts.id),
  opportunityId: varchar("opportunity_id").references(() => opportunities.id),
  status: text("status").notNull().default("draft"),
  orderDate: timestamp("order_date").notNull().defaultNow(),
  deliveryDate: timestamp("delivery_date"),
  shippingAddress: text("shipping_address"),
  billingAddress: text("billing_address"),
  subtotal: decimal("subtotal", { precision: 15, scale: 2 }).notNull(),
  taxAmount: decimal("tax_amount", { precision: 15, scale: 2 }).default("0"),
  shippingCost: decimal("shipping_cost", { precision: 12, scale: 2 }).default("0"),
  discount: decimal("discount", { precision: 12, scale: 2 }).default("0"),
  totalAmount: decimal("total_amount", { precision: 15, scale: 2 }).notNull(),
  currency: text("currency").notNull().default("USD"),
  notes: text("notes"),
  ownerId: varchar("owner_id").references(() => users.id),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertSalesOrderSchema = createInsertSchema(salesOrders).omit({
  id: true,
  orderNumber: true,
  createdAt: true,
  updatedAt: true,
});
export type InsertSalesOrder = z.infer<typeof insertSalesOrderSchema>;
export type SalesOrder = typeof salesOrders.$inferSelect;

export const salesOrderLineItems = pgTable("sales_order_line_items", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  salesOrderId: varchar("sales_order_id").references(() => salesOrders.id).notNull(),
  productId: varchar("product_id").references(() => products.id),
  description: text("description").notNull(),
  quantity: decimal("quantity", { precision: 12, scale: 2 }).notNull(),
  unitPrice: decimal("unit_price", { precision: 12, scale: 2 }).notNull(),
  discount: decimal("discount", { precision: 5, scale: 2 }).default("0"),
  taxRate: decimal("tax_rate", { precision: 5, scale: 2 }).default("0"),
  totalAmount: decimal("total_amount", { precision: 15, scale: 2 }).notNull(),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertSalesOrderLineItemSchema = createInsertSchema(salesOrderLineItems).omit({
  id: true,
  createdAt: true,
});
export type InsertSalesOrderLineItem = z.infer<typeof insertSalesOrderLineItemSchema>;
export type SalesOrderLineItem = typeof salesOrderLineItems.$inferSelect;

export const purchaseOrders = pgTable("purchase_orders", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  orderNumber: text("order_number").notNull().unique(),
  supplierId: varchar("supplier_id").references(() => accounts.id),
  status: text("status").notNull().default("draft"),
  orderDate: timestamp("order_date").notNull().defaultNow(),
  expectedDeliveryDate: timestamp("expected_delivery_date"),
  receivedDate: timestamp("received_date"),
  warehouseId: varchar("warehouse_id").references(() => warehouses.id),
  subtotal: decimal("subtotal", { precision: 15, scale: 2 }).notNull(),
  taxAmount: decimal("tax_amount", { precision: 15, scale: 2 }).default("0"),
  shippingCost: decimal("shipping_cost", { precision: 12, scale: 2 }).default("0"),
  totalAmount: decimal("total_amount", { precision: 15, scale: 2 }).notNull(),
  currency: text("currency").notNull().default("USD"),
  notes: text("notes"),
  approvedById: varchar("approved_by_id").references(() => users.id),
  approvedAt: timestamp("approved_at"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertPurchaseOrderSchema = createInsertSchema(purchaseOrders).omit({
  id: true,
  orderNumber: true,
  createdAt: true,
  updatedAt: true,
  approvedAt: true,
});
export type InsertPurchaseOrder = z.infer<typeof insertPurchaseOrderSchema>;
export type PurchaseOrder = typeof purchaseOrders.$inferSelect;

export const purchaseOrderLineItems = pgTable("purchase_order_line_items", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  purchaseOrderId: varchar("purchase_order_id").references(() => purchaseOrders.id).notNull(),
  productId: varchar("product_id").references(() => products.id),
  description: text("description").notNull(),
  quantity: decimal("quantity", { precision: 12, scale: 2 }).notNull(),
  unitPrice: decimal("unit_price", { precision: 12, scale: 2 }).notNull(),
  taxRate: decimal("tax_rate", { precision: 5, scale: 2 }).default("0"),
  totalAmount: decimal("total_amount", { precision: 15, scale: 2 }).notNull(),
  receivedQuantity: decimal("received_quantity", { precision: 12, scale: 2 }).default("0"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertPurchaseOrderLineItemSchema = createInsertSchema(purchaseOrderLineItems).omit({
  id: true,
  createdAt: true,
});
export type InsertPurchaseOrderLineItem = z.infer<typeof insertPurchaseOrderLineItemSchema>;
export type PurchaseOrderLineItem = typeof purchaseOrderLineItems.$inferSelect;

// ============================================================================
// CONSTRUCTION SPECIFIC - Projects, Equipment, Safety, Documents
// ============================================================================

export const projects = pgTable("projects", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  location: text("location").notNull(),
  status: text("status").notNull(),
  progress: integer("progress").notNull().default(0),
  plannedProgress: integer("planned_progress").notNull().default(0),
  budget: decimal("budget", { precision: 12, scale: 2 }).notNull(),
  actualCost: decimal("actual_cost", { precision: 12, scale: 2 }).notNull().default("0"),
  dueDate: text("due_date").notNull(),
  accountId: varchar("account_id").references(() => accounts.id),
  managerId: varchar("manager_id").references(() => users.id),
  description: text("description"),
  startDate: timestamp("start_date"),
  nextMilestoneDate: timestamp("next_milestone_date"),
  nextMilestoneName: text("next_milestone_name"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertProjectSchema = createInsertSchema(projects).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});
export type InsertProject = z.infer<typeof insertProjectSchema>;
export type Project = typeof projects.$inferSelect;

export const transactions = pgTable("transactions", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  projectId: text("project_id").references(() => projects.id),
  description: text("description").notNull(),
  amount: decimal("amount", { precision: 12, scale: 2 }).notNull(),
  status: text("status").notNull(),
  category: text("category"),
  type: text("type").default("expense"),
  date: timestamp("date").notNull().defaultNow(),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertTransactionSchema = createInsertSchema(transactions).omit({
  id: true,
  createdAt: true,
});
export type InsertTransaction = z.infer<typeof insertTransactionSchema>;
export type Transaction = typeof transactions.$inferSelect;

export const equipment = pgTable("equipment", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  status: text("status").notNull(),
  location: text("location").notNull(),
  nextService: text("next_service").notNull(),
  imageUrl: text("image_url"),
  serialNumber: text("serial_number"),
  purchaseDate: timestamp("purchase_date"),
  purchasePrice: decimal("purchase_price", { precision: 12, scale: 2 }),
  warehouseId: varchar("warehouse_id").references(() => warehouses.id),
  assignedToId: varchar("assigned_to_id").references(() => employees.id),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertEquipmentSchema = createInsertSchema(equipment).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});
export type InsertEquipment = z.infer<typeof insertEquipmentSchema>;
export type Equipment = typeof equipment.$inferSelect;

export const safetyInspections = pgTable("safety_inspections", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  site: text("site").notNull(),
  type: text("type").notNull(),
  status: text("status").notNull(),
  inspector: text("inspector").notNull(),
  date: timestamp("date").notNull().defaultNow(),
  notes: text("notes"),
  projectId: text("project_id").references(() => projects.id),
  findings: text("findings"),
  correctiveActions: text("corrective_actions"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertSafetyInspectionSchema = createInsertSchema(safetyInspections).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});
export type InsertSafetyInspection = z.infer<typeof insertSafetyInspectionSchema>;
export type SafetyInspection = typeof safetyInspections.$inferSelect;

export const clients = pgTable("clients", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  name: text("name").notNull(),
  company: text("company").notNull(),
  role: text("role").notNull(),
  email: text("email").notNull(),
  phone: text("phone").notNull(),
  status: text("status").notNull(),
  avatar: text("avatar").notNull(),
  accountId: varchar("account_id").references(() => accounts.id),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertClientSchema = createInsertSchema(clients).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});
export type InsertClient = z.infer<typeof insertClientSchema>;
export type Client = typeof clients.$inferSelect;

export const documents = pgTable("documents", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  name: text("name").notNull(),
  type: text("type").notNull(),
  size: text("size").notNull(),
  author: text("author").notNull(),
  uploadedAt: timestamp("uploaded_at").notNull().defaultNow(),
  projectId: text("project_id").references(() => projects.id),
  category: text("category"),
  url: text("url"),
  version: integer("version").default(1),
});

export const insertDocumentSchema = createInsertSchema(documents).omit({
  id: true,
  uploadedAt: true,
});
export type InsertDocument = z.infer<typeof insertDocumentSchema>;
export type Document = typeof documents.$inferSelect;

// ============================================================================
// EVENT SYSTEM - For async inter-service communication
// ============================================================================

export const events = pgTable("events", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  type: text("type").notNull(),
  payload: text("payload").notNull(),
  status: text("status").notNull().default("pending"),
  source: text("source").notNull(),
  processedAt: timestamp("processed_at"),
  error: text("error"),
  retryCount: integer("retry_count").notNull().default(0),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertEventSchema = createInsertSchema(events).omit({
  id: true,
  createdAt: true,
  processedAt: true,
});
export type InsertEvent = z.infer<typeof insertEventSchema>;
export type Event = typeof events.$inferSelect;

// ============================================================================
// AUDIT LOG - For tracking all changes
// ============================================================================

export const auditLogs = pgTable("audit_logs", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  userId: varchar("user_id").references(() => users.id),
  action: text("action").notNull(),
  entityType: text("entity_type").notNull(),
  entityId: text("entity_id").notNull(),
  oldValues: text("old_values"),
  newValues: text("new_values"),
  ipAddress: text("ip_address"),
  userAgent: text("user_agent"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertAuditLogSchema = createInsertSchema(auditLogs).omit({
  id: true,
  createdAt: true,
});
export type InsertAuditLog = z.infer<typeof insertAuditLogSchema>;
export type AuditLog = typeof auditLogs.$inferSelect;
