import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

def main():
    # Start WebDriver
    driver = webdriver.Chrome()
    driver.get("https://www.ntl.hr/prodajna-mjesta")
    driver.maximize_window()

    # Give yourself time to translate the page if needed
    input("Translate the page if needed, then press Enter to continue...")

    # Prepare CSV output
    # You can adjust or rename these columns as you wish
    fieldnames = ["storeNumber", "address", "monFri", "saturday", "sunday"]
    with open("ntl_stores.csv", "w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        # Each store is in a div.store-info > div
        store_divs = driver.find_elements(By.CSS_SELECTOR, "div.store-info > div")

        for idx, store_div in enumerate(store_divs, start=1):
            # Each store_div has multiple <p> tags
            p_tags = store_div.find_elements(By.TAG_NAME, "p")
            # Convert them to text lines (some might be empty)
            lines = [p.text.strip() for p in p_tags if p.text.strip()]

            # lines might look like:
            # [
            #   "STORE NO.384",
            #   "Ružina Street 63/71, OSIJEK",
            #   "Mon-Fri: 6:30-20:00",
            #   "Sat: 6:30-20:00",
            #   "Sun: 8:00-13:00"
            # ]
            # We’ll do our best to parse them:
            store_num = ""
            address   = ""
            mon_fri   = ""
            sat       = ""
            sun       = ""

            # The first line is often "STORE NO.X"
            if len(lines) >= 1:
                store_num = lines[0]

            # The second line is typically the address
            if len(lines) >= 2:
                address = lines[1]

            # The third line is typically "Mon-Fri: HH:MM-HH:MM"
            if len(lines) >= 3:
                mon_fri = lines[2].replace("Mon-Fri:", "").strip()

            # The fourth line is "Sat: HH:MM-HH:MM"
            if len(lines) >= 4:
                sat = lines[3].replace("Sat:", "").strip()

            # The fifth line is "Sun: HH:MM-HH:MM"
            if len(lines) >= 5:
                sun = lines[4].replace("Sun:", "").strip()

            # Print to console for debugging
            print(f"Store #{idx} → {store_num}, {address}, Mon-Fri: {mon_fri}, Sat: {sat}, Sun: {sun}")

            # Write to CSV
            row = {
                "storeNumber": store_num,
                "address": address,
                "monFri": mon_fri,
                "saturday": sat,
                "sunday": sun,
            }
            writer.writerow(row)

    driver.quit()

if __name__ == "__main__":
    main()
