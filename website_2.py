import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_hours(div_text: str) -> str:
    # e.g. "Monday - Friday: 07:00-22:00" -> "07:00-22:00"
    parts = div_text.split(":", 1)
    if len(parts) > 1:
        return parts[1].strip()
    return div_text.strip()

driver = webdriver.Chrome()
driver.get("https://www.plodine.hr/supermarketi")
driver.maximize_window()

input("Translate the page if needed. Then press Enter to continue...")

# Wait for the container
wait = WebDriverWait(driver, 15)
container = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div.mapfilter__listing.cf.js_ps.ps.ps--active-y"))
)

# SCROLL THE CONTAINER
last_height = driver.execute_script("return arguments[0].scrollHeight;", container)
while True:
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", container)
    time.sleep(1)
    new_height = driver.execute_script("return arguments[0].scrollHeight;", container)
    if new_height == last_height:
        break
    last_height = new_height

# GRAB ALL LI
store_elements = container.find_elements(By.CSS_SELECTOR, "li.market")

all_stores = []

for li_el in store_elements:
    # Optionally scroll each li into view
    driver.execute_script("arguments[0].scrollIntoView(true);", li_el)
    time.sleep(0.3)  # slight pause

    # storeName
    try:
        name_el = li_el.find_element(By.CSS_SELECTOR, "h2.market__title a")
        store_name = name_el.text.strip()
    except:
        store_name = ""

    # address lines
    try:
        address_lines = li_el.find_elements(By.CSS_SELECTOR, ".market__location p")
        if len(address_lines) >= 2:
            address_1 = address_lines[0].text.strip()
            address_2 = address_lines[1].text.strip()
        else:
            address_1, address_2 = "", ""
    except:
        address_1, address_2 = "", ""

    full_address = (address_1 + ", " + address_2).strip(", ")

    # openOnSunday
    try:
        open_sun_str = li_el.get_attribute("data-open-on-sunday")
        open_on_sunday = (open_sun_str.lower() == "true")
    except:
        open_on_sunday = False

    # Work hours
    mon_fri, sat, sun = "", "", ""
    try:
        workhours_div = li_el.find_element(By.CSS_SELECTOR, ".market__workhours")
        rows = workhours_div.find_elements(By.TAG_NAME, "div")
        if len(rows) >= 4:
            # skip rows[0], it’s the label
            mon_fri = get_hours(rows[1].text)
            sat     = get_hours(rows[2].text)
            sun     = get_hours(rows[3].text)
    except:
        pass

    data = {
        "storeName": store_name,
        "address": full_address,
        "mondayFriday": mon_fri,
        "saturday": sat,
        "sunday": sun,
        "openOnSunday": open_on_sunday
    }
    all_stores.append(data)

# Print results to console (optional)
for s in all_stores:
    print(s)

# ---- SAVE TO CSV ----
with open("plodine_stores.csv", "w", newline="", encoding="utf-8") as f:
    # Option 1: Using csv.DictWriter
    fieldnames = ["storeName", "address", "mondayFriday", "saturday", "sunday", "openOnSunday"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_stores)

driver.quit()
