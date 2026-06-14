# probe_ilo.py -- Diagnostic: inspect raw ILOSTAT API response structure
import sys, io, json, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

url    = "https://rplumber.ilo.org/data/indicator/"
params = {
    "id":          "UNE_2EAP_SEX_AGE_RT_A",
    "startPeriod": "2015",
    "endPeriod":   "2016",
    "format":      "json",
    "lang":        "en",
}

r = requests.get(url, params=params, timeout=60)
print(f"Status code : {r.status_code}")
print(f"Content-Type: {r.headers.get('Content-Type')}")

data = r.json()

# Print the top-level structure
print("\n--- Top-level type ---")
print(type(data))

if isinstance(data, list):
    print(f"List length: {len(data)}")
    print("First element keys:", list(data[0].keys()) if data else "empty")
elif isinstance(data, dict):
    print("Dict keys:", list(data.keys()))
    for k, v in data.items():
        print(f"  '{k}' -> type: {type(v).__name__}", end="")
        if isinstance(v, dict):
            print(f", keys: {list(v.keys())}")
        elif isinstance(v, list):
            print(f", length: {len(v)}")
            if v and isinstance(v[0], dict):
                print(f"    first item keys: {list(v[0].keys())}")
        else:
            print(f", value: {str(v)[:100]}")

# Save full raw response to file so we can inspect it
with open("ilo_raw_probe.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("\nFull response saved to ilo_raw_probe.json")