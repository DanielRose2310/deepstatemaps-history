import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set Chrome options
chrome_options = Options()
chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=Service(), options=chrome_options)
driver.get("https://deepstatemap.live/")

WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".leaflet-container"))
)
driver.execute_script("document.querySelector('.cl-dialog')?.remove();")

clicked = 0
seen_urls = set()

print("[INFO] Starting repeated clicks and response capture...\n")

while True:
    try:
        # Click button[2]
        driver.execute_script("document.querySelectorAll('button.pager-button')[2]?.click();")
        clicked += 1
        print(f"[CLICK] #{clicked}")
    except Exception as e:
        print(f"[ERROR] Click failed: {e}")

    # Wait for network traffic
    time.sleep(1)

    # Get new logs
    logs = driver.get_log("performance")

    for entry in logs:
        try:
            msg = json.loads(entry["message"])["message"]
            if (
                msg["method"] == "Network.responseReceived"
                and "url" in msg["params"]["response"]
            ):
                url = msg["params"]["response"]["url"]
                mime = msg["params"]["response"].get("mimeType", "")
                if "api/history" in url and "geojson" in url and url not in seen_urls:
                    seen_urls.add(url)
                    print(f"[RESPONSE] {url}")
                    with open("geojson_urls.txt", "a", encoding="utf-8") as f:
                        f.write(url + "\n")
        except Exception:
            pass
