import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Map Croatian day names to English
DAY_MAP = {
    "Ponedjeljak": "Monday",
    "Utorak": "Tuesday",
    "Srijeda": "Wednesday",
    "Četvrtak": "Thursday",
    "Petak": "Friday",
    "Subota": "Saturday",
    "Nedjelja": "Sunday",
}

# Fields we want in the output
OUTPUT_FIELDS = [
    "storeLink",
    "storeName",
    "dateRange",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

def setup_driver():
    """Setup and return a Selenium WebDriver instance with proper configurations."""
    options = Options()
    # options.add_argument("--headless")  # Remove this if you want UI mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def scrape_store_hours(driver, link):
    """Scrape store data from a given link."""
    driver.get(link)

    # Allow time for dynamic elements to load
    time.sleep(5)

    # Ensure .marketsingle__workhours exists
    try:
        wait = WebDriverWait(driver, 30)
        container = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".marketsingle__workhours"))
        )
    except:
        print(f"Could not find .marketsingle__workhours for {link}, skipping...")
        return {"storeLink": link}

    # Get the date range
    date_range = ""
    try:
        title_el = container.find_element(By.CSS_SELECTOR, "h2.marketsingle__title")
        small_el = title_el.find_element(By.TAG_NAME, "small")
        date_range = small_el.text.strip()
    except:
        pass

    # Get the store name
    store_name = ""
    try:
        meta_el = driver.find_element(By.CSS_SELECTOR, ".marketsingle__meta h2")
        store_name = meta_el.text.strip()
    except:
        pass

    # Get opening hours
    day_times = {day: "" for day in DAY_MAP.values()}

    try:
        li_elements = container.find_elements(By.CSS_SELECTOR, ".marketsingle__columns .marketsingle__column ul li")
        for li_el in li_elements:
            full_text = li_el.text.strip()
            try:
                strong_el = li_el.find_element(By.TAG_NAME, "strong")
                hours_str = strong_el.text.strip()
            except:
                hours_str = ""

            cro_day = full_text.split(":")[0].strip()
            eng_day = DAY_MAP.get(cro_day, cro_day)

            if eng_day in day_times:
                day_times[eng_day] = hours_str

    except:
        pass

    # Create output row
    return {
        "storeLink": link,
        "storeName": store_name,
        "dateRange": date_range,
        **day_times,
    }

def main():
    driver = setup_driver()

    with open("studenac_stores.csv", "r", encoding="utf-8") as f_in, \
         open("studenac_store_hours.csv", "w", newline="", encoding="utf-8") as f_out:

        reader = csv.DictReader(f_in)
        writer = csv.DictWriter(f_out, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()

        for idx, row in enumerate(reader, 1):
            link = row.get("storeLink", "").strip()
            if not link:
                continue

            print(f"Scraping store #{idx}: {link}")
            store_data = scrape_store_hours(driver, link)
            print("Scraped:", store_data)

            writer.writerow(store_data)

    driver.quit()

if __name__ == "__main__":
    main()
