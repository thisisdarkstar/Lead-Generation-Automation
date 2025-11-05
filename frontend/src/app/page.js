"use client"
import React, { useState } from "react";
import DomainUploader from "@/components/DomainUploader";
import LeadsJsonExtractor from "@/components/LeadsJsonExtractor";
import HtmlDomainExtractor from "@/components/HtmlDomainExtractor";
import LeadGenerator from "@/components/LeadGeneration";

// Add more as you modularize!

const TABS = [
  { id: "csv", label: "CSV to Domains" },
  { id: "leads", label: "Extract From JSON" },
  { id: "html", label: "Extract From HTML" },
  { id: "lead_gen", label: "Lead Generation (slow)" }
];

export default function Home() {
  const [tab, setTab] = useState("csv");

  // Shared state (example: share domains across modules)
  const [domains, setDomains] = useState([]);

  return (
    <main style={{ maxWidth: 820, margin: "auto", padding: 24 }}>
      <nav style={{ marginBottom: 24, display: "flex", gap: 20 }}>
        {TABS.map(t => (
          <button
            key={t.id}
            style={{
              fontWeight: tab === t.id ? "bold" : "normal",
              borderBottom: tab === t.id ? "2px solid #1976d2" : "none",
              background: "none",
              padding: "8px 12px",
              cursor: "pointer"
            }}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </nav>
      <section>
        <div style={{ display: tab === "csv" ? "block" : "none" }}>
          <DomainUploader onExtracted={d => setDomains(d)} />
        </div>
        <div style={{ display: tab === "leads" ? "block" : "none" }}>
          <LeadsJsonExtractor initialDomains={domains} />
        </div>
        <div style={{ display: tab === "html" ? "block" : "none" }}>
          <HtmlDomainExtractor onExtracted={d => setDomains(d)} />
        </div>
        <div style={{ display: tab === "lead_gen" ? "block" : "none" }}>
          <LeadGenerator />
        </div>
      </section>

    </main>
  );
}
