from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import csv
import sys
import logging
import time
import httplib
import socket
from selenium.webdriver.remote.command import Command

DOWNLOAD_PATH = os.getcwd()
DOWNLOAD_FILE = "savedrecs.txt"
RETRACTION_LIST_PATH = "top_articles.csv"
CITATION_LIST_PATH = "miscitationlist.csv"
WEB_SCIENCE_USERNAME = "xiaoran1@ualberta.ca"
WEB_SCIENCE_PASSWORD = "Wscq@1234"
MAX_SEARCH_NUMBER = 500
CONTINUE_WRITE = "ab"
WHERE_TO_START = 0
FIRST_BY_TITLE = 0
FAILED_FILE_NAME = "faillist.csv"
CREATE_FAIL_FILE = 0


def remove_extra_file():
    try:
        os.remove(DOWNLOAD_FILE)
        print "savedrecs removed"
    except Exception, e:
        print "savedrecs already removed"
        pass
    return


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
    noerror = True
    try:
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@id='s2id_saveToMenu']")))
        divarray = []
        divarray = browser.find_elements_by_xpath("//div[@id='s2id_saveToMenu']/a/span[@class='select2-arrow']/b")
        divarray[0].click()
        #webdriver.ActionChains(browser).move_to_element(divarray[0]).click(divarray[0]).perform()
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[text()='Save to Other File Formats']")))
        browser.find_element_by_xpath("//div[text()='Save to Other File Formats']").click()
        select = Select(browser.find_element_by_xpath("//select[@id='saveOptions']"))
        browser.find_element_by_xpath("//input[@id='markFrom']").send_keys(str(start))
        browser.find_element_by_xpath("//input[@id='markTo']").send_keys(str(end))
        select.select_by_visible_text('Tab-delimited (Win, UTF-8)')
        browser.find_element_by_xpath("//div[@class='quickoutput-overlay-buttonset']/span/input").click()
        errorm = []
        errorm = browser.find_elements_by_xpath("//div[@id='searchErrorMessage']")
        if len(errorm)>0:
            noerror = False
        else:
            try:
                WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='quickoutput-overlay-buttonset']")))
                browser.find_element_by_xpath("//div[@class='quickoutput-overlay-buttonset']/a").click()
            except Exception, e:
                pass
    except Exception, e:
        logging.exception(e)
        browser.quit()
    return browser, noerror


def loop_through_record_and_download(browser, record_count, row_index):
    start_from = 0
    end_by = 0
    try:
        while record_count > 0:
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
            browser,error_go_beyond = mark_and_download_data(browser, end_by, start_from)
            print error_go_beyond
            if error_go_beyond:
                if get_status(browser) == "Dead":
                    raise Exception, 'browser already quit'
                while not os.path.isfile(DOWNLOAD_FILE):
                    if get_status(browser) == "Dead":
                        raise Exception, 'browser already quit'
                    continue
                add_download_data_to_csv_file(CITATION_LIST_PATH, row_index,start_from)
            else:
                return browser
            # Reduce the upper case by 500 to see if there are still left records haven't been downloaded
            record_count -= 500
            if record_count < 0:
                record_count = 0
            else:
                browser.refresh()
    except Exception as e:
        logging.exception(e)
        browser.quit()
    return browser


def get_citation_data(browser, row_index,article_title):
    try:
        remove_extra_file()
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@id='s2id_saveToMenu']")))
        numeric_time = browser.find_element_by_xpath("//span[@id='hitCount.top']").get_attribute("innerHTML")
        record_count = int(numeric_time.replace(',', ''))
        print "actual cited times: ", record_count
        if record_count > 0:
            loop_through_record_and_download(browser,record_count,row_index)
            browser.find_element_by_xpath("//h1[@class='titleh1']/a").click()
        # else:
        #     print "{0!s} has not been cited yet !".format(article_title)
        #     write_failed_info(article_title,"times cited is 0",row_index)
        #     browser.find_element_by_xpath("//h1[@class='titleh1']/a").click()
        #     return browser
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


def take_out_title_from_articles_list():
    global FIRST_BY_TITLE
    test_time = 0
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
        with open(csv_file, "rb") as miscitation_list_file:
            list_reader = csv.reader(miscitation_list_file)
            for row in list_reader:
                if is_column_head:
                    is_column_head = False
                    continue
                else:
                    article_title = row[2]
                    if MAX_SEARCH_NUMBER != 0:
                        if test_time >= MAX_SEARCH_NUMBER:
                            break
                    where += 1
                    row_index += 1
                    if WHERE_TO_START > 0 and where < WHERE_TO_START:
                        continue
                    if WHERE_TO_START > 0 and where > WHERE_TO_START+198:
                        browser.quit()
                        FIRST_BY_TITLE = 0
                        browser = setup_webdriver("chrome")
                        browser = login_to_serach_page(browser)
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
        take_out_title_from_articles_list()
    finally:
        print "Quit the main program"
    sys.exit(0)

