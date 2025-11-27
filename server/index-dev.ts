import fs from "node:fs";
import { type Server } from "node:http";
import path from "node:path";
import { spawn, type ChildProcess } from "node:child_process";

import type { Express } from "express";
import { nanoid } from "nanoid";
import { createServer as createViteServer, createLogger } from "vite";

import runApp from "./app";

import viteConfig from "../vite.config";

const viteLogger = createLogger();

let djangoProcess: ChildProcess | null = null;

const useGunicorn = process.env.USE_GUNICORN === "true";

function startDjango(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (useGunicorn) {
      console.log("[Django] Starting Gunicorn production server...");
      
      djangoProcess = spawn("gunicorn", [
        "backend.wsgi:application",
        "--bind", "0.0.0.0:8000",
        "--workers", "4",
        "--threads", "2",
        "--timeout", "120",
        "--access-logfile", "-",
        "--error-logfile", "-",
        "--log-level", "info",
        "--capture-output",
      ], {
        cwd: process.cwd(),
        env: {
          ...process.env,
          DJANGO_SETTINGS_MODULE: "backend.settings",
          PYTHONUNBUFFERED: "1",
        },
        stdio: ["ignore", "pipe", "pipe"],
      });

      djangoProcess.stdout?.on("data", (data) => {
        const output = data.toString().trim();
        if (output) {
          console.log(`[Gunicorn] ${output}`);
        }
        if (output.includes("Booting worker") || output.includes("Listening at")) {
          resolve();
        }
      });

      djangoProcess.stderr?.on("data", (data) => {
        const output = data.toString().trim();
        if (output) {
          console.log(`[Gunicorn] ${output}`);
        }
        if (output.includes("Booting worker") || output.includes("Listening at")) {
          resolve();
        }
      });
    } else {
      console.log("[Django] Starting Django development server...");
      
      djangoProcess = spawn("python", ["-m", "django", "runserver", "0.0.0.0:8000"], {
        cwd: process.cwd(),
        env: {
          ...process.env,
          DJANGO_SETTINGS_MODULE: "backend.settings",
          PYTHONUNBUFFERED: "1",
        },
        stdio: ["ignore", "pipe", "pipe"],
      });

      djangoProcess.stdout?.on("data", (data) => {
        const output = data.toString().trim();
        if (output) {
          console.log(`[Django] ${output}`);
        }
        if (output.includes("Starting development server") || output.includes("Watching for file changes")) {
          resolve();
        }
      });

      djangoProcess.stderr?.on("data", (data) => {
        const output = data.toString().trim();
        if (output) {
          console.error(`[Django] ${output}`);
        }
      });
    }

    djangoProcess.on("error", (err) => {
      console.error("[Django] Failed to start:", err.message);
      reject(err);
    });

    djangoProcess.on("close", (code) => {
      console.log(`[Django] Process exited with code ${code}`);
      djangoProcess = null;
    });

    setTimeout(() => {
      if (djangoProcess) {
        console.log("[Django] Server started (timeout)");
        resolve();
      }
    }, 8000);
  });
}

function stopDjango() {
  if (djangoProcess) {
    console.log("[Django] Stopping Django server...");
    djangoProcess.kill("SIGTERM");
    djangoProcess = null;
  }
}

process.on("SIGTERM", () => {
  stopDjango();
  process.exit(0);
});

process.on("SIGINT", () => {
  stopDjango();
  process.exit(0);
});

export async function setupVite(app: Express, server: Server) {
  const serverOptions = {
    middlewareMode: true,
    hmr: { server },
    allowedHosts: true as const,
  };

  const vite = await createViteServer({
    ...viteConfig,
    configFile: false,
    customLogger: {
      ...viteLogger,
      error: (msg, options) => {
        viteLogger.error(msg, options);
        process.exit(1);
      },
    },
    server: serverOptions,
    appType: "custom",
  });

  app.use(vite.middlewares);
  app.use("*", async (req, res, next) => {
    const url = req.originalUrl;

    try {
      const clientTemplate = path.resolve(
        import.meta.dirname,
        "..",
        "client",
        "index.html",
      );

      let template = await fs.promises.readFile(clientTemplate, "utf-8");
      template = template.replace(
        `src="/src/main.tsx"`,
        `src="/src/main.tsx?v=${nanoid()}"`,
      );
      const page = await vite.transformIndexHtml(url, template);
      res.status(200).set({ "Content-Type": "text/html" }).end(page);
    } catch (e) {
      vite.ssrFixStacktrace(e as Error);
      next(e);
    }
  });
}

(async () => {
  try {
    await startDjango();
    console.log("[Express] Django backend started, starting Express gateway...");
  } catch (err) {
    console.error("[Express] Warning: Django backend failed to start, API calls will fail");
  }
  
  await runApp(setupVite);
})();
