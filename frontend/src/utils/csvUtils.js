// extracts only domain header values from csv file
export default function parseCSV(text) {
  const lines = text.split(/\r?\n/).filter(Boolean);
  if (!lines.length) return [];
  const headers = lines[0].toLowerCase().split(",");
  let domainIdx = headers.findIndex((h) => h.trim() === "domain");
  if (domainIdx === -1) {
    domainIdx = lines[0]
      .split(",")
      .findIndex((h) => h.trim().toLowerCase() === "domain");
    if (domainIdx === -1) return [];
  }
  const domains = new Set();
  lines.slice(1).forEach((line) => {
    const fields = line.split(",");
    const val = fields[domainIdx];
    if (val) domains.add(val.trim());
  });
  return Array.from(domains).sort();
}