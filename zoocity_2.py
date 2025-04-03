from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import re
from urllib.parse import urlparse

def collect_links():
    """Scrape all location links from the main page and return a list of URLs."""
    url = "https://www.zoocity.hr/poslovnice"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(3)  # Allow page to load

    # Find all location links
    location_links = driver.find_elements(By.CSS_SELECTOR, "ul.locations-list li a.location")
    hrefs = [link.get_attribute("href") for link in location_links]

    driver.quit()
    return hrefs

def extract_branch_data(url):
    """Scrape branch details from a given location URL."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(3)  # Allow page to load

    # Extract branch name from URL
    branch_name = urlparse(url).path.strip("/").split("/")[-1]

    # Find location info div
    try:
        location_info = driver.find_element(By.CLASS_NAME, "location-info")

        # Extract phone number
        try:
            phone_element = location_info.find_element(By.XPATH, './/p/strong[contains(text(), "Phone")]/following-sibling::a')
            branch_phone = phone_element.text.strip() if phone_element else "N/A"
        except:
            branch_phone = "N/A"

        # Extract working hours
        try:
            hours_element = location_info.find_element(By.XPATH, './/p/strong[contains(text(), "Working hours")]/following-sibling::font')
            working_hours_text = hours_element.text.strip() if hours_element else ""
        except:
            working_hours_text = ""

    except:
        branch_phone = "N/A"
        working_hours_text = ""

    driver.quit()

    # Parse working hours
    hours = parse_working_hours(working_hours_text)

    return {
        "Branch Name": branch_name,
        "Branch Phone": branch_phone,
        **hours
    }

def parse_working_hours(text):
    """Convert Croatian working hours text into a structured format."""

    # Croatian Day Mapping
    DAY_MAP = {
        "Pon": "Ponedjeljak",
        "Uto": "Utorak",
        "Sri": "Srijeda",
        "Čet": "Četvrtak",
        "Pet": "Petak",
        "Sub": "Subota",
        "Ned": "Nedjelja",
    }

    # Initialize empty hours structure
    hours_data = {f"{day}_start": "N/A" for day in DAY_MAP.values()}
    hours_data.update({f"{day}_end": "N/A" for day in DAY_MAP.values()})

    # Match pattern: "Pon - Sub: 08:00 - 20:00"
    match = re.search(r"(\w{3}) - (\w{3}): (\d{2}:\d{2}) - (\d{2}:\d{2})", text)
    if match:
        start_day, end_day, start_time, end_time = match.groups()
        
        # Convert short form days to full Croatian names
        start_day_full = DAY_MAP.get(start_day, start_day)
        end_day_full = DAY_MAP.get(end_day, end_day)

        found = False
        for short, full_day in DAY_MAP.items():
            if full_day == start_day_full:
                found = True
            if found:
                hours_data[f"{full_day}_start"] = start_time
                hours_data[f"{full_day}_end"] = end_time
            if full_day == end_day_full:
                break

    return hours_data


def main():
    """Main function to run the scraping process."""
    print("Collecting all links...")
    links = collect_links()
    print(f"Collected {len(links)} links.")

    all_data = []

    for link in links[:5]:
        print(f"Scraping: {link}")
        branch_data = extract_branch_data(link)
        all_data.append(branch_data)

    # Save to CSV
    df = pd.DataFrame(all_data)
    df.to_csv("zoocity_branches.csv", index=False, encoding="utf-8")

    print(f"Saved data for {len(all_data)} branches.")

if __name__ == "__main__":
    main()
