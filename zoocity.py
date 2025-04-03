from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time

# Set up Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode (no browser UI)
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

# URL to scrape
url = "https://www.zoocity.hr/poslovnice"
driver.get(url)

# Wait for the page to load
time.sleep(3)

# Find all <a> tags inside <li> within the <ul class="locations-list">
location_links = driver.find_elements(By.CSS_SELECTOR, "ul.locations-list li a.location")

# Extract href attributes
hrefs = [link.get_attribute("href") for link in location_links]

# Save to CSV
df = pd.DataFrame(hrefs, columns=["URL"])
df.to_csv("zoocity_locations.csv", index=False, encoding="utf-8")

print(f"Saved {len(hrefs)} links to zoocity_locations.csv")

# Close the browser
driver.quit()
