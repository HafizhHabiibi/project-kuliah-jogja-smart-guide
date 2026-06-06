from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
import time

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# Enable performance logging to capture network requests
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

url = "https://widget.goersapp.com/venues/schedules/Candi-Prambanan--candiprambanan/2026-05-24"
driver.get(url)
print("Navigating to Goers widget...")
time.sleep(10) # Let it render and make API calls

# Parse logs
logs = driver.get_log("performance")
driver.quit()

print(f"Captured {len(logs)} performance logs.")

api_calls = []
for entry in logs:
    log_msg = json.loads(entry["message"])["message"]
    method = log_msg.get("method", "")
    params = log_msg.get("params", {})
    if "Network.requestWillBeSent" in method:
        request = params.get("request", {})
        req_url = request.get("url", "")
        if req_url:
            api_calls.append(req_url)

print("\nAll Captured Requests:")
for call in sorted(list(set(api_calls))):
    if "goers" in call or "api" in call or "graphql" in call:
        print("-", call)

