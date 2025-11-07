import React, { useState, useEffect } from "react";

const DOMAIN_HANDOFF_KEY = "leadGenHandoffDomains";
const LOCAL_STORAGE_KEY = "fetchedDomains";
const SIZE_OPTIONS = [10, 50, 100, 150, 200];

export default function FetchAllocations() {
    const [mounted, setMounted] = useState(false);
    useEffect(() => {
        const id = setTimeout(() => setMounted(true), 0);
        return () => clearTimeout(id);
    }, []);

    const [token, setToken] = useState("");
    const [size, setSize] = useState(50);
    const [domains, setDomains] = useState(() => {
        if (typeof window === "undefined") return [];
        const saved = window.localStorage.getItem(LOCAL_STORAGE_KEY);
        if (saved) {
            try {
                return JSON.parse(saved);
            } catch {
                return [];
            }
        }
        return [];
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [copied, setCopied] = useState(false);

    useEffect(() => {
        if (domains.length)
            window.localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(domains));
        else
            window.localStorage.removeItem(LOCAL_STORAGE_KEY);
    }, [domains]);

    const fetchDomains = async () => {
        setLoading(true);
        setError("");
        setDomains([]);
        try {
            const res = await fetch("http://localhost:8000/api/extract-namekart", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ token, size }),
            });
            if (!res.ok) throw new Error("Error fetching data");
            const data = await res.json();
            if (data.success && Array.isArray(data.domains)) {
                setDomains(data.domains);
            } else {
                throw new Error(data.message || "Error fetching data");
            }
        } catch (err) {
            setDomains([]);
            setError(err.message || "Error fetching data");
        } finally {
            setLoading(false);
        }
    };

    const handleLeadGen = () => {
        if (domains.length) {
            window.localStorage.setItem(DOMAIN_HANDOFF_KEY, JSON.stringify(domains));
            alert("Domains sent for lead generation!");
        }
    };

    const handleCopy = async () => {
        await navigator.clipboard.writeText(domains.join("\n"));
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const handleClear = () => {
        setDomains([]);
        setError("");
        setCopied(false);
        window.localStorage.removeItem(LOCAL_STORAGE_KEY);
    };

    if (!mounted) {
        return (
            <main className="max-w-4xl mx-auto p-10">
                <h2 className="text-3xl font-bold mb-6">Namekart API Extractor</h2>
                <div className="text-gray-400">Loading...</div>
            </main>
        );
    }

    return (
        <main className="max-w-4xl mx-auto p-10">
            <h2 className="text-3xl font-bold mb-6">Namekart API Extractor</h2>
            <div className="mb-4 flex flex-col gap-4">
                <label className="font-medium block">
                    <span className="mb-2 inline-block">TOKEN</span>
                    <input
                        type="text"
                        className="w-full px-3 py-2 bg-gray-800 text-white border border-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
                        value={token}
                        onChange={e => setToken(e.target.value)}
                        placeholder="Paste token here"
                    />
                </label>
                <label className="font-medium block">
                    <span className="mb-2 inline-block">SIZE</span>
                    <input
                        type="number"
                        min={1}
                        max={500}
                        step={1}
                        list="size-options"
                        value={size}
                        onChange={e => setSize(Number(e.target.value))}
                        className="w-40 px-3 py-2 bg-gray-800 text-white border border-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
                        placeholder="Enter or select size"
                    />
                    <datalist id="size-options">
                        {SIZE_OPTIONS.map(opt => (
                            <option key={opt} value={opt} />
                        ))}
                    </datalist>
                </label>
                <button
                    onClick={fetchDomains}
                    disabled={loading}
                    className="max-w-fit cursor-pointer px-4 py-2 rounded bg-green-700 hover:bg-green-800 text-white font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400"
                >
                    {loading ? "Fetching..." : "Fetch Domains"}
                </button>
            </div>
            {error && <div className="text-red-400 mb-2 font-semibold">{error}</div>}
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
                            className={
                                "px-4 py-2 rounded transition-colors " +
                                (copied
                                    ? "bg-green-500 text-white"
                                    : "bg-blue-900 hover:bg-blue-700 text-blue-100")
                            }
                        >
                            {copied ? "Copied!" : "Copy All"}
                        </button>
                        <button
                            onClick={handleLeadGen}
                            className="px-4 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white transition-colors"
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
        </main>
    );
}
