import requests
from bs4 import BeautifulSoup
import re

def search_ddg_price(query):
    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    data = {
        "q": query
    }
    
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.post(url, headers=headers, data=data, timeout=10, verify=False)
        print("Status Code:", response.status_code)

        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("a", class_="result__snippet")
        
        print(f"Found {len(results)} snippets.")
        
        prices = []
        for res in results:
            text = res.get_text()
            print("- Snippet:", text[:120])
            # Regex to find price patterns like Rp 50.000 or Rp50.000 or Rp. 50.000
            found = re.findall(r'(?:Rp|IDR)\s?\.?\s?(\d{1,3}(?:\.\d{3})*)', text, re.IGNORECASE)
            for price_str in found:
                price = int(price_str.replace('.', ''))
                if 5000 <= price <= 250000:  # reasonable tourist ticket prices
                    prices.append(price)
                    
        if prices:
            print("Extracted prices:", prices)
            return min(prices)  # or max, or most frequent
        return None
    except Exception as e:
        print("Error:", e)
        return None

print("Result for Candi Prambanan:")
price = search_ddg_price("harga tiket masuk candi prambanan terbaru")
print("Final Price:", price)
