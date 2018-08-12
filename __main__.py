import pandas as panda
from tabulate import tabulate
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from configparser import ConfigParser


def load_config():  # Load config file - should be called config.ini
    print('[STATUS] Loading config file...')
    config = ConfigParser()
    config.read('config.ini')
    username = config.get('MAIN', 'USERNAME')
    password = config.get('MAIN', 'PASSWORD')
    print('[STATUS] Loaded!')
    return username, password


def initiate_browser():  # Initiates the firefox headless browser (geckodriver needs to be installed)
    try:
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(firefox_options=options)  # Starts firefox with options defined above
        print("[STATUS] Firefox Headless Browser Initiated")
        driver.get("https://portal.uea.ac.uk/library")
        print('[STATUS] Page Loaded')
        return driver
    except Exception as e:
        print('[ERROR] ', e)


def login(username, password, browser, delay):  # Logs in to the libary and redirects to the renew page
    try:
        sign_in_button = browser.find_element_by_xpath('//a[@href="/c/portal/uealogin?p_l_id=6273463"]')
        sign_in_button.click()
        email_elem = browser.find_element_by_id('userNameInput')
        email_elem.send_keys(username)
        password_elem = browser.find_element_by_id('passwordInput')
        password_elem.send_keys(password)
        password_elem.submit()
        print("[STATUS] Signed in")
    except Exception as e:
        print("[ERROR] Login failed", e)
    try:
        browser.implicitly_wait(delay)
        details_link = browser.find_element_by_link_text('View details')
        details_link.click()
        select_all = browser.find_element_by_xpath("//input[@name='_libraryaccount_WAR_LibraryAccountportlet_selectAll']")
        select_all.click()
        renew_button = browser.find_element_by_css_selector('input#renewMultipleLoanItems')
        renew_button.click()
        print("[STATUS] Attempting book renew")
    except Exception as e:
        print("[ERROR] Failed to attempt renew", e)
    try:
        html = browser.page_source
        soup = BeautifulSoup(html, 'lxml')
        return soup
    except Exception as e:
        print("[ERROR] BS4 can not load the page", e)


def scrape_page(soup):  # Scrapes the resulting webpage for the success table, imports it into pandas dataframe and taabulate outputs it nicely
    try:
        succ_msg_unfromatted = soup.find("div", {"class": "alert alert-success"})
        succ_msg_whitespace = succ_msg_unfromatted.get_text()
        succ_msg = re.sub(r'\s+', ' ', succ_msg_whitespace).strip()
        print("[STATUS]" + succ_msg)
    except Exception as e:
        print("[ERROR] Error while web scraping", e)
    try:
        table = soup.find("table", {"class": "table table-bordered table-hover table-striped"})
        df = panda.read_html(str(table))
        df1 = panda.DataFrame(df[0])
        df1.drop(df1.columns[[0, 5]], axis=1, inplace=True)
        df1.columns = ['Title', 'Author', 'Due Date', 'Fines so far', 'Renews used']
        print(tabulate(df1, headers='keys', tablefmt='psql'))
    except Exception as e:
        print("[ERROR] Table failed to be read", e)


def main():
    username, password = load_config()
    delay = 15  # Time to wait for web page to load to find "View Details"
    scrape_page(login(username, password, initiate_browser(), delay))


if __name__ == "__main__":
    main()
