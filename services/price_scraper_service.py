import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import urllib3
from flask import current_app
from models import db
from models.destination import Destination

# Disable SSL verification warnings for robustness
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_html_content(url, use_scraper_api=False, render_js=False):
    """
    Helper to fetch HTML content. 
    If use_scraper_api is True and SCRAPER_API_KEY is configured, it routes via ScraperAPI.
    """
    scraper_key = None
    try:
        scraper_key = current_app.config.get('SCRAPER_API_KEY')
    except Exception:
        # Fallback if outside app context
        pass

    if use_scraper_api and scraper_key:
        print(f"[ScraperAPI] Fetching (render={render_js}): {url}")
        params = {
            "api_key": scraper_key,
            "url": url
        }
        if render_js:
            params["render"] = "true"
        try:
            response = requests.get("http://api.scraperapi.com", params=params, headers=HEADERS, timeout=60, verify=False)
            if response.status_code == 200:
                return response.text
            else:
                print(f"[ScraperAPI] Returned status {response.status_code}, falling back to direct request...")
        except Exception as e:
            print(f"[ScraperAPI] Request failed: {e}, falling back to direct request...")

    # Direct request fallback
    print(f"[Direct] Fetching: {url}")
    response = requests.get(url, headers=HEADERS, timeout=20, verify=False)
    return response.text

# ==========================================
# 1. INDIVIDUAL STATIC SCRAPERS
# ==========================================

def scrape_gembiraloka():
    url = "https://gembiralokazoo.com/news/gembira-loka-zoo-umumkan-penyesuaian-harga-tiket-mulai-30-maret"
    html = get_html_content(url)
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    prices = [int(p.replace('.', '')) for p in re.findall(r'Rp\.?\s?(\d{1,3}(?:\.\d{3})*)', text)]
    if prices:
        return max(prices), "Official Gembira Loka Website"
    return None, None

def scrape_sonobudoyo():
    url = "https://sonobudoyo.jogjaprov.go.id/id/information"
    html = get_html_content(url)
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(" ", strip=True)
    prices = [int(p.replace('.', '')) for p in re.findall(r'Rp\.?\s?(\d{1,3}(?:\.\d{3})*)', text)]
    if prices:
        return max(prices), "Official Sonobudoyo Website"
    return None, None

def scrape_waduk_sermo():
    url = "https://waduksermo.com/karcis-masuk-waduk-sermo/"
    html = get_html_content(url)
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(" ", strip=True)
    prices = [int(p.replace('.', '')) for p in re.findall(r'Rp\.?\s?(\d{1,3}(?:\.\d{3})*)', text)]
    if prices:
        return max(prices), "Official Waduk Sermo Website"
    return None, None

def scrape_heha():
    url = "https://id.trip.com/travel-guide/attraction/patuk/heha-sky-view-142511061/?locale=id-ID&curr=IDR"
    html = get_html_content(url)
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(" ", strip=True)
    raw_prices = re.findall(r'Mulai dari\s+(\d+(?:\.\d+)?)', text)
    prices = []
    for p in raw_prices:
        try:
            harga = int(float(p))
            if 5000 <= harga <= 150000:
                prices.append(harga)
        except ValueError:
            pass
    if prices:
        return max(prices), "Trip.com (HeHa Sky View)"
    # Alternative direct fallback for HeHa Sky View
    return scrape_generic_travelspromo("Heha Sky View")

def scrape_dolandeso():
    url = "https://www.dolandesoboro.com/#pricing"
    html = get_html_content(url)
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(" ", strip=True)
    prices_k = re.findall(r'Rp\s?(\d+)\s?k', text, re.IGNORECASE)
    prices = []
    for p in prices_k:
        harga = int(p) * 1000
        if 10000 <= harga <= 500000:
            prices.append(harga)
    if prices:
        return max(prices), "Official DolaNDeso Website"
    return None, None

def scrape_merapi():
    url = "https://mgm.slemankab.go.id/harga-tiket/"
    html = get_html_content(url)
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(" ", strip=True)
    prices = [int(p.replace('.', '')) for p in re.findall(r'Rp\.?\s?(\d{1,3}(?:\.\d{3})*)', text)]
    prices = [p for p in prices if 1000 <= p <= 150000]
    if prices:
        return max(prices), "Official MGM Website"
    return None, None

def scrape_jeep_merapi():
    url = "https://jeepmerapitour.com/"
    html = get_html_content(url)
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator=" ", strip=True)
    prices = [int(p.replace('.', '').replace(',', '')) for p in re.findall(r'Rp\.?\s?(\d{1,3}(?:[.,]\d{3})+)', text)]
    prices = [p for p in prices if 10000 <= p <= 1000000]
    if prices:
        return min(prices), "jeepmerapitour.com" # Minimum package price
    return None, None

def scrape_tebing_breksi():
    url = "https://tebingbreksi.com/formulir-reservasi/"
    html = get_html_content(url)
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(" ", strip=True)
    prices = [int(p.replace('.', '')) for p in re.findall(r'Rp\s?([\d\.]+)', text)]
    prices = [p for p in prices if 2000 <= p <= 100000]
    if prices:
        return max(prices), "Official Tebing Breksi Website"
    return None, None

def scrape_pantai_timang():
    url = "https://pantaitimang.com/paket-wisata-timang/"
    html = get_html_content(url)
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(" ", strip=True)
    prices = [int(p.replace('.', '').replace(',', '')) for p in re.findall(r'Rp\.?\s?(\d{1,3}(?:[.,]\d{3})*)', text)]
    prices = [p for p in prices if 10000 <= p <= 500000]
    if prices:
        return min(prices), "Official Pantai Timang Website"
    return None, None

def scrape_parangtritis():
    url = "https://travelspromo.com/htm-wisata/pantai-parangtritis-bantul/"
    html = get_html_content(url)
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(" ", strip=True)
    prices = [int(p.replace('.', '').replace(',', '')) for p in re.findall(r'Rp\.?\s?(\d{1,3}(?:[.,]\d{3})*)', text)]
    prices = [p for p in prices if 5000 <= p <= 50000]
    if prices:
        return min(prices), "Travelspromo (Pantai Parangtritis)"
    return None, None

def scrape_pantai_glagah():
    url = "https://travelspromo.com/htm-wisata/pantai-glagah-kulon-progo/"
    html = get_html_content(url)
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(" ", strip=True)
    prices = [int(p.replace('.', '').replace(',', '')) for p in re.findall(r'Rp\.?\s?(\d{1,3}(?:[.,]\d{3})*)', text)]
    prices = [p for p in prices if 3000 <= p <= 50000]
    if prices:
        return min(prices), "Travelspromo (Pantai Glagah)"
    return None, None


# ==========================================
# 2. DYNAMIC SCRAPERS WITH SCRAPERAPI / STATIC FALLBACK
# ==========================================

def scrape_prambanan():
    """Candi Prambanan: GoersApp (Dynamic JS) / Fallback to travelspromo.com"""
    # Try dynamic via ScraperAPI
    today_str = datetime.now().strftime("%Y-%m-%d")
    url = f"https://widget.goersapp.com/venues/schedules/Candi-Prambanan--candiprambanan/{today_str}"
    
    scraper_key = None
    try:
        scraper_key = current_app.config.get('SCRAPER_API_KEY')
    except Exception:
        pass

    if scraper_key:
        try:
            html = get_html_content(url, use_scraper_api=True, render_js=True)
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()
            prices = [int(p.replace('.', '').replace(',', '')) for p in re.findall(r'(?:Rp|IDR)\s?(\d{1,3}(?:[.,]\d{3})*)', text)]
            prices = [p for p in prices if 20000 <= p <= 150000]
            if prices:
                return max(prices), "Goers (via ScraperAPI)"
        except Exception as e:
            print(f"[Warning] Goers ScraperAPI failed: {e}. Trying fallback...")
            
    # Fallback to static travelspromo
    print("[Fallback] Running fallback static scraper for Candi Prambanan...")
    fallback_url = "https://travelspromo.com/htm-wisata/candi-prambanan-sleman/"
    try:
        html = get_html_content(fallback_url)
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(" ", strip=True)
        prices = [int(p.replace('.', '').replace(',', '')) for p in re.findall(r'Rp\.?\s?(\d{1,3}(?:[.,]\d{3})*)', text)]
        prices = [p for p in prices if 25000 <= p <= 150000]
        if prices:
            # Standard domestic adult ticket is 50000
            if 50000 in prices:
                return 50000, "Travelspromo (Prambanan Fallback)"
            return min(prices), "Travelspromo (Prambanan Fallback)"
    except Exception as e:
        print(f"[Error] Prambanan fallback failed: {e}")
    
    # Ultimate hardcoded fallback to avoid crash
    return 50000, "Fallback Default"

def scrape_tamansari():
    """Taman Sari / Kraton: GlobalTix (Dynamic JS) / Fallback to travelspromo.com"""
    url = "https://kratonjogja-online.globaltix.com/attraction/kraton-taman-sari-35778"
    
    scraper_key = None
    try:
        scraper_key = current_app.config.get('SCRAPER_API_KEY')
    except Exception:
        pass

    if scraper_key:
        try:
            html = get_html_content(url, use_scraper_api=True, render_js=True)
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()
            prices = [int(p.replace('.', '').replace(',', '')) for p in re.findall(r'(?:Rp|IDR)\s?(\d{1,3}(?:[.,]\d{3})*)', text)]
            prices = [p for p in prices if 5000 <= p <= 50000]
            if prices:
                return max(prices), "GlobalTix (via ScraperAPI)"
        except Exception as e:
            print(f"[Warning] GlobalTix ScraperAPI failed: {e}. Trying fallback...")
            
    # Fallback to static travelspromo
    print("[Fallback] Running fallback static scraper for Taman Sari...")
    fallback_url = "https://travelspromo.com/htm-wisata/taman-sari-yogyakarta/"
    try:
        html = get_html_content(fallback_url)
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(" ", strip=True)
        prices = [int(p.replace('.', '').replace(',', '')) for p in re.findall(r'Rp\.?\s?(\d{1,3}(?:[.,]\d{3})*)', text)]
        prices = [p for p in prices if 5000 <= p <= 50000]
        if prices:
            if 15000 in prices:
                return 15000, "Travelspromo (Taman Sari Fallback)"
            return min(prices), "Travelspromo (Taman Sari Fallback)"
    except Exception as e:
        print(f"[Error] Taman Sari fallback failed: {e}")
        
    return 15000, "Fallback Default"

def scrape_ske():
    """SKE City Park: skecitypark.com (Dynamic JS) / Fallback to travelspromo.com"""
    url = "https://skecitypark.com/tickets"
    
    scraper_key = None
    try:
        scraper_key = current_app.config.get('SCRAPER_API_KEY')
    except Exception:
        pass

    if scraper_key:
        try:
            html = get_html_content(url, use_scraper_api=True, render_js=True)
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()
            prices = [int(p.replace('.', '').replace(',', '')) for p in re.findall(r'Rp\.?\s?(\d{1,3}(?:[.,]\d{3})*)', text)]
            prices = [p for p in prices if 10000 <= p <= 150000]
            if prices:
                return max(prices), "SKE Website (via ScraperAPI)"
        except Exception as e:
            print(f"[Warning] SKE ScraperAPI failed: {e}. Trying fallback...")
            
    # Fallback to static travelspromo
    print("[Fallback] Running fallback static scraper for SKE City Park...")
    fallback_url = "https://travelspromo.com/htm-wisata/sindu-kusuma-edupark-sleman/"
    try:
        html = get_html_content(fallback_url)
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(" ", strip=True)
        prices = [int(p.replace('.', '').replace(',', '')) for p in re.findall(r'Rp\.?\s?(\d{1,3}(?:[.,]\d{3})*)', text)]
        prices = [p for p in prices if 10000 <= p <= 150000]
        if prices:
            return max(prices), "Travelspromo (SKE Fallback)"
    except Exception as e:
        print(f"[Error] SKE fallback failed: {e}")
        
    return 30000, "Fallback Default"


# ==========================================
# 3. UNIVERSAL FALLBACK SCRAPER (TRAVELSPROMO SEARCH)
# ==========================================

def scrape_generic_travelspromo(destination_name):
    """
    Search travelspromo.com for the destination name,
    find the best matching article, and scrape it for ticket prices.
    """
    print(f"[Search] Searching travelspromo.com for: {destination_name}")
    search_url = f"https://travelspromo.com/?s={destination_name}"
    
    try:
        html = get_html_content(search_url)
        soup = BeautifulSoup(html, "html.parser")
        
        links = []
        # Find all result links
        for a in soup.find_all("a", href=True):
            href = a["href"]
            title = a.get_text().lower()
            if "travelspromo.com" in href and ("htm" in href or "tiket" in href or "wisata" in href):
                # Calculate matching words score
                query_words = destination_name.lower().split()
                matches = sum(1 for w in query_words if w in title)
                if matches > 0:
                    links.append((href, a.get_text().strip(), matches))
        
        # Sort by match score descending, then title length difference ascending
        links.sort(key=lambda x: (-x[2], len(x[1])))
        
        # Remove duplicates
        seen = set()
        unique_links = []
        for href, title, score in links:
            if href not in seen:
                seen.add(href)
                unique_links.append((href, title))
                
        if unique_links:
            target_url = unique_links[0][0]
            print(f"[Search] Matched article: {unique_links[0][1]} ({target_url})")
            
            sub_html = get_html_content(target_url)
            sub_soup = BeautifulSoup(sub_html, "html.parser")
            text = sub_soup.get_text(" ", strip=True)
            
            found_prices = re.findall(r'Rp\.?\s?(\d{1,3}(?:\.\d{3})*)', text)
            prices = []
            for p_str in found_prices:
                price = int(p_str.replace(".", ""))
                # Limit ticket prices to realistic bounds for tourist spots in IDR
                if 2000 <= price <= 250000:
                    prices.append(price)
                    
            if prices:
                # Often travelspromo pages contain multiple prices (children, packages, adults).
                # We return the minimum (usually standard entry) or most common. Let's return the minimum/standard price.
                return min(prices), f"Travelspromo ({unique_links[0][1]})"
                
    except Exception as e:
        print(f"[Error] Generic scraper failed for {destination_name}: {e}")
        
    return None, None


# ==========================================
# 4. DISPATCHER & DATABASE BRIDGE
# ==========================================

SCRAPER_MAPPING = {
    "gembira loka": scrape_gembiraloka,
    "prambanan": scrape_prambanan,
    "taman sari": scrape_tamansari,
    "kraton": scrape_tamansari,
    "keraton": scrape_tamansari,
    "sonobudoyo": scrape_sonobudoyo,
    "sermo": scrape_waduk_sermo,
    "heha": scrape_heha,
    "dolandeso": scrape_dolandeso,
    "gunungapi merapi": scrape_merapi,
    "museum merapi": scrape_merapi,
    "sindu kusuma": scrape_ske,
    "ske": scrape_ske,
    "jeep merapi": scrape_jeep_merapi,
    "tebing breksi": scrape_tebing_breksi,
    "breksi": scrape_tebing_breksi,
    "pantai timang": scrape_pantai_timang,
    "timang": scrape_pantai_timang,
    "pantai parangtritis": scrape_parangtritis,
    "parangtritis": scrape_parangtritis,
    "pantai glagah": scrape_pantai_glagah,
    "glagah": scrape_pantai_glagah,
}

def find_scraper_by_name(name):
    """
    Finds the appropriate scraper function based on name match.
    If no hardcoded scraper is matched, returns the universal travelspromo search scraper.
    """
    clean_name = name.lower().strip()
    
    # 1. Hardcoded mapping check
    for key, scraper_func in SCRAPER_MAPPING.items():
        if key in clean_name:
            print(f"[Match] Matched scraper for '{name}': {scraper_func.__name__}")
            return scraper_func
            
    # 2. Check for free zero-priced spots
    if "malioboro" in clean_name or "tugu" in clean_name or "nol kilometer" in clean_name:
        print(f"[Match] Matched free spot for '{name}'")
        return lambda: (0, "Gratis (Free Spot)")
        
    # 3. Universal Search scraper fallback
    print(f"[Match] No direct scraper matched for '{name}'. Using generic search fallback.")
    return lambda: scrape_generic_travelspromo(name)

def scrape_destination_price_by_id(dest_id):
    """
    Runs the appropriate scraper for a destination ID and updates the SQLite DB.
    """
    dest = Destination.query.get(dest_id)
    if not dest:
        return False, "Destinasi tidak ditemukan"
        
    scraper_func = find_scraper_by_name(dest.name)
    try:
        price, source = scraper_func()
        if price is not None:
            dest.price = price
            dest.price_last_scraped = datetime.now()
            dest.price_scrape_status = 'SUCCESS'
            db.session.commit()
            return True, f"Berhasil update: Rp {price} ({source})"
        else:
            dest.price_last_scraped = datetime.now()
            dest.price_scrape_status = 'FAILED'
            db.session.commit()
            return False, "Harga tidak ditemukan oleh parser"
    except Exception as e:
        dest.price_last_scraped = datetime.now()
        dest.price_scrape_status = 'FAILED'
        db.session.commit()
        return False, f"Scraper error: {str(e)}"

def scrape_all_destinations_prices():
    """
    Loops through all destinations in the DB and runs scraping.
    Called by the background scheduler.
    """
    print("[Daily] Starting daily automatic price sync...")
    destinations = Destination.query.all()
    success_count = 0
    
    for dest in destinations:
        # Skip Malioboro or other permanently free locations from heavy network queries if they are already 0
        if "malioboro" in dest.name.lower() and dest.price == 0:
            continue
            
        print(f"[Daily] Processing: {dest.name}")
        success, msg = scrape_destination_price_by_id(dest.id)
        if success:
            success_count += 1
            print(f"[Daily] SUCCESS - {dest.name}: {msg}")
        else:
            print(f"[Daily] FAILED - {dest.name}: {msg}")
            
    print(f"[Daily] Automatic price sync finished. Updated {success_count}/{len(destinations)} destinations.")
