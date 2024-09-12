import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

url = "https://www.fatourati.ma/FatLite/ma/MTC/formulaire?cid=01&fid=1039"


def setup_driver(headless=False):
    options = Options()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--window-size=1920,1080')  # Set a specific window size
    # options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
    # options.add_argument('--disable-gpu')  # applicable to windows os only
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8',
        'Cache-Control': 'no-cache',
        'dnt': '1',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    for key, value in headers.items():
        options.add_argument(f"--{key}={value}")

    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except WebDriverException as e:
        logging.error(f"Failed to set up WebDriver: {e}")
        return None



def handle_captcha_and_submit(driver, payload):
    try:
        # Wait for the page to load
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Log the current URL
        logging.info(f"Current URL: {driver.current_url}")

        # Check if reCAPTCHA is present
        try:
            recaptcha_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".g-recaptcha"))
            )

            recaptcha_box.click()

            time.sleep(3)

            captcha_images = driver.find_elements(By.CSS_SELECTOR, ".rc-imageselect")

            if captcha_images:
                logging.info("reCaptcha modal found...")
                handle_captcha_and_submit(driver, payload)
                return None

            # wait for the box to be checked
            # time.sleep(5)

            # see if checked or not
            if recaptcha_box.get_attribute("aria-checked") == "true":
                logging.info("reCAPTCHA already solved")
                return None
            else:

                logging.info("reCAPTCHA clicked")


            logging.info("reCAPTCHA found on the page")
        except TimeoutException:
            logging.warning("reCAPTCHA not found on the page")

        # Fill in the form fields
        for key, value in payload.items():
            try:
                field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, key))
                )
                field.clear()
                field.send_keys(value)
                logging.info(f"Filled field: {key}")
            except TimeoutException:
                logging.warning(f"Could not find field: {key}")

        # Try to find and click the submit button
        try:
            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
            )
            submit_button.click()
            logging.info("Clicked submit button")
        except TimeoutException:
            logging.error("Could not find or click submit button")
            return None

        # Wait for the page to load after submission
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Get the response content
        return driver.page_source
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None


def parse_data(html_content):
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    result = {
        "client_details": {},
        "factures": []
    }

    # Extract client details
    identifiers = soup.find_all('span', class_='tagline')
    for identifier in identifiers:
        key, value = identifier.text.split(':', 1)
        result["client_details"][key.strip()] = value.strip()

    # Extract invoice details
    invoice_table = soup.find('table', id='hor-zebra')
    if invoice_table:
        rows = invoice_table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 6:
                facture = {
                    'numero': cols[1].text.strip(),
                    'mois_consommation': cols[2].text.strip(),
                    'echeance': cols[3].text.strip(),
                    'type': cols[4].text.strip(),
                    'montant_ttc': cols[5].text.strip()
                }
                result["factures"].append(facture)

    # Convert to JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))

def scrape_data(num_contrat):
    payload = {
        "num_contrat": str(num_contrat),
        "email": "a@a.com",
        "email1": "a@a.com",
    }
    driver = setup_driver()
    if not driver:
        logging.error("Failed to set up WebDriver")
        return None

    try:
        # add headers
        driver.get(url)
        response_content = handle_captcha_and_submit(driver, payload)
        if response_content:
            logging.info("Form submitted successfully with Selenium")
            return response_content
        else:
            logging.error("Failed to submit form with Selenium")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        driver.quit()

    return None




if __name__ == '__main__':
    result = scrape_data(2744688)
    if result:
        time.sleep(3)
        parse_data(result)
    else:
        logging.error("Failed to retrieve data")
