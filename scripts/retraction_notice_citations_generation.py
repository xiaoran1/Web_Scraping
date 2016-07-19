# This script can generate a retracted notice citations list in the csv format
# it will take out each row from the retracted notices list file and
# use each row's author, publication year and publication name for doing
# the search in web of science, the search results will then be sorted by times cited,
# the program then will click into the article with highest times cited and download the each
# results' detailed information that cited to that article into a csv file.

from General_browser_function_handle import *

CONINFO = ConfigData("", "")

def read_from_config():
    global CONINFO
    with open(CONFIGRATION_FILE_NAME, "r+") as my_config:
        for line in my_config:
            line = line.replace('=', ' ').replace('/n', ' ').split()
            if line[0] == "WEB_SCIENCE_USERNAME":
                CONINFO.web_science_username = line[1]
            if line[0] == "WEB_SCIENCE_PASSWORD":
                CONINFO.web_science_password = line[1]
            if line[0] == "RETRACTION_NOTICES_FILE_PATH":
                CONINFO.retraction_notices_path= "{}\data\{}".format(
                    os.path.dirname(os.getcwd()),line[1])
            if line[0] == "FAILED_FILE_NAME":
                CONINFO.failed_file_name = "{}\data\{}".format(
                    os.path.dirname(os.getcwd()),line[1])
            if line[0] == "RETRACTION_NOTICE_CITATIONS_FILE_PATH":
                CONINFO.retraction_notice_citations_path = "{}\data\{}".format(
                    os.path.dirname(os.getcwd()),line[1])
            if line[0] == "MAX_RETRACTION_NOTICE_CITATIONS_NUMBER":
                CONINFO.max_retraction_notice_citations_number= int(line[1].replace(',', ''))
            if line[0] == "CONTINUE_WRITE":
                CONINFO.continue_write = int(line[1].replace(',', ''))
            if line[0] == "WHERE_TO_START":
                CONINFO.where_to_start = int(line[1].replace(',', ''))
            if line[0] == "CREATE_FAIL_FILE":
                CONINFO.create_fail_file = int(line[1].replace(',', ''))


def add_search_condition(browser, search_input, search_type,field_index):
    if search_input != "":
        # add input field
        if field_index > 1:
            ww = []
            ww = browser.find_elements_by_xpath("//div[@class='search-criteria-action add-search-row']/"
                                                "span[@class='search-criteria-link j-add-criteria']/a")
            ww[len(ww) - 1].click()
        # add search content
        search_query = "//div[@id='container(input"+str(field_index)+")']/input[@type='text']"
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, search_query)))
        input_field = browser.find_element_by_xpath(search_query)
        input_field.clear()
        input_field.send_keys(search_input)
        # select search type
        search_query1 = "//tr[@id='searchrow" + str(field_index) + "']/td[@class='search-criteria-cell2']/" \
                       "div/a/span[@class='select2-arrow']/b"
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH,search_query1)))
        browser.find_element_by_xpath(search_query1).click()
        typelist = []
        search_query2 = "//li[@class='select2-results-dept-0 select2-result select2-result-selectable']/div[text()='"+search_type+"']"
        browser.find_element_by_xpath(search_query2).click()
    return browser

def do_search(browser, article_name):
    field_index = 1
    try:
        resetform = []
        resetform = browser.find_elements_by_xpath("//span[@class='search-criteria-link j-clear-criteria']/a")
        resetform[len(resetform)-1].click()
        browser = add_search_condition(browser, article_name, "Title", field_index)
        search_buttons = []
        search_buttons = browser.find_elements_by_xpath(
            "//span[@class='searchButton']/input[@title='Search']")
        search_buttons[len(search_buttons)-1].click()
    except Exception, e:
        logging.exception(e)
    return browser


def download_data(browser, end, start):
    noerror = True
    try:
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@id='s2id_saveToMenu']")))
        divarray = []
        divarray = browser.find_elements_by_xpath("//div[@id='s2id_saveToMenu']/a/span[@class='select2-arrow']/b")
        divarray[0].click()
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


def loop_through_record_and_download(browser, row_index):
    start_from = 0
    end_by = 0
    total_citing_number = browser.find_element_by_xpath("//span[@id='hitCount.top']").get_attribute("innerHTML")
    record_count = int(total_citing_number.replace(',', ''))
    print "actual cited times: ", record_count
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
            browser,error_not_go_beyond = download_data(browser, end_by, start_from)
            if error_not_go_beyond:
                if get_status(browser) == "Dead":
                    raise Exception, 'browser already quit'
                while not os.path.isfile(DOWNLOAD_FILE):
                    if get_status(browser) == "Dead":
                        raise Exception, 'browser already quit'
                    continue
                add_download_data_to_csv_file(CONINFO.retraction_notice_citations_path, row_index,start_from)
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
        if CONINFO.first_by_title == 0:
            # do sorting by publish date
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH,
                                                                             "//div[@id='s2id_selectSortBy_.top']/a/span[@class='select2-arrow']/b")))
            browser.find_element_by_xpath(
                "//div[@id='s2id_selectSortBy_.top']/a/span[@class='select2-arrow']/b").click()
            browser.find_element_by_xpath("//div[text()=' Times Cited -- highest to lowest ']").click()
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
                browser = loop_through_record_and_download(browser, row_index)
                browser.find_element_by_xpath("//h1[@class='titleh1']/a").click()
        except:
            print "{0!s} has not been cited yet !".format(article_title)
            write_failed_info(article_title, "no record found error", row_index,
                              CONINFO.create_fail_file, CONINFO.continue_write, CONINFO.failed_file_name)
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
                    with open(csv_file, "ab") as out_csv:
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
    test_time = 0
    where = 0
    remove_extra_file()
    row_index = 0
    #column index value init
    take_out_col_num = 1
    title_col = 0
    if CONINFO.continue_write == 0:
        try:
            os.remove(CONINFO.retraction_notice_citations_path)
        except Exception:
            print "Citation list file already been removed"
    browser = setup_webdriver("chrome")
    try:
        browser = login_to_serach_page(browser, CONINFO.web_science_username, CONINFO.web_science_password)
        is_column_head = True
        csv_file = CONINFO.retraction_notices_path
        with open(csv_file, "rb") as retraction_list_file:
            list_reader = csv.reader(retraction_list_file)
            for row in list_reader:
                if take_out_col_num == 1:
                    for i, coltext in enumerate (row):
                        if coltext == "TI":
                            title_col = i
                    take_out_col_num = 0
                if is_column_head:
                    is_column_head = False
                    continue
                else:
                    where += 1
                    row_index += 1
                    if CONINFO.where_to_start > 0 and where < CONINFO.where_to_start:
                        continue
                    if CONINFO.where_to_start > 0 and where > CONINFO.where_to_start + 198:
                        browser.quit()
                        CONINFO.first_by_title = 0
                        browser = setup_webdriver("chrome")
                        browser = login_to_serach_page(browser, CONINFO.web_science_username,
                                                       CONINFO.web_science_password)
                    #collect search information
                    article_title = row[title_col]
                    if CONINFO.max_retraction_notice_citations_number != 0:
                        if test_time >= CONINFO.max_retraction_notice_citations_number:
                            continue
                    new_article_title = "\"{}\"".format(article_title)
                    print ("{} Article title for search is: {}".format(row_index, new_article_title))
                    # Start to obtain citations with each title
                    browser = do_search(browser, new_article_title)
                    test_time += 1
                    if get_status(browser) == "Dead":
                        raise Exception, 'browser already quit'
                    try:
                        not_found = browser.find_element_by_xpath(
                            "//div[@class='errorMessage'][@id='noRecordsDiv']")
                        write_failed_info(article_title, "no record found error", row_index,
                                          CONINFO.create_fail_file, CONINFO.continue_write, CONINFO.failed_file_name)
                        continue
                    except:
                        pass
                    try:
                        not_found = browser.find_element_by_xpath(
                            "//div[@class='errorMessage'][@id='searchErrorMessage']")
                        write_failed_info(article_title, "no record found error", row_index,
                                          CONINFO.create_fail_file, CONINFO.continue_write, CONINFO.failed_file_name)
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

if __name__ == '__main__':
    try:
        read_from_config()
        print CONINFO.retraction_notice_citations_path
        if (CONINFO.web_science_password == "" or CONINFO.web_science_username == ""
            or CONINFO.retraction_notices_path == ""
            or CONINFO.retraction_notice_citations_path == ""
            or CONINFO.failed_file_name==""):
            raise Exception('something wrong with config file')
        print "Start the generation of retracted article citations list "
        print "max_retraction_notice_citations_number {0!s}".format((CONINFO.max_retraction_notice_citations_number))
        take_out_title_from_retraction_list()
    finally:
        print "Quit the main program"
    sys.exit(0)

