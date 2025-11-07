// Utility to extract all entries from leads.json per domain
export default function extractFromLeads(leadsObj, domains) {
    return domains.map(domain => {
        const entries = leadsObj[domain];
        if (!entries) return { domain, error: "No entries found" };
        return { domain, entries, count: entries.length };
    });
}
