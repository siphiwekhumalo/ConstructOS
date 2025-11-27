import { Suspense } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";
import "./lib/i18n";

createRoot(document.getElementById("root")!).render(
  <Suspense fallback={<div className="flex items-center justify-center h-screen">Loading...</div>}>
    <App />
  </Suspense>
);
