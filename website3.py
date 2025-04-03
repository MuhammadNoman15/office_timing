import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Start the browser
driver = webdriver.Chrome()
driver.get("https://www.studenac.hr/trgovine")
driver.maximize_window()

# Pause so user can translate page if needed















































































































input("Translate the page if needed. Then press Enter to continue...")

# Wait until the UL container #storeList is present
wait = WebDriverWait(driver, 15)
store_list = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul#storeList")))

# Optional: scroll through the container if needed, or just let Selenium see all
# If the page loads all stores dynamically, you might need a scroll approach
# We'll do a simple approach first. If you find it doesn't load everything,
# implement a scrolling loop like in your Plodine script.

# Find all li elements
li_elements = store_list.find_elements(By.CSS_SELECTOR, "li.marketlisting__item")

all_stores = []

for li_el in li_elements:
    # Store ID or any data attributes
    data_store_id = li_el.get_attribute("data-store-id")
    
    # openOnSunday
    open_on_sunday_str = li_el.get_attribute("data-open-on-sunday")  # e.g. "true" or "false"
    open_on_sunday = (open_on_sunday_str.lower() == "true")
    
    # openNow
    open_now_str = li_el.get_attribute("data-open-now")  # e.g. "true" or "false"
    open_now = (open_now_str.lower() == "true")

    # Title / Address from h3.card__title
    try:
        title_el = li_el.find_element(By.CSS_SELECTOR, "h3.card__title")
        store_title = title_el.text.strip()
    except:
        store_title = ""

    # The open hours from p.workhours (e.g. "Open: 07:00-21:00")
    try:
        hours_el = li_el.find_element(By.CSS_SELECTOR, "p.workhours")
        store_hours = hours_el.text.strip()  # might store the entire string
    except:
        store_hours = ""

    # The link (href) from the a inside .card__cta
    try:
        cta_el = li_el.find_element(By.CSS_SELECTOR, ".card__cta a")
        store_link = cta_el.get_attribute("href")
    except:
        store_link = ""

    data = {

        "storeLink": store_link
    }
    all_stores.append(data)

# Print results to console (optional)
for store in all_stores:
    print(store)

# ---- SAVE TO CSV ----
with open("studenac_stores.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = ["storeId", "storeTitle", "storeHours", "openNow", "openOnSunday", "storeLink"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_stores)

# Done
driver.quit()
