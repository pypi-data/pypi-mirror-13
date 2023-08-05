#!/usr/bin/env python


# Core
from __future__ import print_function
from decimal import *

from functools import wraps
import logging
import math
import pprint
import random
import re
import time
import ConfigParser

# Third-Party
import argh

from clint.textui import progress
import funcy
import html2text
from splinter import Browser
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import \
    TimeoutException, UnexpectedAlertPresentException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.expected_conditions as EC
import selenium.webdriver.support.ui as ui

# Local

# Begin code

getcontext().prec = 2
getcontext().rounding = ROUND_DOWN


logging.basicConfig(
    format='%(lineno)s - %(message)s',
    level=logging.INFO
)

random.seed()

pp = pprint.PrettyPrinter(indent=4)

base_url = 'http://www.RevShareWorks.com/'

action_path = dict(
    login='account/login',
    dashboard='members',
    wallet='members/wallet',
    purchase_balance_transfer='pbalance_transfer.php',
    buy_pack='members/adshare/buy_shares'
)

one_minute = 60
three_minutes = 3 * one_minute
ten_minutes = 10 * one_minute
one_hour = 3600


def url_for_action(action):
    return "{0}{1}".format(base_url, action_path[action])


def loop_forever():
    while True:
        pass


def clear_input_box(box):
    box.type(Keys.CONTROL + "e")
    for i in xrange(100):
        box.type(Keys.BACKSPACE)
    return box


# http://stackoverflow.com/questions/16807258/selenium-click-at-certain-position
def click_element_with_offset(driver, elem, x, y):
    action = ActionChains(driver)
    echo_print("Moving to x position", x)
    echo_print("Moving to y position", y)
    action.move_to_element_with_offset(elem, x, y)
    print("OK now see where the mouse is...")
    action.click()
    action.perform()

def page_source(browser):
    document_root = browser.driver.page_source
    return document_root

def wait_visible(driver, locator, by=By.XPATH, timeout=30):
    """

    :param driver:
    :param locator:
    :param by:
    :param timeout:
    :return:
    """
    try:
        if ui.WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, locator))):
            logging.info("Found element.")
            return driver.find_element(by, locator)
    except TimeoutException:
        logging.info("TimeoutException in wait_visible.")
        return False


def maybe_accept_alert(driver):
    try:
        logging.warn("Probing for alert.")
        ui.WebDriverWait(driver, 3).until(EC.alert_is_present(),
                                          'Timed out waiting for PA creation ' +
                                          'confirmation popup to appear.')

        alert = driver.switch_to_alert()
        alert.accept()
        print("alert accepted")
    except TimeoutException:
        print("no alert")


def trap_unexpected_alert(func):
    @wraps(func)
    def wrapper(self):
        try:
            return func(self)
        except UnexpectedAlertPresentException:
            print("Caught unexpected alert.")
            return 254
        except WebDriverException:
            print("Caught webdriver exception.")
            return 254

    return wrapper


def trap_alert(func):
    @wraps(func)
    def wrapper(self):
        try:
            return func(self)
        except UnexpectedAlertPresentException:
            logging.info("Caught UnexpectedAlertPresentException.")
            alert = self.browser.driver.switch_to_alert()
            alert.accept()
            return 254
        except WebDriverException:
            print("Caught webdriver exception.")
            return 253

    return wrapper


def get_element_html(driver, elem):
    return driver.execute_script("return arguments[0].innerHTML;", elem)

def get_outer_html(driver, elem):
    return driver.execute_script("return arguments[0].outerHTML;", elem)


def echo_print(text, elem):
    print("{0}={1}.".format(text, elem))


import inspect
def retrieve_name(var):
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is var]



class Entry(object):
    def __init__(self, username, password, browser):
        self._username = username
        self._password = password
        self.browser = browser

    def login(self):
        print("Logging in...")

        self.browser_visit('login')

        self.browser.find_by_name('username').first.type(self._username)
        self.browser.find_by_name('password').first.type(
            "{0}\t\n".format(self._password))
        # self.browser.find_by_xpath("//input[@value='LOGIN']").first.click()

        logging.info("Waiting for login ad...")

        link_elem = wait_visible(self.browser.driver, "//input[@value='Skip ad >>']")
        if link_elem:
            logging.info("Skip ad found. Clicking.")
            link_elem.click()
        else:
            logging.info("Logging in again.")
            return self.login()

        logging.info("Login complete.")


    def browser_visit(self, action_label):
        try:
            u = url_for_action(action_label)
            logging.info("Visiting URL for {0}: {1}".format(action_label, u))
            self.browser.visit(u)
        except TimeoutException:
            logging.info("Page load timeout.")
            pass
        except UnexpectedAlertPresentException:
            logging.info("Caught UnexpectedAlertPresentException.")
            logging.warn("Attempting to dismiss alert")
            alert = self.browser.driver.switch_to_alert()
            alert.dismiss()
            return 254
        except WebDriverException:
            logging.info("Caught webdriver exception.")
            return 253

    def view_ads(self, surf_amount):
        logging.warn("Visiting viewads")

        for i in xrange(1, surf_amount + 1):
            while True:
                print("Viewing ad {0}".format(i))
                result = self.view_ad()
                if result == 0:
                    break

        self.browser_visit('dashboard')

    @trap_alert
    def view_ad(self):
        self.browser_visit('view_ads')
        ads = self.browser.find_by_xpath('//a[@class="bannerlink"]')
        # print(ads)
        ads[3].click()
        self.browser.driver.switch_to_window(self.browser.driver.window_handles[-1])
        elem = wait_visible(self.browser.driver, '//div[@class="counter-text"]')
        print("may close elem={0}".format(elem))
        self.browser.driver.close()
        self.browser.driver.switch_to_window(self.browser.driver.window_handles[0])

        return 0

    def wait_on_ad(self):
        time_to_wait_on_ad = random.randrange(40, 50)
        for _ in progress.bar(range(time_to_wait_on_ad)):
            time.sleep(1)

    def collect_stats(self):
        self.browser_visit('dashboard')

        ad_pack_elem = self.browser.find_by_xpath("//p[@class='number-pack']")
        ad_packs = int(ad_pack_elem.text)

        main_account_balance_elem = self.browser.find_by_xpath("//p[@style='font-size:41px;']")
        main_account_balance = Decimal(main_account_balance_elem.text[1:])
        account_balance_elem = self.browser.find_by_xpath("//div[@class='account-blance']")
        account_balance_html = get_outer_html(self.browser.driver, account_balance_elem._element)
        account_balance_text = html2text.HTML2Text().handle(account_balance_html)
        floating_point_regexp = re.compile('\d+\.\d+')
        main, purchase, repurchase = [Decimal(f) for f in floating_point_regexp.findall(account_balance_text)]
        self._balance = dict(
            main=main, purchase=purchase, repurchase=repurchase, ad_packs=ad_packs
        )
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self._balance)

    @staticmethod
    def packs_to_purchase(bread, pack_value):
        return int(math.floor(bread/pack_value))

    def click_elem_by_text(self, t):
        xpath = "//*[text()='{0}']".format(t)
        logging.info("Waiting for element with xpath {0}".format(xpath))
        link = wait_visible(self.browser.driver, xpath, by=By.XPATH)
        link.click()


    def get_balance(self):

        self.click_elem_by_text('Dashboard')
        self.click_elem_by_text('My Wallet')
        self.click_elem_by_text('Wallet Balance')

        loop_forever()

        account_balance_elem = wait_visible(self.browser.driver, "rightbar", by=By.ID)
        account_balance_html = get_outer_html(self.browser.driver, account_balance_elem)
        account_balance_text = html2text.HTML2Text().handle(account_balance_html)

        # dollar amount samples:
        # $4.28
        # $0
        # no known samples for something like 28 cents. Not sure if it is
        # $0.28 or $.28
        floating_point_regexp = re.compile('\$(\d+(\.\d+)?)')
        floats = [Decimal(f[0]) for f in floating_point_regexp.findall(account_balance_text)]
        cash, repurchase = floats[20:22]
        self._balance = dict(
            cash=cash, repurchase=repurchase
        )
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self._balance)

    def exhaustive_buy(self):

        self.click_elem_by_text('Buy Adshares')

        loop_forever()

        link_elem = wait_visible(self.browser.driver, "//a[@title='Buy Adshares']", timeout=15)
        link_elem.click()
        loop_forever()


        total_balance = self._balance['cash'] + self._balance['repurchase']

        packs_to_buy = int(total_balance / pack_value)

        logging.info("Buying {0} packs of value {1}".format(packs_to_buy, pack_value))

        pack_value_to_index = {
            1: 0,
            3: 1,
            5: 2,
            7: 3,
            10: 4,
            15: 5,
            20: 6,
            30: 7,
            40: 8,
            50: 9,
        }

        if packs_to_buy < 1:
            return

        buy_form = self.browser.find_by_xpath("//form[@method='post']")
        form = buy_form[pack_value_to_index[pack_value]]
        pack_input = "{0}\t\t ".format(packs_to_buy)
        form.find_by_id('position').type(pack_input)
        button = wait_visible(self.browser.driver, 'paynow', By.ID)
        if button:
            button.click()
#        self.browser.find_by_id('paynow').first.click()

    def calc_account_balance(self):
        time.sleep(1)

        logging.warn("visiting dashboard")
        self.browser_visit('dashboard')

        logging.warn("finding element by xpath")
        elem = self.browser.find_by_xpath(
            '/html/body/table[2]/tbody/tr/td[2]/table/tbody/tr/td[2]/table[6]/tbody/tr/td/table/tbody/tr[2]/td/h2[2]/font/font'
        )

        print("Elem Text: {}".format(elem.text))

        self.account_balance = Decimal(elem.text[1:])

        print("Available Account Balance: {}".format(self.account_balance))

    def calc_credit_packs(self):
        time.sleep(1)

        logging.warn("visiting dashboard")
        self.browser_visit('dashboard')

        logging.warn("finding element by xpath")
        elem = self.browser.find_by_xpath(
            "//font[@color='#009900']"
        )

        print("Active credit packs = {0}".format(elem[0].text))
        # for i, e in enumerate(elem):
        #     print("{0}, {1}".format(i, e.text))

    def solve_captcha(self):
        time.sleep(3)

        t = page_source(self.browser).encode('utf-8').strip()
        # print("Page source {0}".format(t))

        captcha = funcy.re_find(
            """ctx.strokeText\('(\d+)'""", t)

        # print("CAPTCHA = {0}".format(captcha))

        self.browser.find_by_name('codeSb').fill(captcha)

        time.sleep(6)
        button = self.browser.find_by_name('Submit')
        button.click()


