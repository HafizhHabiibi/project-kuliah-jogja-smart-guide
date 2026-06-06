import requests

url = "https://widget.goersapp.com/venues/schedules/Candi-Prambanan--candiprambanan/2026-05-24"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print("Status Code:", response.status_code)
    print("Content length:", len(response.text))
    # Write to a temp file or look for JSON patterns
    with open("scratch/goers_temp.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("HTML saved to scratch/goers_temp.html")
except Exception as e:
    print("Error:", e)
