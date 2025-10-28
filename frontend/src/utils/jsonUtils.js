// Utility to extract desired keys from leads.json per domain
export default function extractFromLeads(leadsObj, domains, key) {
    return domains.map(domain => {
        const entries = leadsObj[domain];
        if (!entries) return { domain, error: "No entries found" };
        if (key) {
            const values = entries.filter(e => key in e).map(e => e[key]);
            return { domain, key, values, count: values.length };
        }
        return { domain, entries, count: entries.length };
    });
}