import sys
import os

# Add parent directory to path to allow importing app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from services.price_scraper_service import (
    find_scraper_by_name,
    scrape_tebing_breksi,
    scrape_gembiraloka,
    scrape_sonobudoyo,
    scrape_parangtritis,
    scrape_prambanan,
    scrape_tamansari,
    scrape_ske
)

app = create_app()

def test_scraper(name, scraper_func):
    print(f"\n--- Testing Scraper for: {name} ---")
    try:
        price, source = scraper_func()
        print(f"Result: Price = {price}, Source = {source}")
        if price is not None and isinstance(price, int):
            print("PASS: Correct format and type.")
        else:
            print("FAIL: Invalid price or type.")
    except Exception as e:
        print(f"FAIL: Scraper raised exception: {e}")


with app.app_context():
    # Test 1: Static site scraper - Gembira Loka
    test_scraper("Gembira Loka Zoo", scrape_gembiraloka)

    # Test 2: Static site scraper - Museum Sonobudoyo
    test_scraper("Museum Sonobudoyo", scrape_sonobudoyo)

    # Test 3: Static site scraper - Tebing Breksi
    test_scraper("Tebing Breksi", scrape_tebing_breksi)

    # Test 4: Static site scraper - Pantai Parangtritis
    test_scraper("Pantai Parangtritis", scrape_parangtritis)

    # Test 5: Dynamic scraper with static fallback - Candi Prambanan
    test_scraper("Candi Prambanan", scrape_prambanan)

    # Test 6: Dynamic scraper with static fallback - Taman Sari
    test_scraper("Taman Sari", scrape_tamansari)

    # Test 7: Dispatcher resolution (free spot)
    print("\n--- Testing Dispatcher: Malioboro (Free Spot) ---")
    func = find_scraper_by_name("Malioboro")
    price, source = func()
    print(f"Result: Price = {price}, Source = {source}")
    if price == 0:
        print("PASS: Correctly marked as Rp 0.")
    else:
        print("FAIL: Should be Rp 0.")

    # Test 8: Dispatcher resolution (unmapped destination, generic search)
    print("\n--- Testing Dispatcher: Candi Borobudur (Generic Search) ---")
    func = find_scraper_by_name("Candi Borobudur")
    price, source = func()
    print(f"Result: Price = {price}, Source = {source}")
    if price is not None and price > 0:
         print("PASS: Successfully resolved via generic search fallback.")
    else:
         print("FAIL: Could not resolve via generic search fallback.")

