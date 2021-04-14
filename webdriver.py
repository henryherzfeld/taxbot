from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from time import sleep
import logging
logger = logging.getLogger(__name__)


class WebDriver:
    timeout = 3

    def __init__(self, local=False):
        self.local = local

    def __enter__(self):
        if self.local:
            self.driver = webdriver.Chrome(executable_path=r"C:\z_chromedriver\chromedriver.exe")
        else:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu-sandbox')
            options.add_argument('--single-process')
            options.binary_location = "/opt/bin/headless-chromium"
            self.driver = webdriver.Chrome(executable_path="/opt/bin/chromedriver", chrome_options=options)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()
        self.driver.quit()

    def wait(self, n):
        print(f"sleeping for {n} seconds")
        sleep(n)

    def visit(self, url):
        self.driver.get(url)

    def click_on(self, elem):
        elem.click()

    def fill_in(self, elem, text):
        elem.clear()
        elem.send_keys(text)

    def back(self):
        self.driver.back()

    def find_element(self, id_=None, selector=None, class_=None, name=None, xpath=None):
        if id_ is not None:
            strategy = By.ID
            element = id_
        elif selector is not None:
            strategy = By.CSS_SELECTOR
            element = selector
        elif class_ is not None:
            strategy = By.CLASS_NAME
            element = class_
        elif name is not None:
            strategy = By.NAME
            element = name
        elif xpath is not None:
            strategy = By.XPATH
            element = xpath
        else:
            return None

        try:
            ret = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((strategy, element)))
        except TimeoutException:
            logger.error(f"failed to find element {element} using {strategy} strategy")
            print(f"failed to find element {element} using {strategy} strategy")
            ret = None

        return ret
