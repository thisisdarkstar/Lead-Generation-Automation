import { downloadAsTxt } from "@/utils/fileSaver";
import extractDomainsFromHtml from "@/utils/htmlUtils";
import React, { useEffect, useRef, useState } from "react";

const LOCAL_STORAGE_KEY = "htmlExtractorDomainsStructured";

export default function HtmlDomainExtractor({ onExtracted }) {
    const [html, setHtml] = useState("");
    const [domains, setDomains] = useState(() => {
        if (typeof window === "undefined") return [];
        const saved = window.localStorage.getItem(LOCAL_STORAGE_KEY);
        if (saved) {
            try { return JSON.parse(saved); }
            catch { return []; }
        }
        return [];
    });
    const [filename, setFilename] = useState("");
    const [error, setError] = useState("");
    const [copied, setCopied] = useState(false);
    const [mode, setMode] = useState("upload");

    const fileInputRef = useRef();

    useEffect(() => {
        if (typeof window === "undefined") return;
        if (domains.length)
            window.localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(domains));
        else
            window.localStorage.removeItem(LOCAL_STORAGE_KEY);
    }, [domains]);

    const processHtml = (inputHtml) => {
        try {
            // extractDomainsFromHtml should return an array of strings
            const found = extractDomainsFromHtml(inputHtml);
            setDomains(found);
            if (onExtracted) onExtracted(found);
            setError("");
        } catch (err) {
            setError("Failed to parse or extract domains.");
            setDomains([]);
        }
    };

    const handleUpload = async (e) => {
        setError("");
        setCopied(false);
        if (!e.target.files[0]) return;
        setFilename(e.target.files[0].name);
        const text = await e.target.files[0].text();
        setHtml(text);
        processHtml(text);
    };

    const handlePaste = (e) => {
        setError("");
        setFilename("");
        setCopied(false);
        setHtml(e.target.value);
        processHtml(e.target.value);
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
        setHtml("");
        setError("");
        setCopied(false);
        setFilename("");
        if (typeof window !== "undefined") window.localStorage.removeItem(LOCAL_STORAGE_KEY);
    };

    return (
        <main className="max-w-4xl mx-auto p-10">
            <h2 className="text-3xl font-bold mb-6">Extract Domains from HTML</h2>
            <div className="mb-4 flex gap-4">
                <button
                    className={`px-3 py-2 rounded ${mode === "upload" ? "bg-blue-800 text-white" : "bg-gray-700 text-gray-100"}`}
                    onClick={() => setMode("upload")}
                >
                    Upload HTML
                </button>
                <button
                    className={`px-3 py-2 rounded ${mode === "paste" ? "bg-blue-800 text-white" : "bg-gray-700 text-gray-100"}`}
                    onClick={() => setMode("paste")}
                >
                    Paste HTML
                </button>
            </div>
            {mode === "upload" && (
                <label className="text-base font-medium mb-2 block">
                    <span className="mb-2 inline-block">Choose File</span>
                    <div className="relative flex items-center">
                        <button
                            type="button"
                            className="px-4 py-2 rounded bg-blue-700 hover:bg-blue-800 text-white font-medium mr-3 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400"
                            tabIndex={-1}
                            onClick={() => fileInputRef.current && fileInputRef.current.click()}
                        >
                            Choose File
                        </button>
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".html,.htm,text/html"
                            onChange={handleUpload}
                            className="absolute left-0 top-0 w-full h-full opacity-0 cursor-pointer"
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
            )}
            {mode === "paste" && (
                <textarea
                    rows={8}
                    className="w-full p-2 bg-gray-900 text-green-200 border rounded mb-2"
                    placeholder="Paste HTML here…"
                    value={html}
                    onChange={handlePaste}
                />
            )}
            {error && <div className="text-red-400 mb-2">{error}</div>}
            {domains.length > 0 && (
                <>
                    <h3 className="text-xl font-semibold mt-6 mb-2">
                        Extracted Domains <span className="text-gray-400 font-normal">({domains.length})</span>
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
