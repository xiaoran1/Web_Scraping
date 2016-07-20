# This script include the model of the configuration file information and some
# basic functions (include login and write failed information) that shared by multiple scripts

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

CONFIGRATION_FILE_NAME = "config"
DOWNLOAD_PATH = os.getcwd()
DOWNLOAD_FILE = "savedrecs.txt"

class ConfigData:
    retracted_articles_path = ""
    retraction_notices_path = ""
    retraction_notice_citations_path = ""
    retracted_article_citations_path = ""
    miscitation_result_file_path = ""
    web_science_username = ""
    web_science_password = ""
    continue_write = 0
    where_to_start = 0
    first_by_title = 0
    failed_file_name = ""
    create_fail_file = 0
    max_retracted_articles_number = 0
    max_retraction_notices_number = 0
    max_retraction_notice_citations_number = 0
    max_retracted_article_citations_number = 0
    max_miscitation_result_number = 0
    miscitaion_or_not = 0

    def __init__(self, name, password):
        self.web_science_username = name
        self.web_science_password = password
        self.retracted_articles_path = ""
        self.retraction_notices_path = ""
        self.retraction_notice_citations_path = ""
        self.retracted_article_citations_path = ""
        self.miscitation_result_file_path = ""
        self.continue_write = 0
        self.where_to_start = 0
        self.first_by_title = 0
        self.failed_file_name = ""
        self.create_fail_file = 0
        self.max_retracted_articles_number = 0
        self.max_retraction_notices_number = 0
        self.max_retraction_notice_citations_number = 0
        self.max_retracted_article_citations_number = 0
        self.max_miscitation_result_number = 0
        self.miscitaion_or_not = 0

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


def login_to_serach_page(browser,username,password):
    try:
        browser.get("https://login.webofknowledge.com")
        browser.find_element_by_css_selector("input[name=username]").send_keys(username)
        browser.find_element_by_css_selector("input[name=password]").send_keys(password)
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


def get_status(browser):
    try:
        browser.execute(Command.STATUS)
        return "Alive"
    except (socket.error, httplib.CannotSendRequest):
        return "Dead"


def write_failed_info(article_title, fail_indormation,row_index,
                      create_fail_file,continue_write,failed_file_name):
    print "write failed info start======================================="
    if create_fail_file == 1:
        if continue_write == 0:
            try:
                os.remove(failed_file_name)
            except:
                print "fail infomation file already removed"
        row = [article_title,fail_indormation,row_index]
        with open(failed_file_name,"ab") as in_csv:
            print "{0!s} open success!".format(failed_file_name)
            writer = csv.writer(in_csv)
            writer.writerow(row)

def modify_config_file(newwhere):
    copyname = "copyconfig"
    configcopy = "{}\scripts\{}".format(
                    os.path.dirname(os.getcwd()),copyname)
    with open(CONFIGRATION_FILE_NAME, "r+") as r_file:
        with open(configcopy, 'w') as w_file:
            for line in r_file:
                newline = line.replace('=', ' ').replace('/n', ' ').split()
                if newline[0] == "WHERE_TO_START":
                    w_file.write("WHERE_TO_START = {} (Must be an integer >=0 )\n".format(newwhere))
                elif newline[0] == "CONTINUE_WRITE":
                    w_file.write("CONTINUE_WRITE = 1 (1 for append 0 for overwrite)\n")
                else:
                    w_file.write(line)
    #Remove original file
    os.remove(CONFIGRATION_FILE_NAME)
    #Move new file
    os.rename(configcopy,CONFIGRATION_FILE_NAME)
