import React, { useEffect, useState } from "react";

// Pomocnik do fetch z timeoutem
async function fetchWithTimeout(url, { timeout = 5000 } = {}) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  try {
    const res = await fetch(url, { signal: controller.signal });
    clearTimeout(id);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } finally {
    clearTimeout(id);
  }
}

// Prosta mapa statusów -> etykieta + kolor
const badge = (status) => {
  const map = {
    ok:  { label: "OK",      className: "rounded-full px-3 py-1 text-xs bg-green-100 text-green-700" },
    down:{ label: "DOWN",    className: "rounded-full px-3 py-1 text-xs bg-red-100 text-red-700" },
    warn:{ label: "WARN",    className: "rounded-full px-3 py-1 text-xs bg-yellow-100 text-yellow-800" },
    pending:{ label: "PENDING", className: "rounded-full px-3 py-1 text-xs bg-yellow-100 text-yellow-800" },
    error:{ label: "ERROR",  className: "rounded-full px-3 py-1 text-xs bg-gray-200 text-gray-700" },
  };
  return map[status] ?? map.error;
};

export default function SystemHealth() {
  const [db, setDb]   = useState({ status: "pending", msg: "Checking..." });
  const [api, setApi] = useState({ status: "pending", msg: "Checking..." });

  useEffect(() => {
    let alive = true;

    async function checkOne(setter, url) {
      // do 3 prób (np. gdy sieć „mrugnie”)
      for (let attempt = 1; attempt <= 3; attempt++) {
        try {
          const data = await fetchWithTimeout(url, { timeout: 4000 });
          if (!alive) return;
          const status = data?.status === "ok" ? "ok" : (data?.status || "warn");
          setter({ status, msg: data?.message || "—" });
          return;
        } catch (e) {
          if (attempt === 3) {
            if (!alive) return;
            setter({ status: e.name === "AbortError" ? "warn" : "error", msg: e.message });
          }
          // mała pauza między próbami
          await new Promise(r => setTimeout(r, 300));
        }
      }
    }

    checkOne(setDb,  "/health/db");
    checkOne(setApi, "/health/api");

    // opcjonalne odświeżanie co 30 s
    const id = setInterval(() => {
      checkOne(setDb,  "/health/db");
      checkOne(setApi, "/health/api");
    }, 30000);

    return () => { alive = false; clearInterval(id); };
  }, []);

  const DB = badge(db.status);
  const API = badge(api.status);

  return (
    <div className="rounded-2xl shadow p-4 bg-white">
      <h3 className="font-semibold mb-3">System Health</h3>
      <div className="flex items-center justify-between py-2 border-b">
        <div>
          <div className="font-medium">Database</div>
          <div className="text-sm text-gray-500">{db.msg}</div>
        </div>
        <span className={DB.className}>{DB.label}</span>
      </div>
      <div className="flex items-center justify-between py-2">
        <div>
          <div className="font-medium">API Status</div>
          <div className="text-sm text-gray-500">{api.msg}</div>
        </div>
        <span className={API.className}>{API.label}</span>
      </div>
    </div>
  );
}
export default function SystemHealth() { ... }
