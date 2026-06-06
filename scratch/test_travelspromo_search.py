import requests
from bs4 import BeautifulSoup
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def search_travelspromo(query):
    search_url = f"https://travelspromo.com/?s={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=15, verify=False)
        if response.status_code != 200:
            print("Failed to load search page:", response.status_code)
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        # In typical WordPress themes, search results are in h2.entry-title a or h2.post-title a or similar article links
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            title = a.get_text().lower()
            if "htm" in href or "tiket" in href or "wisata" in href:
                if any(word in title for word in query.lower().split()):
                    links.append((href, a.get_text().strip()))
        
        if not links:
            # Let's try more general link finding
            for article in soup.find_all("article"):
                a = article.find("a", href=True)
                if a:
                    links.append((a["href"], a.get_text().strip()))
                    
        # Remove duplicates
        seen = set()
        unique_links = []
        for href, title in links:
            if href not in seen and "travelspromo.com" in href:
                seen.add(href)
                unique_links.append((href, title))
                
        print(f"Found {len(unique_links)} potential articles for query '{query}':")
        for href, title in unique_links[:3]:
            print(f"- {title}: {href}")
            
        if unique_links:
            # Scrape the first match
            target_url = unique_links[0][0]
            print(f"Scraping content from: {target_url}")
            res = requests.get(target_url, headers=headers, timeout=15, verify=False)
            sub_soup = BeautifulSoup(res.text, "html.parser")
            text = sub_soup.get_text(" ", strip=True)
            
            # Find all prices
            found_prices = re.findall(r'Rp\.?\s?(\d{1,3}(?:\.\d{3})*)', text)
            prices = []
            for p_str in found_prices:
                price = int(p_str.replace(".", ""))
                if 2000 <= price <= 500000:
                    prices.append(price)
            if prices:
                print("Found prices:", prices)
                # Usually for tickets on travelspromo, the ticket price is one of the lowest numbers or most frequent.
                # Let's return the minimum or median of realistic prices.
                ticket_price = min(prices)
                print(f"Extracted ticket price: Rp {ticket_price}")
                return ticket_price
        return None
    except Exception as e:
        print("Error in travelspromo search:", e)
        return None

search_travelspromo("Borobudur")
search_travelspromo("Ullen Sentalu")
