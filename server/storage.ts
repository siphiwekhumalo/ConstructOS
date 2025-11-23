import { drizzle } from "drizzle-orm/neon-serverless";
import { Pool } from "@neondatabase/serverless";
import { eq } from "drizzle-orm";
import {
  users,
  projects,
  transactions,
  equipment,
  safetyInspections,
  clients,
  documents,
  type User,
  type InsertUser,
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
} from "@shared/schema";

const pool = new Pool({ connectionString: process.env.DATABASE_URL });
const db = drizzle(pool);

export interface IStorage {
  // Users
  getUser(id: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;

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
}

export class DatabaseStorage implements IStorage {
  // Users
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

  // Projects
  async getProjects(): Promise<Project[]> {
    return await db.select().from(projects);
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
    const [updated] = await db.update(projects).set(project).where(eq(projects.id, id)).returning();
    return updated;
  }

  async deleteProject(id: string): Promise<boolean> {
    const result = await db.delete(projects).where(eq(projects.id, id));
    return result.rowCount ? result.rowCount > 0 : false;
  }

  // Transactions
  async getTransactions(): Promise<Transaction[]> {
    return await db.select().from(transactions);
  }

  async getTransactionsByProject(projectId: string): Promise<Transaction[]> {
    return await db.select().from(transactions).where(eq(transactions.projectId, projectId));
  }

  async createTransaction(transaction: InsertTransaction): Promise<Transaction> {
    const [newTransaction] = await db.insert(transactions).values(transaction).returning();
    return newTransaction;
  }

  // Equipment
  async getEquipment(): Promise<Equipment[]> {
    return await db.select().from(equipment);
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
    const [updated] = await db.update(equipment).set(item).where(eq(equipment.id, id)).returning();
    return updated;
  }

  // Safety Inspections
  async getSafetyInspections(): Promise<SafetyInspection[]> {
    return await db.select().from(safetyInspections);
  }

  async createSafetyInspection(inspection: InsertSafetyInspection): Promise<SafetyInspection> {
    const [newInspection] = await db.insert(safetyInspections).values(inspection).returning();
    return newInspection;
  }

  // Clients
  async getClients(): Promise<Client[]> {
    return await db.select().from(clients);
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
    const [updated] = await db.update(clients).set(client).where(eq(clients.id, id)).returning();
    return updated;
  }

  // Documents
  async getDocuments(): Promise<Document[]> {
    return await db.select().from(documents);
  }

  async getDocumentsByProject(projectId: string): Promise<Document[]> {
    return await db.select().from(documents).where(eq(documents.projectId, projectId));
  }

  async createDocument(document: InsertDocument): Promise<Document> {
    const [newDocument] = await db.insert(documents).values(document).returning();
    return newDocument;
  }
}

export const storage = new DatabaseStorage();
