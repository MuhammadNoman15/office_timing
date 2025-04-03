import time
import random
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

# Function for human-like scrolling
def human_like_scroll(driver):
    scroll_pause = random.uniform(2, 4)
    for _ in range(random.randint(3, 6)):  # Scroll multiple times
        driver.execute_script(f"window.scrollBy(0, {random.randint(300, 800)});")
        time.sleep(scroll_pause)
    driver.execute_script("window.scrollTo(0, 0);")

# Function for human-like mouse movements
def human_mouse_movement(driver):
    action = ActionChains(driver)
    
    width = driver.execute_script("return window.innerWidth") or 1366  # Default to 1366 if None
    height = driver.execute_script("return window.innerHeight") or 768  # Default to 768 if None
    
    for _ in range(random.randint(5, 10)):
        x_offset = random.randint(50, width - 50)
        y_offset = random.randint(50, height - 50)
        
        try:
            action.move_by_offset(x_offset, y_offset).perform()
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            print(f"Mouse movement skipped due to error: {e}")
            break

def scrape_agents_from_page(driver, zip_code, csv_filename):
    agents_data = []
    
    try:
        grid_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.Grid-c11n-8-101-3__sc-18zzowe-0.iyaBVr"))
        )
    except Exception as e:
        print("Failed to find the agents list container:", e)
        return agents_data
    
    agent_divs = grid_container.find_elements(By.CSS_SELECTOR, "div.Grid-c11n-8-101-3__sc-18zzowe-0.iZzmpw")

    for agent_div in agent_divs:
        try:
            anchor_tag = agent_div.find_element(By.TAG_NAME, "a")
            agent_link = anchor_tag.get_attribute("href")
            
            if not agent_link.startswith("https://www.zillow.com"):
                agent_link = f"https://www.zillow.com{agent_link}"
            
            agent_info = {
                "ZIP Code": zip_code,
                "Profile Link": agent_link
            }
            agents_data.append(agent_info)

            df = pd.DataFrame([agent_info])
            df.to_csv(csv_filename, mode='a', header=not pd.io.common.file_exists(csv_filename), index=False)
            
            if random.random() > 0.7:
                driver.execute_script("window.scrollBy(0, 300);")
                time.sleep(random.uniform(2, 4))
        
        except Exception as e:
            print(f"Skipping an agent due to an error: {e}")
            continue
    
    return agents_data

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

try:
    zip_code = "75006"
    csv_filename = f"zillow_zipcode_{zip_code}.csv"
    base_url = f"https://www.zillow.com/professionals/real-estate-agent-reviews/{zip_code}"
    driver.get(base_url)
    time.sleep(random.uniform(5, 8))
    
    total_pages = 25
    
    for page in range(1, total_pages + 1):
        if page > 1:
            page_url = f"https://www.zillow.com/professionals/real-estate-agent-reviews/{zip_code}/?page={page}"
            print(f"Scraping page {page} of {total_pages} ({page_url})")
            driver.get(f"{page_url}")
            time.sleep(random.uniform(5, 10))
            human_mouse_movement(driver)
            time.sleep(random.uniform(2, 5))
            human_like_scroll(driver)
            time.sleep(random.uniform(2, 5))
        
        scrape_agents_from_page(driver, zip_code, csv_filename)
    
    print("Waiting for user action...")
    time.sleep(30)

except Exception as e:
    print("Error:", e)

finally:
    driver.quit()

print(f"Scraping completed! Data saved to {csv_filename}.")
