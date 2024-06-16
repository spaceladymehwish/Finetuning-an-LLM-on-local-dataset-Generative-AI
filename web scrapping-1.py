import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from GlobalFunctions import get_laws, get_rules
import urllib3
urllib3.disable_warnings()
logging.captureWarnings(True)


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors')
# try:
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
main_url = 'https://punjabcode.punjab.gov.pk/urdu'

pdf_save_dir = 'Files/Pdf/ur'
csv_save_dir = 'Files/Csv/ur'


driver.get(main_url)
# sub_urls = ["https://punjabcode.punjab.gov.pk/en/get_laws","https://punjabcode.punjab.gov.pk/en/get_rules"]

selector = 'a[href="https://punjabcode.punjab.gov.pk/urdu/get_rules"]'
alphabetical_tab = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
)
alphabetical_tab.click()
time.sleep(5)
page_source = driver.page_source
get_rules(page_source,pdf_save_dir,csv_save_dir)
driver.quit()

# main_url = 'https://punjabcode.punjab.gov.pk/en'

# en_pdf_save_dir = 'Files/Pdf/en'
# en_csv_save_dir = 'Files/Csv/en'

# driver.get(main_url)
# selector = 'a[href={"https://punjabcode.punjab.gov.pk/en/get_rules"}]'
# alphabetical_tab = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.CSS_SELECTOR, selector))
# )
# alphabetical_tab.click()
# time.sleep(5)
# page_source = driver.page_source
# get_laws(page_source,en_pdf_save_dir,en_csv_save_dir)

# driver.quit()