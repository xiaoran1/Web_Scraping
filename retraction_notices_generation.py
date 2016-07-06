from General_browser_function_handle import *

CONINFO = Config_Data("", "")

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
                CONINFO.retraction_notices_path= line[1]
            if line[0] == "FAILED_FILE_NAME":
                CONINFO.failed_file_name = line[1]
            if line[0] == "MAX_RETRACTION_NOTICES_NUMBER":
                CONINFO.max_retraction_notices_number = int(line[1].replace(',', ''))
            if line[0] == "CONTINUE_WRITE":
                continue_write = int(line[1].replace(',', ''))
                CONINFO.continue_write = ("ab" if continue_write == 1 else "wb")
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
            "//span[@class='searchButton']/input[@id='UA_GeneralSearch_input_form_sb']")
        search_buttons[len(search_buttons)-1].click()
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


def loop_through_record_and_download(browser, upper_bound, row_index):
    start_from = 0
    end_by = 0
    if CONINFO.where_to_start > 0:
        start_from = CONINFO.where_to_start
        end_by = CONINFO.where_to_start
    try:
        while upper_bound > 0:
            if upper_bound > 500:
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
                end_by += upper_bound
            print "search from ", start_from, " to ", end_by
            browser,error_not_go_beyond = mark_and_download_data(browser, end_by, start_from)
            if error_not_go_beyond:
                if get_status(browser) == "Dead":
                    raise Exception, 'browser already quit'
                while not os.path.isfile(DOWNLOAD_FILE):
                    if get_status(browser) == "Dead":
                        raise Exception, 'browser already quit'
                    continue
                add_download_data_to_csv_file(CONINFO.retraction_notices_path, row_index,start_from)
            else:
                return browser
            # Reduce the upper case by 500 to see if there are still left records haven't been downloaded
            upper_bound -= 500
            if upper_bound < 0:
                upper_bound = 0
            else:
                browser.refresh()
    except Exception as e:
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
                    with open(csv_file, CONINFO.continue_write) as out_csv:
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


def get_retraction_list():
    upper_bound = 0
    if CONINFO.continue_write == 0:
        try:
            os.remove(CONINFO.retraction_notices_path)
        except Exception:
            print "retraction list file already been removed"
    browser = setup_webdriver("chrome")
    try:
        remove_extra_file()
        browser = login_to_serach_page(browser,CONINFO.web_science_username,CONINFO.web_science_password)
        if get_status(browser) == "Dead":
            raise Exception, 'browser already quit'
        # start searching for retracted articles
        browser = do_search(browser,"retraction of")
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
        upper_bound = CONINFO.max_retraction_notices_number
        browser = loop_through_record_and_download(browser,upper_bound,0)
        time.sleep(2)
    except Exception, e:
        browser.quit()
        logging.exception(e)
        pass
    finally:
        browser.quit()
    return

if __name__ == '__main__':
    try:
        read_from_config()
        if (CONINFO.web_science_password == "" or CONINFO.web_science_username == ""
            or CONINFO.retraction_notices_path == ""
            or CONINFO.failed_file_name==""):
            raise Exception('something wrong with config file')
        print "Start the generation of retraction notices list "
        print "This will return you {0!s} records".format((CONINFO.max_retraction_notices_number))
        print "Start from record: {0!s}".format((CONINFO.where_to_start))
        # out_file = generate_more_column(RETRACTION_LIST_PATH)
        # RETRACTION_LIST_PATH =out_file
        get_retraction_list()
    finally:
        print "Quit the main program"
    sys.exit(0)

