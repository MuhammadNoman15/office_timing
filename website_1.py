import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def scrape_sportvision():
    # 1. Setup Selenium in NON-headless mode
    chrome_options = Options()
    # Do NOT add --headless if you want to see the browser and manually translate
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920x1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://www.sportvision.hr/trgovine")
        wait = WebDriverWait(driver, 20)

        # 2. Attempt to close the cookie overlay if it appears
        try:
            accept_cookies_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='uc-accept-all-button']"))
            )
            accept_cookies_btn.click()
            time.sleep(1)
        except:
            pass  # If no cookie banner, ignore

        # 3. Pause so you can manually translate the page to English
        print("\nPlease right-click on the opened browser and choose 'Translate to English'.")
        print("Once the page is translated, press ENTER in this console to start scraping.")
        input()  # Wait for user to press Enter

        # 4. Find all store <li> items in the left panel
        store_cards = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.stores-list li.store-item"))
        )

        all_data = []

        for card in store_cards:
            # --- A) Scrape basic info (store name, city, street, phone) from the left card ---
            try:
                store_name_el = card.find_element(By.CSS_SELECTOR, ".nb-store-name.title span.nb-insert-content")
                store_name_left = store_name_el.text.strip()
            except:
                store_name_left = ""

            try:
                city_el = card.find_element(By.CSS_SELECTOR, ".nb-store-cityName.cityName span.nb-insert-content")
                city_left = city_el.text.strip()
            except:
                city_left = ""

            try:
                street_el = card.find_element(By.CSS_SELECTOR, ".nb-store-street.address span.nb-insert-content")
                street_left = street_el.text.strip()
            except:
                street_left = ""

            try:
                phone_el = card.find_element(By.CSS_SELECTOR, ".nb-store-phone.phone span.nb-insert-content")
                phone_left = phone_el.text.strip()
            except:
                phone_left = ""

            # --- B) Click the card (this may show working hours in left panel OR a map pop-up) ---
            card.click()
            time.sleep(1)  # allow the UI to update

            # --- C) Try to scrape working hours from .nb-store-workingHours in the left panel ---
            #     (Scenario A: The snippet you gave with <div class="item item-wrapper nb-store-workingHours">)
            working_hours = ""
            try:
                hours_el = wait.until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, ".item.nb-store-workingHours .content.nb-insert-content")
                    )
                )
                working_hours = hours_el.text.strip()
            except:
                # If that fails, we attempt the map pop-up approach
                pass

            # --- D) If not found, try the .leaflet-popup-content approach (Scenario B) ---
            #     Some stores only show hours in the map pop-up
            if not working_hours:
                try:
                    popup_el = wait.until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, ".leaflet-popup-content"))
                    )
                    popup_text = popup_el.text.strip()
                    # Example lines for a store:
                    #   0: "Sport Vision LA Labin"
                    #   1: "Strmac 303"
                    #   2: "52200"
                    #   3: "LABIN"
                    #   4: "Every day from: 9am - 9pm"
                    lines = popup_text.split("\n")

                    # We assume the hours might be at lines[4+] (or 3+ if the store has fewer lines).
                    # If you only want the lines that mention "am/pm" or "Weekdays" / "Sundays", you can parse further.
                    # For simplicity, let's join everything after line[4].
                    if len(lines) > 4:
                        working_hours = "\n".join(lines[4:]).strip()
                    elif len(lines) > 3:
                        # Fallback: maybe line[3] is the hours
                        # (In case the city is missing or we only have 3 lines total)
                        possible_hours = lines[3]
                        # Check if it looks like hours. If so, store it:
                        if "am" in possible_hours or "pm" in possible_hours:
                            working_hours = possible_hours
                except:
                    pass

            # --- E) Build a dictionary combining all info ---
            store_info = {
                "Store Name": store_name_left,
                "City": city_left,
                "Street": street_left,
                "Phone": phone_left,
                "Working Hours": working_hours
            }

            all_data.append(store_info)

        # 5. Convert to DataFrame and print/save
        df = pd.DataFrame(all_data)
        print(df)

        df.to_csv("sportvision_stores.csv", index=False, encoding="utf-8")

        print("\nScraping complete. Check 'sportvision_stores.csv'. Close the browser or press Ctrl+C to exit.")

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_sportvision()
