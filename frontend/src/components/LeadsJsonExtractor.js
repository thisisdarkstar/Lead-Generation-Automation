import { downloadAsTxt } from "@/utils/fileSaver";
import extractFromLeads from "@/utils/jsonUtils";
import React, { useEffect, useState, useRef } from "react";

const LOCAL_STORAGE_KEY = "leadsExtractorResults";
const JSON_FILE_KEY = "leadsExtractorJsonFile";
const TXT_FILE_KEY = "leadsExtractorTxtFile";
const PASTEBOX_KEY = "leadsJsonExtractorPasteBox";
const LEADGEN_RESULT_KEY = "leadGeneratorResults";

export default function LeadsJsonExtractor() {
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        const id = setTimeout(() => setMounted(true), 0);
        return () => clearTimeout(id);
    }, []);

    // Leads JSON upload state
    const [leads, setLeads] = useState(() => {
        if (typeof window === "undefined") return null;
        const saved = window.localStorage.getItem(JSON_FILE_KEY);
        try { return saved ? JSON.parse(saved) : null; } catch { return null; }
    });
    const [filenameJSON, setFilenameJSON] = useState(() => (
        (typeof window !== "undefined" && window.localStorage.getItem(JSON_FILE_KEY + "_name")) || ""
    ));

    // Domains TXT
    const [domains, setDomains] = useState(() => {
        if (typeof window === "undefined") return [];
        const saved = window.localStorage.getItem(TXT_FILE_KEY);
        try { return saved ? JSON.parse(saved) : []; } catch { return []; }
    });
    const [filenameTXT, setFilenameTXT] = useState(() => (
        (typeof window !== "undefined" && window.localStorage.getItem(TXT_FILE_KEY + "_name")) || ""
    ));
    const [pasteText, setPasteText] = useState(() => (
        (typeof window !== "undefined" && window.localStorage.getItem(PASTEBOX_KEY)) || ""
    ));
    const [key, setKey] = useState("");
    const [copied, setCopied] = useState(false);

    const [result, setResult] = useState(() => {
        if (typeof window === "undefined") return null;
        try {
            const saved = window.localStorage.getItem(LOCAL_STORAGE_KEY);
            return saved ? JSON.parse(saved) : null;
        } catch { return null; }
    });

    const jsonFileInputRef = useRef();
    const txtFileInputRef = useRef();

    // Persist uploaded JSON/filename
    useEffect(() => {
        if (typeof window === "undefined") return;
        if (leads) {
            window.localStorage.setItem(JSON_FILE_KEY, JSON.stringify(leads));
            window.localStorage.setItem(JSON_FILE_KEY + "_name", filenameJSON);
        } else {
            window.localStorage.removeItem(JSON_FILE_KEY);
            window.localStorage.removeItem(JSON_FILE_KEY + "_name");
        }
    }, [leads, filenameJSON]);

    // Persist uploaded TXT/filename
    useEffect(() => {
        if (typeof window === "undefined") return;
        if (domains.length > 0) {
            window.localStorage.setItem(TXT_FILE_KEY, JSON.stringify(domains));
            window.localStorage.setItem(TXT_FILE_KEY + "_name", filenameTXT);
        } else {
            window.localStorage.removeItem(TXT_FILE_KEY);
            window.localStorage.removeItem(TXT_FILE_KEY + "_name");
        }
    }, [domains, filenameTXT]);
    useEffect(() => {
        if (typeof window === "undefined") return;
        window.localStorage.setItem(PASTEBOX_KEY, pasteText);
    }, [pasteText]);
    useEffect(() => {
        if (typeof window !== "undefined") {
            if (result) window.localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(result));
            else window.localStorage.removeItem(LOCAL_STORAGE_KEY);
        }
    }, [result]);

    const handleLeads = async (e) => {
        setFilenameJSON(e.target.files[0]?.name || "");
        const fileText = await e.target.files[0].text();
        setLeads(JSON.parse(fileText));
    };

    const handleClearJSON = () => {
        setLeads(null);
        setFilenameJSON("");
        if (typeof window !== "undefined") {
            window.localStorage.removeItem(JSON_FILE_KEY);
            window.localStorage.removeItem(JSON_FILE_KEY + "_name");
        }
    };

    const handleDomains = async (e) => {
        setFilenameTXT(e.target.files[0]?.name || "");
        const fileText = await e.target.files[0].text();
        setDomains(fileText.split('\n').map(x => x.trim()).filter(Boolean));
    };

    const handleClearTXT = () => {
        setDomains([]);
        setFilenameTXT("");
        if (typeof window !== "undefined") {
            window.localStorage.removeItem(TXT_FILE_KEY);
            window.localStorage.removeItem(TXT_FILE_KEY + "_name");
        }
    };

    const handlePasteBoxClear = () => {
        setPasteText("");
        if (typeof window !== "undefined") window.localStorage.removeItem(PASTEBOX_KEY);
    };

    const handleExtract = () => {
        const useDomains = pasteText.trim() ? pasteText.split('\n').map(x => x.trim()).filter(Boolean) : domains;
        if (!leads || !useDomains.length) return;
        setResult(extractFromLeads(leads, useDomains));
        setCopied(false);
    };

    const handleClearAll = () => {
        setLeads(null);
        setDomains([]);
        setPasteText("");
        setResult(null);
        setKey("");
        setCopied(false);
        setFilenameJSON("");
        setFilenameTXT("");
        if (typeof window !== "undefined") {
            window.localStorage.removeItem(LOCAL_STORAGE_KEY);
            window.localStorage.removeItem(JSON_FILE_KEY);
            window.localStorage.removeItem(JSON_FILE_KEY + "_name");
            window.localStorage.removeItem(TXT_FILE_KEY);
            window.localStorage.removeItem(TXT_FILE_KEY + "_name");
            window.localStorage.removeItem(PASTEBOX_KEY);
        }
    };

    // --- Load from LeadGenerator handler ---
    const handleLoadFromLeadGen = () => {
        if (typeof window !== "undefined") {
            const saved = window.localStorage.getItem(LEADGEN_RESULT_KEY);
            if (saved) {
                try {
                    setLeads(JSON.parse(saved));
                    setFilenameJSON("Loaded from Lead Generator");
                } catch {
                    alert("Couldn't load or parse results from Lead Generator!");
                }
            } else {
                alert("No results in localStorage yet.");
            }
        }
    };

    if (!mounted) {
        return (
            <main className="max-w-4xl mx-auto p-10">
                <h2 className="text-3xl font-bold mb-6">Extract From JSON</h2>
                <div className="text-gray-400">Loading...</div>
            </main>
        );
    }

    return (
        <main className="max-w-4xl mx-auto p-10">
            <h2 className="text-3xl font-bold mb-6">Extract From JSON</h2>
            <div className="flex flex-wrap gap-4 mb-6">
                <div className="flex flex-col">
                    <div className="relative flex items-center mb-2">
                        <button type="button" className="px-4 py-2 rounded bg-blue-700 hover:bg-blue-800 text-white font-medium mr-3 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400"
                            onClick={() => jsonFileInputRef.current && jsonFileInputRef.current.click()}>
                            Choose JSON File
                        </button>
                        <input ref={jsonFileInputRef} type="file" accept=".json" onChange={handleLeads}
                            className="absolute left-0 top-0 w-full h-full opacity-0 cursor-pointer"
                            style={{ position: "absolute", left: 0, top: 0, width: "170px", height: "100%", opacity: 0, cursor: "pointer" }}
                        />
                        <button
                            onClick={handleLoadFromLeadGen}
                            className="px-3 py-2 rounded cursor-pointer bg-blue-700 hover:bg-blue-900 text-white font-medium ml-2"
                        >Load from Lead Generator</button>
                    </div>
                    <div className="flex gap-2 items-center">
                        <span className="ml-2 text-gray-400 text-sm">{filenameJSON ? filenameJSON : "leads.json"}</span>
                        {filenameJSON && (
                            <button onClick={handleClearJSON}
                                className="px-2 py-1 rounded bg-red-700 hover:bg-red-800 text-white text-xs">Clear JSON</button>
                        )}
                    </div>
                </div>
                <div className="flex flex-col">
                    <div className="relative flex items-center mb-2">
                        <button type="button" className="px-4 py-2 rounded bg-blue-700 hover:bg-blue-800 text-white font-medium mr-3 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400"
                            onClick={() => txtFileInputRef.current && txtFileInputRef.current.click()}>
                            Choose TXT File
                        </button>
                        <input ref={txtFileInputRef} type="file" accept=".txt" onChange={handleDomains}
                            className="absolute left-0 top-0 w-full h-full opacity-0 cursor-pointer"
                            style={{ position: "absolute", left: 0, top: 0, width: "160px", height: "100%", opacity: 0, cursor: "pointer" }}
                        />
                    </div>
                    <div className="flex gap-2 items-center">
                        <span className="ml-2 text-gray-400 text-sm">{filenameTXT ? filenameTXT : "domains.txt"}</span>
                        {filenameTXT && (
                            <button onClick={handleClearTXT}
                                className="px-2 py-1 rounded bg-red-700 hover:bg-red-800 text-white text-xs">Clear TXT</button>
                        )}
                    </div>
                </div>
                <div className="">
                    <button
                        onClick={handleExtract}
                        className="cursor-pointer px-4 py-2 rounded bg-green-700 hover:bg-green-800 text-white font-medium">Extract!</button>
                </div>
                <div className="flex-1" />
                <button
                    onClick={handleClearAll}
                    className="px-4 py-2 rounded bg-red-800 hover:bg-red-700 text-white transition-colors self-start">Clear All</button>
            </div>

            <div className="mb-6">
                <label className="block text-base font-medium mb-1">Paste Domains (one per line) <span className="text-xs text-gray-400">(Overrides TXT upload if filled)</span></label>
                <textarea rows={5} value={pasteText} onChange={e => setPasteText(e.target.value)}
                    placeholder="domain1.com\ndomain2.com"
                    className="w-full p-2 bg-gray-900 text-green-200 border rounded mb-2"
                />
                <button
                    onClick={handlePasteBoxClear}
                    className="px-3 py-1 rounded bg-red-700 hover:bg-red-800 text-white text-sm">Clear PasteBox</button>
            </div>

            {result && (

                <div className="bg-gray-900 p-4 rounded max-h-96 min-w-[420px] min-h-64 overflow-y-auto shadow">
                    <ul>
                        {result.map((item, idx) => (
                            <li key={item.domain || idx} className="mb-3">
                                <details>
                                    <summary className="font-bold cursor-pointer text-green-300">
                                        {item.domain || "Domain"}{" "}
                                        {item.count !== undefined && (
                                            <span className="text-xs text-gray-400 ml-2">({item.count})</span>
                                        )}
                                        {item.error && (
                                            <span className="text-red-400 text-xs ml-2">[Error]</span>
                                        )}
                                    </summary>
                                    <ul className="ml-8 mt-2">
                                        {item.error && <li className="text-red-400">{item.error}</li>}
                                        {item.entries && Array.isArray(item.entries) && item.entries.map((entry, vi) => (
                                            <li key={vi} className="mb-2 bg-gray-800 p-2 rounded">
                                                {Object.entries(entry).map(([k, v]) =>
                                                    k === "url" && typeof v === "string" && v.match(/^https?:\/\//) ? (
                                                        <div key={k}>
                                                            <span className="text-gray-400">{k}: </span>
                                                            <a href={v} target="_blank" rel="noopener noreferrer"
                                                                className="text-blue-400 underline break-all">{v}</a>
                                                        </div>
                                                    ) : (
                                                        <div key={k}>
                                                            <span className="text-gray-400">{k}: </span>
                                                            <span className="text-green-100 break-all">{String(v)}</span>
                                                        </div>
                                                    )
                                                )}
                                            </li>
                                        ))}
                                    </ul>
                                </details>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </main>
    );
}
