import fs from "node:fs";
import { type Server } from "node:http";
import path from "node:path";
import { spawn, type ChildProcess } from "node:child_process";

import express, { type Express, type Request } from "express";

import runApp from "./app";

let gunicornProcess: ChildProcess | null = null;

function startGunicorn(): Promise<void> {
  return new Promise((resolve, reject) => {
    console.log("[Gunicorn] Starting production server...");
    
    const workers = process.env.GUNICORN_WORKERS || "4";
    const threads = process.env.GUNICORN_THREADS || "2";
    const timeout = process.env.GUNICORN_TIMEOUT || "120";
    
    gunicornProcess = spawn("gunicorn", [
      "backend.wsgi:application",
      "--bind", "0.0.0.0:8000",
      "--workers", workers,
      "--threads", threads,
      "--timeout", timeout,
      "--access-logfile", "-",
      "--error-logfile", "-",
      "--log-level", "info",
      "--capture-output",
      "--preload",
    ], {
      cwd: process.cwd(),
      env: {
        ...process.env,
        DJANGO_SETTINGS_MODULE: "backend.settings",
        PYTHONUNBUFFERED: "1",
      },
      stdio: ["ignore", "pipe", "pipe"],
    });

    gunicornProcess.stdout?.on("data", (data) => {
      const output = data.toString().trim();
      if (output) {
        console.log(`[Gunicorn] ${output}`);
      }
    });

    gunicornProcess.stderr?.on("data", (data) => {
      const output = data.toString().trim();
      if (output) {
        console.log(`[Gunicorn] ${output}`);
      }
      if (output.includes("Booting worker") || output.includes("Listening at")) {
        resolve();
      }
    });

    gunicornProcess.on("error", (err) => {
      console.error("[Gunicorn] Failed to start:", err.message);
      reject(err);
    });

    gunicornProcess.on("close", (code) => {
      console.log(`[Gunicorn] Process exited with code ${code}`);
      gunicornProcess = null;
    });

    setTimeout(() => {
      if (gunicornProcess) {
        console.log("[Gunicorn] Server started (timeout)");
        resolve();
      }
    }, 10000);
  });
}

function stopGunicorn() {
  if (gunicornProcess) {
    console.log("[Gunicorn] Stopping server...");
    gunicornProcess.kill("SIGTERM");
    gunicornProcess = null;
  }
}

process.on("SIGTERM", () => {
  stopGunicorn();
  process.exit(0);
});

process.on("SIGINT", () => {
  stopGunicorn();
  process.exit(0);
});

export async function serveStatic(app: Express, server: Server) {
  const distPath = path.resolve(import.meta.dirname, "public");

  if (!fs.existsSync(distPath)) {
    throw new Error(
      `Could not find the build directory: ${distPath}, make sure to build the client first`,
    );
  }

  app.use(express.static(distPath));

  app.use("*", (_req, res) => {
    res.sendFile(path.resolve(distPath, "index.html"));
  });
}

(async () => {
  try {
    await startGunicorn();
    console.log("[Express] Gunicorn backend started, starting Express gateway...");
  } catch (err) {
    console.error("[Express] Warning: Gunicorn backend failed to start, API calls will fail");
  }
  
  await runApp(serveStatic);
})();
