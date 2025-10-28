export default function extractDomainsFromHtml(html) {
    const domainPattern = /(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}/;
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, "text/html");
    const out = new Set();
    Array.from(doc.querySelectorAll('div[class*="MuiStack-root"]')).forEach(div => {
        div.querySelectorAll('p[class*="MuiTypography-body2"]').forEach(p => {
            const text = p.textContent.trim();
            if (domainPattern.test(text)) out.add(text);
        });
    });
    return Array.from(out).sort();
}