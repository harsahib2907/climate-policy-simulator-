import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider } from "react-router-dom";

import { router } from "./app/routes";
import { SimulationProvider } from "./app/context/SimulationContext";

import "./styles/index.css";

const API =
  import.meta.env.VITE_API_URL || "http://localhost:5000/api";


/**
 * Bootstrap the app
 * Loads backend baseline BEFORE rendering UI
 */
async function bootstrap() {
  try {
    const res = await fetch(`${API}/init`);

    if (!res.ok) throw new Error("Backend not reachable");

    const json = await res.json();

    const initialData = json?.data || {};

    ReactDOM.createRoot(document.getElementById("root")!).render(
      <React.StrictMode>
        <SimulationProvider initialData={initialData}>
          <RouterProvider router={router} />
        </SimulationProvider>
      </React.StrictMode>
    );
  } catch (err) {
    console.error("❌ Backend server not running:", err);

    ReactDOM.createRoot(document.getElementById("root")!).render(
      <div style={{ padding: 40, fontFamily: "system-ui" }}>
        ⚠️ Backend not running<br />
        Start server → <b>python app.py</b>
      </div>
    );
  }
}

bootstrap();
