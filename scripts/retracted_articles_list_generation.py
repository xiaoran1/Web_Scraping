# This script can generate a retracted article information list in the csv format
# it will take out each row from the retracted notices list file and
# use each row's author, publication year and publication name for doing
# the search in web of science, the search results will then be sorted by time cited,
# the program then will download the articles' detailed information with highest time cited into a csv file.


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
            if line[0] == "RETRACTED_ARTICLES_FILE_PATH":
                CONINFO.retracted_articles_path= "{}\data\{}".format(
                    os.path.dirname(os.getcwd()),line[1])
            if line[0] == "FAILED_FILE_NAME":
                CONINFO.failed_file_name = "{}\data\{}".format(
                    os.path.dirname(os.getcwd()),line[1])
            if line[0] == "MAX_RETRACTED_ARTICLES_NUMBER":
                CONINFO.max_retracted_articles_number = int(line[1].replace(',', ''))
            if line[0] == "CONTINUE_WRITE":
                CONINFO.continue_write = int(line[1].replace(',', ''))
            if line[0] == "WHERE_TO_START":
                CONINFO.where_to_start = int(line[1].replace(',', ''))
            if line[0] == "CREATE_FAIL_FILE":
                CONINFO.create_fail_file = int(line[1].replace(',', ''))
            if line[0] == "MISCITAION_OR_NOT":
                CONINFO.miscitaion_or_not = int(line[1].replace(',', ''))



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

def do_search(browser, publication_name, year, authorlist,second_search, title):
    field_index = 1
    author_num = 0
    try:
        resetform = []
        resetform = browser.find_elements_by_xpath("//span[@class='search-criteria-link j-clear-criteria']/a")
        resetform[len(resetform)-1].click()
        if title == "":
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
        else:
            browser = add_search_condition(browser, title, "Title", field_index)
        search_buttons = []
        search_buttons = browser.find_elements_by_xpath(
            "//span[@class='searchButton']/input[@title='Search']")
        search_buttons[len(search_buttons)-1].click()
    except Exception, e:
        logging.exception(e)
    return browser


def download_data(browser, end, start):
    try:
        # do sorting by publish date
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH,
                                                                         "//div[@id='s2id_selectSortBy_.top']/a/span[@class='select2-arrow']/b")))
        browser.find_element_by_xpath(
            "//div[@id='s2id_selectSortBy_.top']/a/span[@class='select2-arrow']/b").click()
        browser.find_element_by_xpath("//div[text()=' Times Cited -- highest to lowest ']").click()
        # Start download
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
        try:
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='quickoutput-overlay-buttonset']")))
            browser.find_element_by_xpath("//div[@class='quickoutput-overlay-buttonset']/a").click()
        except Exception, e:
            pass
    except Exception, e:
        logging.exception(e)
        browser.quit()
    return browser


def get_article_data(browser, row_index):
    try:
        remove_extra_file()
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@id='s2id_saveToMenu']")))
        browser = download_data(browser, 1, 1)
        if get_status(browser) == "Dead":
            raise Exception, 'browser already quit'
        while not os.path.isfile(DOWNLOAD_FILE):
            if get_status(browser) == "Dead":
                raise Exception, 'browser already quit'
            continue
        add_download_data_to_csv_file(CONINFO.retracted_articles_path, row_index)
        browser.find_element_by_xpath("//h1[@class='titleh1']/a").click()
    except Exception, e:
        logging.exception(e)
        browser.quit()
    return browser


def add_download_data_to_csv_file(dest_path, row_index):
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
                                        line.append(row_index)
                                    write_to.writerow(line)
                        else:
                            # if this is not the first time accessing the target file
                            for line in read_in:
                                if is_head == 1:
                                    is_head = 0
                                else:
                                    if row_index > 0:
                                        line.append(row_index)
                                    write_to.writerow(line)
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
            os.remove(CONINFO.retracted_articles_path)
        except Exception:
            print "Citation list file already been removed"
    browser = setup_webdriver("chrome")
    try:
        browser = login_to_serach_page(browser,CONINFO.web_science_username,CONINFO.web_science_password)
        is_column_head = True
        csv_file = CONINFO.retraction_notices_path
        with open(csv_file, "rb") as miscitation_list_file:
            list_reader = csv.reader(miscitation_list_file)
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
                    if CONINFO.where_to_start > 0 and where > CONINFO.where_to_start+198:
                        browser.quit()
                        CONINFO.first_by_title = 0
                        browser = setup_webdriver("chrome")
                        browser = login_to_serach_page(browser,CONINFO.web_science_username,CONINFO.web_science_password)
                    #collect search information
                    article_title = row[title_col]
                    authorstring = row[author_col]
                    if authorstring != "[Anonymous]":
                        authorlist = authorstring.split(";")
                    year = row[year_col]
                    publication_name = row[pub_name_col]
                    if year == "" or len(authorlist) < 1 or publication_name == "":
                        continue
                    if CONINFO.max_retracted_articles_number != 0:
                        if test_time >= CONINFO.max_retracted_articles_number:
                            continue
                    print ("{} Article title for search is: {}".format(row_index, article_title))
                    # Start to obtain citations with each title
                    if(CONINFO.miscitaion_or_not == 1):
                        article_title  = "\"{}\"".format(article_title)
                    else:
                        article_title = ""
                    browser = do_search(browser,publication_name,year,authorlist,False,article_title)
                    test_time += 1
                    if get_status(browser) == "Dead":
                        raise Exception, 'browser already quit'
                    try:
                        not_found = browser.find_element_by_xpath(
                            "//div[@class='errorMessage'][@id='noRecordsDiv']")
                        if(article_title!=""):
                            browser = do_search(browser, publication_name, year, authorlist, True,article_title)
                            not_found = browser.find_element_by_xpath(
                                "//div[@class='errorMessage'][@id='noRecordsDiv']")
                        write_failed_info(article_title,"no record found error",row_index,
                                          CONINFO.create_fail_file,CONINFO.continue_write,CONINFO.failed_file_name)
                        continue
                    except:
                        pass
                    try:
                        not_found = browser.find_element_by_xpath(
                            "//div[@class='errorMessage'][@id='searchErrorMessage']")
                        write_failed_info(article_title,"search name error",row_index,
                                          CONINFO.create_fail_file, CONINFO.continue_write, CONINFO.failed_file_name)
                        continue
                    except:
                        pass
                    browser = get_article_data(browser, row_index)
                    if get_status(browser) == "Dead":
                        raise Exception, 'browser already quit'
    except Exception, e:
        print "take_out_title_from_retraction_list error", e
        browser.quit()
    finally:
        print "done taking out titles from retraction list for gathering citations"
        browser.quit()
        return row_index

if __name__ == '__main__':
    try:
        read_from_config()
        if (CONINFO.web_science_password == "" or CONINFO.web_science_username == ""
            or CONINFO.retraction_notices_path == ""
            or CONINFO.retracted_articles_path == ""
            or CONINFO.failed_file_name==""):
            raise Exception('something wrong with config file')
        print "Start the generation of retracted articles list "
        end_row = 0
        while(end_row < CONINFO.max_retracted_articles_number):
            end_row = take_out_title_from_retraction_list()
            modify_config_file(end_row)
            read_from_config()
    finally:
        print "Quit the main program"
    sys.exit(0)

