import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Setup Selenium ---
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920x1080")
# chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
chrome_options.page_load_strategy = "eager"  # Load essential resources only

# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Set a page load timeout
driver.set_page_load_timeout(60)

# Open the website
url = "https://www.prima-namjestaj.hr/poslovnice"

try:
    print("Opening website...")
    driver.get(url)
    time.sleep(5)  # Let JavaScript load

    # Debugging: Print Page Source (check if data is loaded dynamically)
    with open("debug_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

    print("Waiting for store list...")
    outer_div = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "lettered-store-list"))
    )

    # Find all store divs
    store_divs = outer_div.find_elements(By.CLASS_NAME, "widget.block.block-cms-link")

    if not store_divs:
        print("No stores found. Check if the class names have changed.")
    else:
        print(f"Found {len(store_divs)} stores.")

    # Extract store data
    store_data = []
    for div in store_divs:
        a_tag = div.find_element(By.TAG_NAME, "a")
        href = a_tag.get_attribute("href")
        title = a_tag.get_attribute("title")
        if href and title:
            store_data.append({"Href": href, "Title": title})

    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(store_data)
    df.to_csv("prima_stores.csv", index=False, encoding="utf-8")

    print("Data successfully scraped and saved to prima_stores.csv!")

except Exception as e:
    print("Error occurred:", str(e))

finally:
    driver.quit()
