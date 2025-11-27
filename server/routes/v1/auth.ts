import { Router, Request, Response } from "express";
import { storage } from "../../storage";
import {
  hashPassword,
  verifyPassword,
  createSession,
  destroySession,
  getSession,
  getActiveSessions,
  requireAuth,
  UserRole,
} from "../../services/auth";

const router = Router();

router.post("/register", async (req: Request, res: Response) => {
  try {
    const { username, password, email, role = "employee" } = req.body;
    
    if (!username || !password) {
      return res.status(400).json({ error: "Username and password required" });
    }
    
    const existing = await storage.getUserByUsername(username);
    if (existing) {
      return res.status(409).json({ error: "Username already exists" });
    }
    
    const hashedPassword = hashPassword(password);
    const user = await storage.createUser({
      username,
      password: hashedPassword,
      email: email || `${username}@constructos.app`,
    });
    
    const { token, session } = createSession(user.id, user.username, role as UserRole, email);
    
    res.status(201).json({
      user: {
        id: user.id,
        username: user.username,
      },
      token,
      session: {
        role: session.role,
        permissions: session.permissions,
        expiresAt: session.expiresAt,
      },
    });
  } catch (error) {
    console.error("Registration error:", error);
    res.status(500).json({ error: "Registration failed" });
  }
});

router.post("/login", async (req: Request, res: Response) => {
  try {
    const { username, password } = req.body;
    
    if (!username || !password) {
      return res.status(400).json({ error: "Username and password required" });
    }
    
    const user = await storage.getUserByUsername(username);
    if (!user) {
      return res.status(401).json({ error: "Invalid credentials" });
    }
    
    if (!verifyPassword(password, user.password)) {
      return res.status(401).json({ error: "Invalid credentials" });
    }
    
    const role: UserRole = "admin";
    const { token, session } = createSession(user.id, user.username, role);
    
    res.json({
      user: {
        id: user.id,
        username: user.username,
      },
      token,
      session: {
        role: session.role,
        permissions: session.permissions,
        expiresAt: session.expiresAt,
      },
    });
  } catch (error) {
    console.error("Login error:", error);
    res.status(500).json({ error: "Login failed" });
  }
});

router.post("/logout", (req: Request, res: Response) => {
  const authHeader = req.headers.authorization;
  if (authHeader && authHeader.startsWith("Bearer ")) {
    const token = authHeader.substring(7);
    destroySession(token);
  }
  res.json({ success: true });
});

router.get("/me", requireAuth, (req: Request, res: Response) => {
  const session = (req as any).session;
  res.json({
    userId: session.userId,
    username: session.username,
    role: session.role,
    permissions: session.permissions,
    expiresAt: session.expiresAt,
  });
});

router.post("/refresh", requireAuth, (req: Request, res: Response) => {
  const session = (req as any).session;
  const { token, session: newSession } = createSession(
    session.userId,
    session.username,
    session.role,
    session.email
  );
  
  const authHeader = req.headers.authorization;
  if (authHeader && authHeader.startsWith("Bearer ")) {
    destroySession(authHeader.substring(7));
  }
  
  res.json({
    token,
    session: {
      role: newSession.role,
      permissions: newSession.permissions,
      expiresAt: newSession.expiresAt,
    },
  });
});

router.get("/sessions/active", requireAuth, (req: Request, res: Response) => {
  const session = (req as any).session;
  if (session.role !== "admin") {
    return res.status(403).json({ error: "Admin access required" });
  }
  res.json({ activeSessions: getActiveSessions() });
});

export default router;
