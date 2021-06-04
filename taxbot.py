import yaml
from webdriver import WebDriver
from collections import deque
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException,\
                                       ElementClickInterceptedException
from os import path
import re
import logging
logger = logging.getLogger(__name__)

screenshot_dir = 'screenshots'
source_dir = 'sources'
yaml_dir = 'yamls'


class TaxBot:
    def __init__(self, pid, fips, local=False, verbosity=0):
        self.verbosity = verbosity
        self.fips = fips
        self.pid = pid
        self.return_ = {}
        self.local = local

        # load yaml data
        with open(path.join(yaml_dir, '.'.join([self.fips, 'yaml']))) as f:
            data = yaml.load(f.read())

        if 'form' in data:
            if 'steps' in data['form']:
                directives = deque(data['form']['steps'])

        self.directives = directives
        self.success = False
        self.complete = False

    def process_form(self):
        print(f"processing pid {self.pid} with fips {self.fips}...")

        with WebDriver(local=self.local) as driver:
            while not self.complete:
                # get current directive in directive queue
                if not len(self.directives):
                    self.complete = True
                    self.success = True
                    break
                else:
                    current = self.directives.popleft()
                    self.process_step(current, driver)

        if self.success:
            return self.return_
        else:
            return None

    def abort(self):
        self.complete = True
        self.success = False

        # if self.success:  # if successful operation save page source
        #     with open(path.join(source_dir, self.pid) + '.html', 'w') as f:
        #         f.write(self.driver.driver.page_source)
        # else:              # else save screenshot
        #     self.driver.driver.save_screenshot(path.join(screenshot_dir, self.pid) + '.png')

    def resolve_alias(self, value):
        value = value.lstrip('$')
        if value == 'PID':
            value = self.pid

        return value

# uses selectors in directive data to perform finds on elements, falls back on alternative selectors if available
    def process_find(self, driver, directive, directive_data, find_elem_keys):
        # build subset of directive_data
        element_data = {key: value for key, value in directive_data.items() if key in find_elem_keys}

        # find element on page
        elem = None
        try:
            elem = driver.find_element(**element_data)
        except NoSuchElementException as e:
            logger.error(f"failed to find element, {e}")

        # employ alternative selectors if no
        if elem is None or (elem.text == "" and directive == 'return'):
            if 'alt_selector' in directive_data:
                print('failed to find element, trying alternative selectors...')

                # alt_selectors could be a str, or dict of str
                if type(directive_data['alt_selector']) is str:
                    alt_selectors = [directive_data['alt_selector']]
                else:
                    alt_selectors = directive_data['alt_selector'].values()

                for i, alt_selector in enumerate(alt_selectors):
                    try:
                        elem = driver.find_element(selector=alt_selector)
                    except NoSuchElementException as e:
                        logger.error(f"{e} failed to find element using alt_selector {i+1}: {alt_selector}")
                        print(f"{e} failed to find element using alt_selector {i+1}: {alt_selector}")

                    if elem is None or (elem.text == "" and directive == 'return'):
                        print(f"failed to find element using alt_selector {i+1}: {alt_selector}")

            else:
                print('failed to find element, no alternative selectors...')
                return None

        return elem

    def process_step(self, current, driver):
        # decompose directive into key, value
        directive, directive_data = next(iter(current.items()))

        if type(directive_data) is not list:
            directive_data_list = [directive_data]
        else:
            directive_data_list = directive_data

        # log/output directives
        logger.debug(f"processing directive {directive}")
        if self.verbosity > 0:
            print(f"processing directive {directive}")

        if not self.complete:
            find_elem_keys = ['id', 'name', 'selector', 'class', 'xpath']
            for directive_data in directive_data_list:

                # first test for attribute-free directives for webdriver
                if directive == 'back':
                    driver.back()
                elif directive == 'wait':
                    driver.wait(directive_data)
                elif directive == 'visit':
                    driver.visit(directive_data)
                elif directive == 'exit_iframe':
                    driver.exit_iframe()
                else:
                    # confirm our directive requires a find on an element on the page using directive data key values
                    find_elem = False
                    for key in find_elem_keys:
                        if key in directive_data:
                            find_elem = True
                            break

                    if not find_elem:
                        logger.error(f"directive requiring a find on element missing {find_elem_keys} entries")
                    else:
                        # perform find for element using selectors and alt_selectors if available
                        elem = self.process_find(driver, directive, directive_data, find_elem_keys)

                        find_and_fail = True
                        if 'mod' in directive_data:
                            mod = directive_data['mod']

                            if mod == "TRY":
                                find_and_fail = False

                        if elem is None:
                            if find_and_fail:
                                print('failed to find element, aborting...')
                                self.abort()
                                break
                            else:
                                print('failed to find element, TRY modification for current step, continuing...')
                                break

                        value = None
                        if 'value' in directive_data:
                            value = directive_data['value']

                            if '$' in value:  # check for alias symbol, if present identify and replace
                                value = self.resolve_alias(value)

                        if directive == 'fill_in':
                            if value is not None:
                                driver.fill_in(elem, value)
                            else:
                                logger.error(f"fill_in directive missing 'value' entry, skipping...")

                        elif directive == 'click_on':
                            try:
                                driver.click_on(elem)
                            except ElementNotInteractableException as e:
                                logger.error(f"{e} Element not interactable...")
                                print(f"{e} Element not interactable...")
                                self.abort()
                                break
                            except ElementClickInterceptedException as e:
                                logger.error(f"{e} Element click intercepted...")
                                print(f"Element click intercepted...")
                                self.abort()
                                break

                        elif directive == 'select':
                            driver.select(elem)

                        elif directive == 'return':
                            if value is not None:
                                ret = elem.text
                                if 'mod' in directive_data:
                                    mod = directive_data['mod']
                                    if mod == 'CLEAN_INT':
                                        ret = re.sub(r"[^0-9.]", "", elem.text)
                                    elif mod == 'CLEAN_NEWLINE':
                                        ret = re.sub(r'[\n]+', ' ', elem.text)
                                self.return_[value] = ret

                        elif directive == 'enter_iframe':
                            driver.enter_iframe(elem)
