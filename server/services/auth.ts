import { Request, Response, NextFunction } from "express";
import crypto from "crypto";

export interface UserSession {
  userId: string;
  username: string;
  email?: string;
  role: UserRole;
  permissions: Permission[];
  loginAt: Date;
  expiresAt: Date;
}

export type UserRole = "admin" | "manager" | "employee" | "viewer" | "guest";

export type Permission = 
  | "projects:read" | "projects:write" | "projects:delete"
  | "transactions:read" | "transactions:write" | "transactions:delete"
  | "clients:read" | "clients:write" | "clients:delete"
  | "equipment:read" | "equipment:write" | "equipment:delete"
  | "safety:read" | "safety:write" | "safety:delete"
  | "leads:read" | "leads:write" | "leads:delete"
  | "opportunities:read" | "opportunities:write" | "opportunities:delete"
  | "contacts:read" | "contacts:write" | "contacts:delete"
  | "accounts:read" | "accounts:write" | "accounts:delete"
  | "campaigns:read" | "campaigns:write" | "campaigns:delete"
  | "tickets:read" | "tickets:write" | "tickets:delete"
  | "products:read" | "products:write" | "products:delete"
  | "inventory:read" | "inventory:write" | "inventory:delete"
  | "invoices:read" | "invoices:write" | "invoices:delete"
  | "payments:read" | "payments:write" | "payments:delete"
  | "employees:read" | "employees:write" | "employees:delete"
  | "payroll:read" | "payroll:write" | "payroll:delete"
  | "orders:read" | "orders:write" | "orders:delete"
  | "reports:read" | "reports:export"
  | "settings:read" | "settings:write"
  | "admin:all";

const rolePermissions: Record<UserRole, Permission[]> = {
  admin: ["admin:all"],
  manager: [
    "projects:read", "projects:write", "projects:delete",
    "transactions:read", "transactions:write", "transactions:delete",
    "clients:read", "clients:write", "clients:delete",
    "equipment:read", "equipment:write", "equipment:delete",
    "safety:read", "safety:write", "safety:delete",
    "leads:read", "leads:write", "leads:delete",
    "opportunities:read", "opportunities:write", "opportunities:delete",
    "contacts:read", "contacts:write", "contacts:delete",
    "accounts:read", "accounts:write", "accounts:delete",
    "campaigns:read", "campaigns:write",
    "tickets:read", "tickets:write",
    "products:read", "products:write",
    "inventory:read", "inventory:write",
    "invoices:read", "invoices:write",
    "payments:read", "payments:write",
    "employees:read", "employees:write",
    "payroll:read",
    "orders:read", "orders:write",
    "reports:read", "reports:export",
    "settings:read",
  ],
  employee: [
    "projects:read", "projects:write",
    "transactions:read",
    "clients:read",
    "equipment:read", "equipment:write",
    "safety:read", "safety:write",
    "leads:read", "leads:write",
    "opportunities:read", "opportunities:write",
    "contacts:read", "contacts:write",
    "accounts:read",
    "tickets:read", "tickets:write",
    "products:read",
    "inventory:read",
    "orders:read",
    "reports:read",
  ],
  viewer: [
    "projects:read",
    "transactions:read",
    "clients:read",
    "equipment:read",
    "safety:read",
    "leads:read",
    "opportunities:read",
    "contacts:read",
    "accounts:read",
    "tickets:read",
    "products:read",
    "inventory:read",
    "orders:read",
    "reports:read",
  ],
  guest: [
    "projects:read",
    "clients:read",
  ],
};

const sessions = new Map<string, UserSession>();

export function hashPassword(password: string): string {
  const salt = crypto.randomBytes(16).toString("hex");
  const hash = crypto.pbkdf2Sync(password, salt, 1000, 64, "sha512").toString("hex");
  return `${salt}:${hash}`;
}

export function verifyPassword(password: string, storedHash: string): boolean {
  const [salt, hash] = storedHash.split(":");
  const computedHash = crypto.pbkdf2Sync(password, salt, 1000, 64, "sha512").toString("hex");
  return hash === computedHash;
}

export function generateSessionToken(): string {
  return crypto.randomBytes(32).toString("hex");
}

export function createSession(userId: string, username: string, role: UserRole, email?: string): { token: string; session: UserSession } {
  const token = generateSessionToken();
  const permissions = getPermissionsForRole(role);
  const session: UserSession = {
    userId,
    username,
    email,
    role,
    permissions,
    loginAt: new Date(),
    expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000),
  };
  sessions.set(token, session);
  return { token, session };
}

export function getSession(token: string): UserSession | undefined {
  const session = sessions.get(token);
  if (!session) return undefined;
  if (session.expiresAt < new Date()) {
    sessions.delete(token);
    return undefined;
  }
  return session;
}

export function destroySession(token: string): boolean {
  return sessions.delete(token);
}

export function getPermissionsForRole(role: UserRole): Permission[] {
  return rolePermissions[role] || [];
}

export function hasPermission(session: UserSession, permission: Permission): boolean {
  if (session.permissions.includes("admin:all")) return true;
  return session.permissions.includes(permission);
}

export function hasAnyPermission(session: UserSession, permissions: Permission[]): boolean {
  if (session.permissions.includes("admin:all")) return true;
  return permissions.some(p => session.permissions.includes(p));
}

export function requireAuth(req: Request, res: Response, next: NextFunction): void {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    res.status(401).json({ error: "Authentication required" });
    return;
  }

  const token = authHeader.substring(7);
  const session = getSession(token);
  if (!session) {
    res.status(401).json({ error: "Invalid or expired session" });
    return;
  }

  (req as any).session = session;
  next();
}

export function requirePermission(...permissions: Permission[]) {
  return (req: Request, res: Response, next: NextFunction): void => {
    const session = (req as any).session as UserSession | undefined;
    if (!session) {
      res.status(401).json({ error: "Authentication required" });
      return;
    }

    if (!hasAnyPermission(session, permissions)) {
      res.status(403).json({ error: "Insufficient permissions" });
      return;
    }

    next();
  };
}

export function requireRole(...roles: UserRole[]) {
  return (req: Request, res: Response, next: NextFunction): void => {
    const session = (req as any).session as UserSession | undefined;
    if (!session) {
      res.status(401).json({ error: "Authentication required" });
      return;
    }

    if (!roles.includes(session.role)) {
      res.status(403).json({ error: "Insufficient role" });
      return;
    }

    next();
  };
}

export function optionalAuth(req: Request, res: Response, next: NextFunction): void {
  const authHeader = req.headers.authorization;
  if (authHeader && authHeader.startsWith("Bearer ")) {
    const token = authHeader.substring(7);
    const session = getSession(token);
    if (session) {
      (req as any).session = session;
    }
  }
  next();
}

export function getActiveSessions(): number {
  let count = 0;
  const now = new Date();
  const entries = Array.from(sessions.entries());
  for (const [token, session] of entries) {
    if (session.expiresAt >= now) {
      count++;
    } else {
      sessions.delete(token);
    }
  }
  return count;
}
