import type { Project, InsertProject, Equipment, Client, Transaction, Document, SafetyInspection } from "@shared/schema";

const API_BASE = "/api";

// Projects
export async function getProjects(): Promise<Project[]> {
  const response = await fetch(`${API_BASE}/projects`);
  if (!response.ok) throw new Error("Failed to fetch projects");
  return response.json();
}

export async function createProject(project: InsertProject): Promise<Project> {
  const response = await fetch(`${API_BASE}/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(project),
  });
  if (!response.ok) throw new Error("Failed to create project");
  return response.json();
}

export async function updateProject(id: string, updates: Partial<InsertProject>): Promise<Project> {
  const response = await fetch(`${API_BASE}/projects/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updates),
  });
  if (!response.ok) throw new Error("Failed to update project");
  return response.json();
}

export async function deleteProject(id: string): Promise<void> {
  const response = await fetch(`${API_BASE}/projects/${id}`, {
    method: "DELETE",
  });
  if (!response.ok) throw new Error("Failed to delete project");
}

// Equipment
export async function getEquipment(): Promise<Equipment[]> {
  const response = await fetch(`${API_BASE}/equipment`);
  if (!response.ok) throw new Error("Failed to fetch equipment");
  return response.json();
}

// Clients
export async function getClients(): Promise<Client[]> {
  const response = await fetch(`${API_BASE}/clients`);
  if (!response.ok) throw new Error("Failed to fetch clients");
  return response.json();
}

// Transactions
export async function getTransactions(): Promise<Transaction[]> {
  const response = await fetch(`${API_BASE}/transactions`);
  if (!response.ok) throw new Error("Failed to fetch transactions");
  return response.json();
}

// Documents
export async function getDocuments(): Promise<Document[]> {
  const response = await fetch(`${API_BASE}/documents`);
  if (!response.ok) throw new Error("Failed to fetch documents");
  return response.json();
}

// Safety Inspections
export async function getSafetyInspections(): Promise<SafetyInspection[]> {
  const response = await fetch(`${API_BASE}/safety/inspections`);
  if (!response.ok) throw new Error("Failed to fetch inspections");
  return response.json();
}
