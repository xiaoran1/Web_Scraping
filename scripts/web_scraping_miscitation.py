from General_browser_function_handle import *

CONINFO = Config_Data("", "")

def read_from_config():
    global CONINFO
    with open(CONFIGRATION_FILE_NAME, "r+") as my_config:
        for line in my_config:
            line = line.replace('=', ' ').replace('/n', ' ').split()
            if line[0] == "RETRACTED_ARTICLE_CITATIONS_FILE_PATH":
                CONINFO.retracted_article_citations_path= "{}\data\{}".format(
                    os.path.dirname(os.getcwd()),line[1])
            if line[0] == "FAILED_FILE_NAME":
                CONINFO.failed_file_name = "{}\data\{}".format(
                    os.path.dirname(os.getcwd()),line[1])
            if line[0] == "MISCITATION_RESULT_FILE_PATH":
                CONINFO.miscitation_result_file_path = "{}\data\{}".format(
                    os.path.dirname(os.getcwd()),line[1])
            if line[0] == "MAX_MISCITATION_RESULT_NUMBER":
                CONINFO.max_miscitation_result_number= int(line[1].replace(',', ''))
            if line[0] == "CONTINUE_WRITE":
                CONINFO.continue_write = int(line[1].replace(',', ''))
            if line[0] == "WHERE_TO_START":
                CONINFO.where_to_start = int(line[1].replace(',', ''))
            if line[0] == "CREATE_FAIL_FILE":
                CONINFO.create_fail_file = int(line[1].replace(',', ''))



def do_search(browser, title, authors):
    if title == "" or len(authors) == 0:
        return browser
    else:
        full_author_string = ""
        for author in authors:
            #Create a new name string in the format of "full last name" plus initials of the rest
            final_name = author
            name_pos_list = author.split(",")
            initials = ""
            for i, item in enumerate(name_pos_list):
                if i > 0:
                    initials += item.strip()[0]
            final_name = "author:{} {}, ".format(initials,name_pos_list[0])
            full_author_string += final_name
        search_content = "{} {}".format(title,full_author_string)
        print search_content
        try:
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH,
                                         "//input[@class='gs_in_txt'][@type='text']")))
            search_input_field = browser.find_element_by_xpath("//input[@class='gs_in_txt'][@type='text']")
            search_input_field.clear()
            search_input_field.send_keys(search_content)
            browser.find_element_by_xpath("//button[@id='gs_hp_tsb'][@type='submit']"
                                          "[@class='gs_btnG gs_in_ib gs_btn_act gs_btn_eml']").click()
        except Exception, e:
            logging.exception(e)
    return browser


def download_URL(browser,row_index,article_title):
    print row_index
    try:
        browser.find_element_by_xpath("//span[@class='recaptcha-checkbox goog-inline-block recaptcha-checkbox-unchecked rc-anchor-checkbox']"
                                      "[@role='checkbox']/div[@class='recaptcha-checkbox-checkmark']").click()
    except:
        pass
    try:
        url_element = browser.find_element_by_xpath("//div[@id='gs_ggsW0']/a")
        url_address =  url_element.get_attribute("href")
        add_data_to_csv_file(CONINFO.miscitation_result_file_path,row_index,url_address)
    except:
        # no download link handle
        try:
            if get_status(browser) == "Dead":
                raise Exception, 'browser already quit'
            write_failed_info(article_title, "no download url found", row_index,
                              CONINFO.create_fail_file, CONINFO.continue_write, CONINFO.failed_file_name)
            browser.get("https://scholar.google.ca/")
        except Exception, e:
            pass
            browser.quit()
    return browser


def add_data_to_csv_file(dest_path, row_index,url_address):
    print "add_data_to_csv_file  ",row_index
    is_column_head = 1
    if os.path.isfile(dest_path):
        is_column_head = 0
    print "is_column_head:", is_column_head
    csv_file = dest_path
    with open(csv_file, "ab") as out_csv:
        write_to = csv.writer(out_csv)
        print "{0!s} open success!".format(dest_path)
        if is_column_head == 1:
            # if this is the first time accessing the target file
            write_to.writerow(["URL","Index"])
            write_to.writerow([url_address, row_index])
            is_column_head = 0
        else:
            # if this is not the first time accessing the target file
            write_to.writerow([url_address, row_index])
    print "=====================Done import============================"
    return


def take_out_title_from_articles_list():
    test_time = 0
    where = 0
    row_index = 0
    is_column_head = True
    read_in_file = CONINFO.retracted_article_citations_path
    #init column information
    take_out_col_num = 1
    title_col = 0
    author_col = 0
    if CONINFO.continue_write == 0:
        try:
            os.remove(CONINFO.miscitation_result_file_path)
        except Exception:
            print "miscitation result file already been removed"
    browser = setup_webdriver("chrome")
    try:
        browser.get("https://scholar.google.ca/")
        with open(read_in_file, "rb") as retracted_article_citations_path:
            list_reader = csv.reader(retracted_article_citations_path)
            for row in list_reader:
                authorlist = []
                if is_column_head:
                    if take_out_col_num == 1:
                        for i, coltext in enumerate(row):
                            if coltext == "AU":
                                author_col = i
                            if coltext == "TI":
                                title_col = i
                        take_out_col_num = 0
                    is_column_head = False
                    continue
                else:
                    article_title = row[title_col]
                    authorstring = row[author_col]
                    if authorstring != "[Anonymous]":
                        authorlist = authorstring.split(";")
                    if CONINFO.max_miscitation_result_number != 0:
                        if test_time >= CONINFO.max_miscitation_result_number:
                            break
                    where += 1
                    row_index += 1
                    if CONINFO.where_to_start > 0 and where < CONINFO.where_to_start:
                        continue
                    if CONINFO.where_to_start > 0 and where > CONINFO.where_to_start + 198:
                        browser.quit()
                        browser = setup_webdriver("chrome")
                        browser.get("https://scholar.google.ca/")

                    #Surrond article title with double quotes in order to avoid special characters
                    new_article_title = "\"{}\"".format(article_title)
                    print ("{} Article title for search is: {}".format(row_index, new_article_title))

                    # Start search the article in google scholar with title and authors
                    browser = do_search(browser, new_article_title,authorlist)
                    test_time += 1
                    #check if no record found
                    if get_status(browser) == "Dead":
                        raise Exception, 'browser already quit'
                    try:
                        not_found = browser.find_element_by_xpath(
                            "//blockquote[@class='gs_med']")
                        write_failed_info(article_title,"no record found error",row_index,
                                          CONINFO.create_fail_file,CONINFO.continue_write,CONINFO.failed_file_name)
                        browser.get("https://scholar.google.ca/")
                        continue
                    except:
                        pass
                    #if there are records then save the download URL
                    browser = download_URL(browser,row_index,new_article_title)
                    if get_status(browser) == "Dead":
                        raise Exception, 'browser already quit'
                    browser.get("https://scholar.google.ca/")
    except Exception, e:
        print e
        browser.quit()
    finally:
        browser.quit()
    return

if __name__ == '__main__':
    try:
        read_from_config()
        print CONINFO.retracted_article_citations_path
        if (CONINFO.retracted_article_citations_path == ""
            or CONINFO.miscitation_result_file_path == ""
            or CONINFO.failed_file_name==""):
            raise Exception('something wrong with config file')
        print "Start the generation of miscitaion result list with pdf URL "
        print "max_miscitation_result_number is {0!s}".format((CONINFO.max_miscitation_result_number))
        take_out_title_from_articles_list()
    finally:
        print "Quit the main program"
    sys.exit(0)

