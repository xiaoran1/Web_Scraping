# Script Name   : web_scrapping.py
# Author        : Xiaoran Huang
# Created       : 10th June 2016
# Last Modified	: 19th June 2016
#
# Description   : This script will get all data of retraction articles from Web Of Science, then for each
#                 article, find and download all article information that cited from this artcle

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import os
import csv
import sys
import logging
import re
import httplib
import socket
from selenium.webdriver.remote.command import Command

CONFIGRATION_FILE_NAME = "Configration.config"
DOWNLOAD_PATH = os.getcwd()
DOWNLOAD_FILE = "savedrecs.txt"
RETRACTION_LIST_PATH = ""
CITATION_LIST_PATH = ""
WEB_SCIENCE_USERNAME = ""
WEB_SCIENCE_PASSWORD = ""
CITATION_LIST_ONLY = 0
RETRACTION_LIST_ONLY = 0
MAX_CITATION_NUMBER = 0
MAX_RETRACTION_NUMBER = 0
TITLE_WITH_DATE = 0
CONTINUE_WRITE = "ab"
WHERE_TO_START = 0
FIRST_BY_TITLE = 0
FAILED_FILE_NAME = ""
CREATE_FAIL_FILE = 0

def read_from_config():
    global WEB_SCIENCE_PASSWORD
    global RETRACTION_LIST_PATH
    global CITATION_LIST_PATH
    global WEB_SCIENCE_USERNAME
    global RETRACTION_LIST_ONLY
    global CITATION_LIST_ONLY
    global MAX_CITATION_NUMBER
    global MAX_RETRACTION_NUMBER
    global CONTINUE_WRITE
    global TITLE_WITH_DATE
    global  WHERE_TO_START
    global  FAILED_FILE_NAME
    global  CREATE_FAIL_FILE
    with open(CONFIGRATION_FILE_NAME, "r+") as my_config:
        for line in my_config:
            line = line.replace('=', ' ').replace('/n', ' ').split()
            if line[0] == "WEB_SCIENCE_USERNAME":
                WEB_SCIENCE_USERNAME = line[1]
            if line[0] == "WEB_SCIENCE_PASSWORD":
                WEB_SCIENCE_PASSWORD = line[1]
            if line[0] == "RETRACTION_LIST_NAME":
                RETRACTION_LIST_PATH = line[1]
            if line[0] == "FAILED_FILE_NAME":
                FAILED_FILE_NAME = line[1]
            if line[0] == "CITATION_LIST_NAME":
                CITATION_LIST_PATH = line[1]
            if line[0] == "CITATION_LIST_ONLY":
                CITATION_LIST_ONLY = int(line[1].replace(',', ''))
            if line[0] == "RETRACTION_LIST_ONLY":
                RETRACTION_LIST_ONLY = int(line[1].replace(',', ''))
            if line[0] == "MAX_CITATION_NUMBER":
                MAX_CITATION_NUMBER = int(line[1].replace(',', ''))
            if line[0] == "MAX_RETRACTION_NUMBER":
                MAX_RETRACTION_NUMBER = int(line[1].replace(',', ''))
            if line[0] == "TITLE_WITH_DATE":
                TITLE_WITH_DATE = int(line[1].replace(',', ''))
            if line[0] == "CONTINUE_WRITE":
                CONTINUE_WRITE = int(line[1].replace(',', ''))
                CONTINUE_WRITE = ("ab" if CONTINUE_WRITE == 1 else "wb")
            if line[0] == "WHERE_TO_START":
                WHERE_TO_START = int(line[1].replace(',', ''))
            if line[0] == "CREATE_FAIL_FILE":
                CREATE_FAIL_FILE = int(line[1].replace(',', ''))


def remove_extra_file():
    try:
        os.remove(DOWNLOAD_FILE)
        print "savedrecs removed"
    except Exception, e:
        print "savedrecs already removed"
        pass
    return

def get_correct_title(article_title):
    new_article_title = article_title
    if article_title[len(article_title)-1] == ")":
        pos = re.search(r"\(*\)$", article_title).start() - 1
        bracket_count = 0
        while bracket_count >= 0:
            if article_title[pos] == ")":
                bracket_count += 1
            if article_title[pos] == "(":
                bracket_count -= 1
            if bracket_count == -1:
                break
            pos -= 1
        new_article_title = article_title[:pos]
    return new_article_title


def setup_webdriver(browser_type):
    try:
        if browser_type == "chrome":
            chrome_driver = os.path.abspath("chromedriver.exe")
            os.environ["webdriver.chrome.driver"] = chrome_driver
            options = webdriver.ChromeOptions()
            default_download_path = {"download.default_directory": DOWNLOAD_PATH}
            options.add_experimental_option("prefs", default_download_path)
            options.add_argument('--lang=es')
            my_driver = webdriver.Chrome(executable_path=chrome_driver, chrome_options=options)
        else:
            my_driver = webdriver.Firefox()
        return my_driver
    except Exception, e:
        logging.exception(e)
        pass
    return


def login_to_serach_page(browser):
    try:
        browser.get("https://login.webofknowledge.com")
        browser.find_element_by_css_selector("input[name=username]").send_keys(WEB_SCIENCE_USERNAME)
        browser.find_element_by_css_selector("input[name=password]").send_keys(WEB_SCIENCE_PASSWORD)
        browser.find_element_by_css_selector("input[title='Sign In']").click()
        WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.XPATH, "//td[@class='NEWwokErrorContainer SignInLeftColumn']/h2")))
        # if another session already exist then close that first
        href_text = browser.find_element_by_xpath("//td[@class='NEWwokErrorContainer SignInLeftColumn']/h2").text
        if (href_text == 'A SESSION ALREADY EXISTS WITH THESE LOGIN CREDENTIALS.'):
            browser.find_element_by_link_text("continue and establish a new session").click()
    except Exception, e:
        logging.exception(e)
        browser.quit()
    return browser


def search_by_title(browser, title_name):
    global FIRST_BY_TITLE
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='search-criteria-input-wr']/input[@type='text']")))
        search_input = browser.find_element_by_xpath("//div[@class='search-criteria-input-wr']/input[@type='text']")
        search_input.clear()
        search_input.send_keys(title_name)
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='s2id_select1']/a[@class='select2-choice']/span[@class='select2-arrow']/b")))
        if FIRST_BY_TITLE == 0:
            browser.find_element_by_xpath(
				"//div[@id='s2id_select1']/a[@class='select2-choice']/span[@class='select2-arrow']/b").click()
            browser.find_element_by_xpath(
				"//li[@class='select2-results-dept-0 select2-result select2-result-selectable']/div[text()='Title']").click()
            FIRST_BY_TITLE = 1
        #time.sleep(3)
        browser.find_element_by_xpath(
            "//span[@class='searchButton']/input[@id='UA_GeneralSearch_input_form_sb']").click()
    except Exception, e:
        logging.exception(e)
    return browser


def mark_and_download_data(browser, end, start):
    try:
        # add retraction list to the marked list (5000 per time)
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[@class='addToMarkedListButton'][@style='visibility: visible;']")))
        browser.find_element_by_xpath("//span[@class='addToMarkedListButton'][@style='visibility: visible;']/a").click()
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='numberOfRecordsRange']")))
        browser.find_element_by_xpath("//input[@id='numberOfRecordsRange']").click()
        browser.find_element_by_xpath("//input[@id='markFrom']").send_keys(str(start))
        browser.find_element_by_xpath("//input[@id='markTo']").send_keys(str(end))

        browser.find_element_by_xpath("//span[@class='quickoutput-action']/input[@title='Add'][@name='add']").click()
        # get into the marked list page
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//li[@class='nav-item']/a[@class='nav-link'][@title='Marked List']")))
        browser.find_element_by_xpath("//li[@class='nav-item']/a[@class='nav-link'][@title='Marked List']").click()
        try:
            current_close_buttons = []
            current_close_buttons = browser.find_elements_by_xpath(
                "//div[@class='ui-dialog ui-widget ui-widget-content ui-corner-all ui-front ui-dialog-csi ui-draggable']/"
                "div[@class='ui-dialog-titlebar ui-widget-header ui-corner-all ui-helper-clearfix']/button")
            current_close_buttons[3].click()
        except Exception, e:
            pass
        # save articles' information to local desktop
        current_spans = []
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[@class='select2-arrow']/b")))
        current_spans = browser.find_elements_by_xpath("//span[@class='select2-arrow']/b")
        current_spans[0].click()
        # browser.find_element_by_xpath("//div[@id='select2-result-label-8']").click()
        browser.find_element_by_xpath("//div[text()='Save to Other File Formats']").click()
        select = Select(browser.find_element_by_xpath("//select[@id='saveOptions']"))
        select.select_by_visible_text('Tab-delimited (Win, UTF-8)')
        browser.find_element_by_xpath("//div[@class='quickoutput-overlay-buttonset']/span/input").click()
    except Exception, e:
        logging.exception(e)
        browser.quit()
    return browser


def loop_through_record_and_download(browser, citation_or_retraction, celling, row_index):
    start_from = 0
    end_by = 0
    if CITATION_LIST_ONLY == 0 and RETRACTION_LIST_ONLY == 1:
        start_from = WHERE_TO_START
        end_by = WHERE_TO_START
    upper_bound = 0
    try:
        total_citing_number = browser.find_element_by_xpath("//span[@id='hitCount.top']").get_attribute("innerHTML")
        record_count = int(total_citing_number.replace(',', ''))
        print "actual cited times: ", record_count
        if celling > 0:
            if celling < record_count:
                upper_bound = record_count - celling
        while record_count > upper_bound:
            if record_count > 500:
                if start_from == 0:
                    # "which means this is the 1st time, so from 1-500"
                    start_from = 1
                if start_from > 0 or end_by > 0:
                    # "which means this is the 2nd time, so from (last_end+1)-last"
                    start_from = end_by + 1
                end_by += 500
            else:
                if start_from == 0:
                    # "which means this is the 1st time, so from 1-last"
                    start_from = 1
                if start_from > 0:
                    # "which means this is the 2nd time, so from (last_end+1)-last"
                    start_from = end_by + 1
                end_by += record_count
            print "search from ", start_from, " to ", end_by

            browser = mark_and_download_data(browser, end_by, start_from)
            if get_status(browser) == "Dead":
                raise Exception, 'browser already quit'
            while not os.path.isfile(DOWNLOAD_FILE):
                if get_status(browser) == "Dead":
                    raise Exception, 'browser already quit'
                continue
            if citation_or_retraction == 0:
                add_download_data_to_csv_file(RETRACTION_LIST_PATH, 0,start_from)
            else:
                add_download_data_to_csv_file(CITATION_LIST_PATH, row_index,start_from)
            # Reduce the upper case by 500 to see if there are still left records haven't been downloaded
            record_count -= 500
            # clear list and add another 500 records or start search another title
            try:
                WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='quickoutput-overlay-buttonset']")))
                browser.find_element_by_xpath("//div[@class='quickoutput-overlay-buttonset']/a").click()
                browser.find_element_by_xpath("//div[@class='ml-management']/input[@class='clear']").click()
                try:
                    alert = browser.switch_to_alert()
                    alert.accept()
                except:
                    pass
            except Exception, e:
                print "clear marked list fail: ", e
                browser.quit()
                return
            try:
                WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//li[@class='nonSearchPageLink']")))
                if record_count < 0:
                    browser.find_element_by_xpath("//h1[@class='titleh1']/a").click()
                else:
                    # browser.find_element_by_xpath(
                    #     "//li[@class='nonSearchPageLink']/a[@title='Return to Search Results']").click()
                    browser.execute_script("window.history.go(-1)")
                    browser.execute_script("window.history.go(-1)")
            except Exception, e:
                print "return to search result fail: ", e
                pass
            if record_count < 0:
                record_count = 0
    except Exception as e:
        logging.exception(e)
        browser.quit()
    return browser


def get_retraction_list():
    upper_bound = 0
    if CONTINUE_WRITE == 0:
        try:
            os.remove(RETRACTION_LIST_PATH)
        except Exception:
            print "retraction list file already been removed"
    browser = setup_webdriver("chrome")
    try:
        remove_extra_file()
        browser = login_to_serach_page(browser)
        if get_status(browser) == "Dead":
            raise Exception, 'browser already quit'
        # start searching for retracted articles
        browser = search_by_title(browser,"retraction of")
        if get_status(browser) == "Dead":
            raise Exception, 'browser already quit'
        # Refine result by document type
        browser.find_element_by_xpath("//h4[@class='refine-title']/i[@title='Show the Document Types']").click()
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//a[@id='DocumentType']")))
        browser.find_element_by_xpath("//div[@class='refine-content']/div/a[@id='DocumentType']").click()
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@value='DocumentType_RETRACTION']")))
        browser.find_element_by_xpath("//input[@value='DocumentType_RETRACTION']").click()
        browser.find_element_by_xpath("//input[@value='DocumentType_CORRECTION']").click()
        browser.find_element_by_xpath("//div[@class='more_title']/input[@title='Refine']").click()
        # do sorting by time
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@id='s2id_selectSortBy_.top']/a/span[@class='select2-arrow']")))
        browser.find_element_by_xpath("//div[@id='s2id_selectSortBy_.top']/a/span[@class='select2-arrow']/b").click()
        browser.find_element_by_xpath("//div[text()=' Times Cited -- highest to lowest ']").click()
        # Put records into marked_list and download them in the marked_list page
        if RETRACTION_LIST_ONLY == 1:
            upper_bound = MAX_RETRACTION_NUMBER
        browser = loop_through_record_and_download(browser,0,upper_bound,0)
        time.sleep(2)
    except Exception, e:
        browser.quit()
        logging.exception(e)
        pass
    finally:
        browser.quit()
    return


def get_citation_data(browser, row_index,article_title):
    try:
        remove_extra_file()
        if TITLE_WITH_DATE == 0 and FIRST_BY_TITLE == 0:
            # do sorting by publish date
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH,
                                                                             "//div[@id='s2id_selectSortBy_.top']/a/span[@class='select2-arrow']/b")))
            browser.find_element_by_xpath(
                "//div[@id='s2id_selectSortBy_.top']/a/span[@class='select2-arrow']/b").click()
            browser.find_element_by_xpath("//div[text()=' Publication Date -- oldest to newest ']").click()
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@id='RECORD_1']")))
        try:
            times_cited = browser.find_element_by_xpath("//span[@id='records_chunks']/div[@class='search-results']/"
                                                        "div[@id='RECORD_1']/div[@class='search-results-data']/"
                                                        "div[@class='search-results-data-cite']/a")
            inner_time = times_cited.get_attribute("innerHTML")
            numeric_time = int(inner_time.replace(',', ''))
            print "cited times:", numeric_time
            if numeric_time > 0:
                times_cited.click()
                # Start adding record into Marked list and download the data to local file
                browser = loop_through_record_and_download(browser, 1, 0, row_index)
        except:
            print "{0!s} has not been cited yet !".format(article_title)
            write_failed_info(article_title,"times cited is 0",row_index)
            browser.find_element_by_xpath("//h1[@class='titleh1']/a").click()
            return browser
    except Exception, e:
        logging.exception(e)
        browser.quit()
    return browser


def add_download_data_to_csv_file(dest_path, row_index,start_from):
    txt_file = DOWNLOAD_FILE
    is_head_list = 1
    if os.path.isfile(dest_path):
        is_head_list = 0
    print "is_head_list:", is_head_list
    is_head = 1
    csv_file = dest_path
    open_success = 0
    if os.path.isfile(txt_file):
        while open_success == 0:
            try:
                with open(txt_file, "r+") as in_txt:
                    read_in = csv.reader(in_txt, delimiter='\t')
                    print "{0!s} open success!".format(txt_file)
                    with open(csv_file, CONTINUE_WRITE) as out_csv:
                        write_to = csv.writer(out_csv)
                        print "{0!s} open success!".format(dest_path)
                        rowcount = start_from
                        if is_head_list == 1:
                            # if this is the first time accessing the target file
                            for line in read_in:
                                if is_head == 1:
                                    is_head = 0
                                    if row_index > 0:
                                        line.append("index")
                                    write_to.writerow(line)
                                else:
                                    if row_index > 0:
                                        line.append("{} no {}".format(row_index, rowcount))
                                    write_to.writerow(line)
                                    rowcount += 1
                        else:
                            # if this is not the first time accessing the target file
                            for line in read_in:
                                if is_head == 1:
                                    is_head = 0
                                else:
                                    if row_index > 0:
                                        line.append("{} no {}".format(row_index, rowcount))
                                    write_to.writerow(line)
                                    rowcount += 1
                        open_success = 1
            except Exception, e:
                pass
    remove_extra_file()
    print "=====================Done import============================"
    return


def take_out_title_from_retraction_list():
    global FIRST_BY_TITLE
    test_time = 0
    print WHERE_TO_START
    where = 0
    remove_extra_file()
    row_index = 0
    if CONTINUE_WRITE == 0:
        try:
            os.remove(CITATION_LIST_PATH)
        except Exception:
            print "Citation list file already been removed"
    browser = setup_webdriver("chrome")
    try:
        browser = login_to_serach_page(browser)
        is_column_head = True
        csv_file = RETRACTION_LIST_PATH
        with open(csv_file, "rb") as retraction_list_file:
            list_reader = csv.reader(retraction_list_file)
            for row in list_reader:
                if is_column_head:
                    is_column_head = False
                    continue
                else:
                    article_title = row[9]
                    if MAX_CITATION_NUMBER != 0 and CITATION_LIST_ONLY == 1:
                        if test_time >= MAX_CITATION_NUMBER:
                            break
                    where += 1
                    row_index += 1
                    if CITATION_LIST_ONLY == 1 and RETRACTION_LIST_ONLY == 0:
                        if WHERE_TO_START > 0 and where < WHERE_TO_START:
                            continue
                        if WHERE_TO_START > 0 and where > WHERE_TO_START+198:
                            browser.quit()
                            FIRST_BY_TITLE = 0
                            browser = setup_webdriver("chrome")
                            browser = login_to_serach_page(browser)
                    if TITLE_WITH_DATE == 0:
                        article_title = article_title.strip()
                        article_title = get_correct_title(article_title)
                    new_article_title = unicode(article_title, errors='ignore')
                    print ("{} Article title for search is: {}".format(row_index, new_article_title))
                    # Start to obtain citations with each title
                    browser = search_by_title(browser, new_article_title)
                    test_time += 1
                    if get_status(browser) == "Dead":
                        raise Exception, 'browser already quit'
                    try:
                        not_found = browser.find_element_by_xpath(
                            "//div[@class='errorMessage'][@id='noRecordsDiv']")
                        write_failed_info(article_title,"no record found error",row_index)
                        continue
                    except:
                        pass
                    try:
                        not_found = browser.find_element_by_xpath(
                            "//div[@class='errorMessage'][@id='searchErrorMessage']")
                        write_failed_info(article_title,"search name error",row_index)
                        continue
                    except:
                        pass
                    browser = get_citation_data(browser, row_index,article_title)
                    if get_status(browser) == "Dead":
                        raise Exception, 'browser already quit'

    except Exception, e:
        print "take_out_title_from_retraction_list error", e
        browser.quit()
    finally:
        print "done taking out titles from retraction list for gathering citations"
        browser.quit()
    return

def get_status(browser):
    try:
        browser.execute(Command.STATUS)
        return "Alive"
    except (socket.error, httplib.CannotSendRequest):
        return "Dead"

def write_failed_info(article_title, fail_indormation,row_index):
    if CREATE_FAIL_FILE == 1:
        if CONTINUE_WRITE == 0:
            try:
                os.remove(FAILED_FILE_NAME)
            except:
                print "fail infomation file already removed"
        row = [article_title,fail_indormation,row_index]
        with open(FAILED_FILE_NAME,CONTINUE_WRITE) as in_csv:
            print "{0!s} open success!".format(FAILED_FILE_NAME)
            writer = csv.writer(in_csv)
            writer.writerow(row)

if __name__ == '__main__':
    try:
        read_from_config()
        if (WEB_SCIENCE_PASSWORD == "" or WEB_SCIENCE_USERNAME == ""
            or RETRACTION_LIST_PATH == "" or CITATION_LIST_PATH == "" or FAILED_FILE_NAME==""):
            raise Exception('something wrong with config file')
        if CITATION_LIST_ONLY == 1 and RETRACTION_LIST_ONLY == 0:
            print "CITATION_LIST_ONLY"
            print "MAX_CITATION_NUMBER {0!s}".format((MAX_CITATION_NUMBER))
            take_out_title_from_retraction_list()
        elif RETRACTION_LIST_ONLY == 1 and CITATION_LIST_ONLY == 0:
            print "RETRACTION_LIST_ONLY"
            get_retraction_list()
        elif RETRACTION_LIST_ONLY == 1 and CITATION_LIST_ONLY == 1:
            # raise Exception("You can't have retraction only mode and citation only mode at the same time, please modify your config file")
            get_retraction_list()
            take_out_title_from_retraction_list()
        else:
            MAX_CITATION_NUMBER = 0
            MAX_RETRACTION_NUMBER = 0
            get_retraction_list()
            take_out_title_from_retraction_list()
    finally:
        print "Quit the main program"
    sys.exit(0)

