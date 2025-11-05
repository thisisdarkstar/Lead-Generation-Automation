import parseCSV from "@/utils/csvUtils";
import { downloadAsTxt } from "@/utils/fileSaver";
import React, { useEffect, useState } from "react";

const LOCAL_STORAGE_KEY = "domainUploaderDomains";
const DOMAIN_HANDOFF_KEY = "leadGenHandoffDomains";

export default function DomainUploader({ onExtracted }) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    const id = setTimeout(() => setMounted(true), 0);
    return () => clearTimeout(id);
  }, []);

  const [filename, setFilename] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [leadResult, setLeadResult] = useState(null);
  const [copied, setCopied] = useState(false);

  const [domains, setDomains] = useState(() => {
    if (typeof window === "undefined") return [];
    const saved = window.localStorage.getItem(LOCAL_STORAGE_KEY);
    if (saved) {
      try { return JSON.parse(saved); }
      catch { return []; }
    }
    return [];
  });

  useEffect(() => {
    if (domains.length)
      window.localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(domains));
    else
      window.localStorage.removeItem(LOCAL_STORAGE_KEY);
  }, [domains]);

  const handleUpload = async (e) => {
    setError("");
    setDomains([]);
    setLeadResult(null);
    setCopied(false);
    if (!e.target.files[0]) return;
    setFilename(e.target.files[0].name);
    try {
      const text = await e.target.files[0].text();
      const found = parseCSV(text);
      setDomains(found);
      if (onExtracted) onExtracted(found);
    } catch {
      setError("Invalid or unsupported CSV file.");
    }
  };

  const handleSendToLeadGen = () => {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(DOMAIN_HANDOFF_KEY, JSON.stringify(domains));
      // Optionally, trigger a navigation here (e.g., useRouter or a state callback to show the LeadGen component)
    }
  };

  const handleDownload = () => {
    if (!domains.length) return;
    downloadAsTxt(domains.join('\n'), "domains.txt");
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(domains.join("\n"));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleClear = () => {
    setDomains([]);
    setLeadResult(null);
    setError("");
    setCopied(false);
    setFilename("");
    window.localStorage.removeItem(LOCAL_STORAGE_KEY);
  };

  if (!mounted) {
    return (
      <main className="max-w-4xl mx-auto p-10">
        <h2 className="text-3xl font-bold mb-6">Domain CSV Extractor</h2>
        <div className="text-gray-400">Loading...</div>
      </main>
    );
  }

  return (
    <main className="max-w-4xl mx-auto p-10">
      <h2 className="text-3xl font-bold mb-6">Domain CSV Extractor</h2>
      <div className="mb-4 flex flex-wrap gap-3 items-center">
        <label className="text-base font-medium mb-2 block">
          <span className="mb-2 inline-block">UPLOAD CSV FILE</span>
          <div className="relative flex items-center">
            <button
              type="button"
              className="px-4 py-2 rounded bg-blue-700 hover:bg-blue-800 text-white font-medium mr-3 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400"
              tabIndex={-1}
              onClick={() => {
                document.getElementById("domain-upload-input").click();
              }}
            >
              Choose File
            </button>
            <input
              id="domain-upload-input"
              type="file"
              accept=".csv,text/csv"
              className="absolute left-0 top-0 w-full h-full opacity-0 cursor-pointer"
              onChange={handleUpload}
              style={{
                position: "absolute",
                left: 0,
                top: 0,
                width: "145px",
                height: "100%",
                opacity: 0,
                cursor: "pointer"
              }}
              tabIndex={0}
            />
            {filename && <span className="ml-3 text-gray-400">{filename}</span>}
          </div>
        </label>
      </div>
      {error && <div className="text-red-400 mb-2">{error}</div>}
      {domains.length > 0 && (
        <>
          <h3 className="text-xl font-semibold mt-6 mb-2">
            Extracted Domains <span className="font-normal text-gray-400">({domains.length})</span>
          </h3>
          <div
            className="
              border rounded-lg p-4 mb-4
              bg-gray-900 text-green-200
              max-h-80 min-h-72 min-w-[420px]
              text-base leading-6 font-mono
              overflow-y-scroll
              shadow-md
            "
            style={{ letterSpacing: "0.01rem" }}
          >
            {domains.map((d) => (
              <div key={d}>{d}</div>
            ))}
          </div>
          <div className="flex flex-wrap items-center gap-4 mt-2">
            <button
              onClick={handleCopy}
              className={"px-4 py-2 rounded transition-colors " + (copied
                ? "bg-green-500 text-white"
                : "bg-blue-900 hover:bg-blue-700 text-blue-100")}
            >
              {copied ? "Copied!" : "Copy All"}
            </button>
            <button
              onClick={handleDownload}
              className="px-4 py-2 rounded bg-green-800 hover:bg-green-700 text-white transition-colors"
            >
              Download as TXT
            </button>
            <button
              onClick={handleSendToLeadGen}
              className="px-4 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white transition-colors"
              disabled={domains.length === 0}
            >
              Send for Lead Generation
            </button>

            <div className="flex-1" />
            <button
              onClick={handleClear}
              className="px-4 py-2 rounded bg-red-800 hover:bg-red-700 text-white transition-colors"
            >
              Clear All
            </button>
          </div>
        </>
      )}
      {leadResult && (
        <pre className="bg-gray-900 p-4 mt-6 rounded max-h-72 overflow-y-auto text-xs text-gray-100">
          {JSON.stringify(leadResult, null, 2)}
        </pre>
      )}
    </main>
  );
}
