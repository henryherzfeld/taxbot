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
        self.driver = WebDriver(local=local)
        self.verbosity = verbosity
        self.fips = fips
        self.pid = pid
        self.return_ = {}

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
        while not self.complete:
            # get current directive in directive queue
            if not len(self.directives):
                self.complete = True
                self.success = True
                self.abort()
            else:
                current = self.directives.popleft()
                self.process_step(current)

        if self.success:
            ret = self.return_
        else:
            ret = None

        return ret

    def abort(self):
        self.complete = True

        # if self.success:  # if successful operation save page source
        #     with open(path.join(source_dir, self.pid) + '.html', 'w') as f:
        #         f.write(self.driver.driver.page_source)
        # else:              # else save screenshot
        #     self.driver.driver.save_screenshot(path.join(screenshot_dir, self.pid) + '.png')

        self.driver.driver.close()
        del self.driver

    def resolve_alias(self, value):
        value = value.lstrip('$')
        if value == 'PID':
            value = self.pid

        return value

    def process_step(self, current):
        # decompose directive into key, value
        directive, directive_data_list = next(iter(current.items()))

        # log/output directives
        logger.debug(f"processing directive {directive}")
        if self.verbosity > 0:
            print(f"processing directive {directive}")

        # first test for attribute-free directives for webdriver
        if directive == 'back':
            self.driver.back()
        elif directive == 'wait':
            self.driver.wait(directive_data_list)
        elif type(directive_data_list) is str:
            if directive == 'visit':
                self.driver.visit(directive_data_list)

        elif not self.complete:
            for directive_data in directive_data_list:
                # confirm our directive requires a find on an element on the page using directive data key values
                find_elem_keys = ['id', 'name', 'selector', 'class']

                find_elem = False
                for key in find_elem_keys:
                    if key in directive_data:
                        find_elem = True
                        break

                if not find_elem:
                    logger.error(f'directive requiring a find on element missing {find_elem_keys} entries')
                else:
                    # build subset of directive_data
                    element_data = {key: value for key, value in directive_data.items() if key in find_elem_keys}

                    # find element on page
                    try:
                        elem = self.driver.find_element(**element_data)
                    except NoSuchElementException:
                        logger.error("Unable to find element")
                        self.abort()
                        break

                    if elem is None or (elem.text == "" and directive == "return"):
                        print(directive_data)
                        if 'alt_selector' in directive_data:
                            print('failed to find element, using alternative selector...')
                            try:
                                elem = self.driver.find_element(selector=directive_data['alt_selector'])
                            except NoSuchElementException:
                                logger.error("Unable to find element")
                                self.abort()
                                break

                        else:
                            print('failed to find element, aborting...')
                            self.abort()
                            break

                    value = None
                    if 'value' in directive_data:
                        value = directive_data['value']

                        if '$' in value:  # check for alias symbol, if present identify and replace
                            value = self.resolve_alias(value)

                    if directive == 'fill_in':
                        if value is not None:
                            self.driver.fill_in(elem, value)
                        else:
                            logger.error(f'fill_in directive missing "value" entry, skipping...')

                    elif directive == 'click_on':
                        try:
                            self.driver.click_on(elem)
                        except ElementNotInteractableException:
                            logger.error(f'Element not interactable...')
                            print('Element not interactable...')
                            self.abort()
                        except ElementClickInterceptedException:
                            logger.error(f'Element click intercepted...')
                            print('Element click intercepted...')
                            self.abort()

                    elif directive == 'return':
                        if value is not None:
                            if 'mod' in directive_data:
                                mod = directive_data['mod']
                                if mod == 'CLEAN_INT':
                                    temp = re.findall("\d+\.\d+", elem.text)
                                    if type(temp) == list and len(temp):
                                        ret = temp[0]
                                    else:
                                        ret = ""
                            else:
                                ret = elem.text
                            self.return_[value] = ret
