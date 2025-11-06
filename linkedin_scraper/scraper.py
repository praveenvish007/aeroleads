# scraper.py - Selenium Version (Bypasses "Sign in" wall)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time
import random
import sys

# ==============================
# CONFIG
# ==============================

PROFILES = [
    "https://www.linkedin.com/in/williamhgates",
    "https://www.linkedin.com/in/jeffweiner",
    "https://www.linkedin.com/in/reidhoffman",
    "https://www.linkedin.com/in/satyanadella",
    "https://www.linkedin.com/in/marissamayer",
    "https://www.linkedin.com/in/dhh",
    "https://www.linkedin.com/in/naval",
    "https://www.linkedin.com/in/pmarca",
    "https://www.linkedin.com/in/jasonfried",
    "https://www.linkedin.com/in/guillaumec",
    "https://www.linkedin.com/in/harry"
]

OUTPUT_CSV = "linkedin_public_profiles.csv"

# ==============================
# SETUP SELENIUM
# ==============================

def get_driver():
    options = Options()
    options.add_argument("--headless")  # Remove for debugging
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => false});")
    return driver

# ==============================
# SCRAPING FUNCTION
# ==============================

def scrape_profile_selenium(driver, url):
    try:
        print(f"Loading {url}...")
        driver.get(url)
        time.sleep(random.uniform(4, 7))  # Let JS load

        # Scroll to trigger lazy load
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        data = {
            "url": url,
            "name": "N/A",
            "headline": "N/A",
            "location": "N/A",
            "about": "N/A"
        }

        # Name
        try:
            name = driver.find_element(By.CSS_SELECTOR, "h1").text.strip()
            data["name"] = name
        except:
            pass

        # Headline
        try:
            headline = driver.find_element(By.CSS_SELECTOR, "h2").text.strip()
            if "Sign in" not in headline:
                data["headline"] = headline
        except:
            pass

        # Location
        try:
            location = driver.find_element(By.CSS_SELECTOR, "span.text-body-small").text.strip()
            data["location"] = location
        except:
            pass

        # About
        try:
            about = driver.find_element(By.CSS_SELECTOR, "section[id*='about'] .pv-text-entity").text.strip()
            data["about"] = about[:197] + "..." if len(about) > 200 else about
        except:
            pass

        # If still "Sign in", mark as blocked
        if "Sign in" in driver.page_source[:500]:
            print("Login wall detected")
            return None

        print(f"[SUCCESS] {data['name']} - {data['headline']}")
        return data

    except Exception as e:
        print(f"[ERROR] {url} → {e}")
        return None

# ==============================
# MAIN
# ==============================

def main():
    driver = get_driver()
    results = []

    print(f"Scraping {len(PROFILES)} profiles with Selenium...")
    for i, url in enumerate(PROFILES, 1):
        print(f"\n[{i}/{len(PROFILES)}] {url}")
        profile = scrape_profile_selenium(driver, url)
        if profile:
            results.append(profile)
        
        time.sleep(random.uniform(5, 10))  # Be gentle

    driver.quit()

    # Save CSV
    if results:
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["url", "name", "headline", "location", "about"])
            writer.writeheader()
            writer.writerows(results)
        print(f"\nSaved {len(results)} profiles to {OUTPUT_CSV}")
    else:
        print("No data scraped.")

if __name__ == "__main__":
    main()