import time
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Input and output files
input_csv = "zillow_zipcode_75006.csv"
output_csv = "zillow_agnets_75006.csv"

# Function to extract realtor details
def scrape_realtor_details(driver, zip_code, profile_link):
    driver.get(profile_link)
    time.sleep(2)  # Simple sleep instead of scrolling/mouse movements
    
    try:
        # Locate the parent div first
        parent_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Flex-c11n-8-107-0__sc-n94bjd-0.jPTOfn"))
        )
        
        # Extract Realtor Name from h1 inside the parent div
        name_element = parent_div.find_element(By.CLASS_NAME, "Text-c11n-8-107-0__sc-aiai24-0")
        realtor_name = name_element.text.strip()
    except Exception:
        realtor_name = "N/A"
    
    try:
        # Extract Contact Number
        contact_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Flex-c11n-8-107-0__sc-n94bjd-0.ContactColumn__TextButtonFlexWrapper-sc-1ccc42g-0.fWizpG.bttiaK"))
        )
        contact = contact_element.find_element(By.CLASS_NAME, "StyledTextButton-c11n-8-107-0__sc-1nwmfqo-0")
        
        contact_number = contact.text.strip()
    except Exception:
        contact_number = "N/A"
    
    return {"ZIP Code": zip_code, "Realtor Name": realtor_name, "Contact Number": contact_number}

# Setup undetected Chrome options
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/122.0.0.0 Safari/537.36")
options.add_argument(f"user-agent={user_agent}")

# Launch undetected Chrome
driver = uc.Chrome(options=options)

# Read CSV and process each profile link
data = pd.read_csv(input_csv)
extracted_data = []

for index, row in data.iterrows():
    zip_code = row["ZIP Code"]
    profile_link = row["Profile Link"]
    
    if pd.isna(profile_link):
        continue  # Skip empty links
    
    realtor_info = scrape_realtor_details(driver, zip_code, profile_link)
    extracted_data.append(realtor_info)
    
    # Save incrementally
    pd.DataFrame([realtor_info]).to_csv(output_csv, mode='a', header=not pd.io.common.file_exists(output_csv), index=False)
    time.sleep(2)  # Delay between requests

# Close driver
driver.quit()
print(f"Scraping completed! Data saved to {output_csv}.")