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
            if line[0] == "RETRACTED_ARTICLE_CITATIONS_FILE_PATH":
                CONINFO.retracted_article_citations_path = line[1]
            if line[0] == "MAX_RETRACTED_ARTICLE_CITATIONS_NUMBER":
                CONINFO.max_retracted_article_citations_number= int(line[1].replace(',', ''))
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

def do_search(browser, publication_name, year, authorlist,second_search):
    field_index = 1
    author_num = 0
    try:
        resetform = []
        resetform = browser.find_elements_by_xpath("//span[@class='search-criteria-link j-clear-criteria']/a")
        resetform[len(resetform)-1].click()
        browser = add_search_condition(browser, publication_name, "Publication Name", field_index)
        field_index += 1
        browser = add_search_condition(browser, year,"Year Published",field_index)
        for single_author in authorlist:
            #Create a new name string in the format of "full last name" plus initials of the rest
            final_name = single_author
            name_pos_list = single_author.split(",")
            initials = ""
            for i, item in enumerate(name_pos_list):
                if i > 0:
                    initials += item.strip()[0]
            final_name = "{}, {}".format(name_pos_list[0], initials)
            if second_search:
                if author_num >= 2:
                    break
                else:
                    field_index += 1
                    browser = add_search_condition(browser, final_name, "Author", field_index)
                    author_num += 1
            else:
                field_index += 1
                browser = add_search_condition(browser, final_name,"Author",field_index)
        search_buttons = []
        search_buttons = browser.find_elements_by_xpath(
            "//span[@class='searchButton']/input[@id='UA_GeneralSearch_input_form_sb']")
        search_buttons[len(search_buttons)-1].click()
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
            add_download_data_to_csv_file(CONINFO.retracted_article_citations_path, row_index,start_from)
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


def get_citation_data(browser, row_index,article_title):
    try:
        remove_extra_file()
        if CONINFO.first_by_title == 0:
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


def take_out_title_from_retraction_list():
    test_time = 0
    where = 0
    remove_extra_file()
    row_index = 0
    #column index value init
    take_out_col_num = 1
    author_col = 0
    year_col = 0
    title_col = 0
    pub_name_col = 0
    if CONINFO.continue_write == 0:
        try:
            os.remove(CONINFO.retracted_article_citation_path)
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
                year = ""
                publication_name = ""
                authorlist = []
                if take_out_col_num == 1:
                    for i, coltext in enumerate (row):
                        if coltext == "year":
                            year_col = i
                        if coltext == "AU":
                            author_col = i
                        if coltext == "TI":
                            title_col = i
                        if coltext == "SO":
                            pub_name_col = i
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
                    authorstring = row[author_col]
                    if authorstring != "[Anonymous]":
                        authorlist = authorstring.split(";")
                    year = row[year_col]
                    publication_name = row[pub_name_col]
                    if year == "" or len(authorlist) < 1 or publication_name == "":
                        continue
                    if CONINFO.max_retracted_article_citations_number != 0:
                        if test_time >= CONINFO.max_retracted_article_citations_number:
                            continue
                    new_article_title = unicode(article_title, errors='ignore')
                    print ("{} Article title for search is: {}".format(row_index, new_article_title))
                    # Start to obtain citations with each title
                    browser = do_search(browser, publication_name,year,authorlist,False)
                    test_time += 1
                    if get_status(browser) == "Dead":
                        raise Exception, 'browser already quit'
                    try:
                        not_found = browser.find_element_by_xpath(
                            "//div[@class='errorMessage'][@id='noRecordsDiv']")
                        browser = do_search(browser, publication_name, year, authorlist, True)
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
        print CONINFO.retracted_article_citations_path
        if (CONINFO.web_science_password == "" or CONINFO.web_science_username == ""
            or CONINFO.retraction_notices_path == ""
            or CONINFO.retracted_article_citations_path == ""
            or CONINFO.failed_file_name==""):
            raise Exception('something wrong with config file')
        print "Start the generation of retracted article citations list "
        print "max_citation_number {0!s}".format((CONINFO.max_retracted_article_citations_number))
        # out_file = generate_more_column(RETRACTION_LIST_PATH)
        # RETRACTION_LIST_PATH =out_file
        take_out_title_from_retraction_list()
    finally:
        print "Quit the main program"
    sys.exit(0)

