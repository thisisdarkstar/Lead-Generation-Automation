import requests
import json

url = "https://nk-dashboard-1.grayriver-ffcf7337.westus.azurecontainerapps.io/getmysocialallocations"
params = {"page": "0", "size": "200", "sort": "{}", "filter": "{}", "search": ""}

headers = {
    "accept": "application/json",
    "authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJpLmFybmFiQG5hbWVrYXJ0LmNvbSIsInByb3ZpZGVyIjoiR09PR0xFIiwicm9sZXMiOlsiVXNlciIsInNvY2lhbF9hZ2VudCJdLCJpc3MiOiJua2Rhc2hib2FyZCIsImV4cCI6MTc2MTUwMDE4MywiZ2l2ZW5fbmFtZSI6IkFybmFiIiwiaWF0IjoxNzYxNDk5MjgzLCJmYW1pbHlfbmFtZSI6Ik1haXR5IiwiZW1haWwiOiJpLmFybmFiQG5hbWVrYXJ0LmNvbSJ9.39sW9qO9feBW05TJYh7z5IP0_M8KGaz9WRZUTvYn4sU",
    "origin": "https://app.namekart.com",
    "x-auth-provider": "GOOGLE",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
}

response = requests.get(url, headers=headers, params=params)
print(response)
print(response.status_code)

if response.ok:
    data = response.json()
    with open("domains.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("Saved as domains.json!")

    # Extract domains from JSON
    domains = set()
    for entry in data.get("content", []):
        # Add domainName if exists
        if "domainName" in entry and entry["domainName"]:
            domains.add(entry["domainName"])
        # Add presentDomain.domain if present
        present_domain = entry.get("presentDomain", {}).get("domain")
        if present_domain:
            domains.add(present_domain)

    # Write unique domains to domains.txt
    with open("domains.txt", "w", encoding="utf-8") as out:
        for domain in sorted(domains):
            out.write(domain + "\n")
    print(f"Wrote {len(domains)} domains to domains.txt!")
else:
    print(response.text)
