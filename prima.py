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
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
chrome_options.page_load_strategy = "eager"  # Load essential resources only

# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Load the CSV file and take only the first 5 records
df = pd.read_csv("prima_stores.csv").head(5)  # Read first 5 rows

store_details = []

for index, row in df.iterrows():
    store_url = row["Href"]
    store_name = row["Title"]

    try:
        print(f"Scraping {store_name} -> {store_url}")
        driver.get(store_url)
        time.sleep(3)  # Short delay for JavaScript to load

        # Extract address from <div class="single-store-address"> and its <address> tag
        try:
            store_address_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "single-store-address"))
            )
            address_tag = store_address_div.find_element(By.TAG_NAME, "address")
            address = address_tag.text.strip()
        except:
            address = "N/A"

        # Extract phone number from <a class="store-tel"> and its <span class="text">
        try:
            phone_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "store-tel"))
            )
            phone_number = phone_element.find_element(By.TAG_NAME, "span").text.strip()
        except:
            phone_number = "N/A"

        store_details.append({
            "Store Name": store_name,
            "URL": store_url,
            "Address": address,
            "Phone Number": phone_number
        })

    except Exception as e:
        print(f"Error scraping {store_name}: {str(e)}")

# Save results to CSV
df_output = pd.DataFrame(store_details)
df_output.to_csv("prima_store_details.csv", index=False, encoding="utf-8")

print("Scraping complete! Data saved to prima_store_details.csv")

# Close browser
driver.quit()
