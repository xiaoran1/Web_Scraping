## Scrape Web of Science

Collect list of articles that are eventually retracted, and articles that cite retracted articles. 

### Installation

**Requirements:**  
1. Please have Python(2.7) and selenium installed  
2. In order to run the program smoothly, please make sure it is running with a stable and high internet speed.  
3. This program needs the user to have Chrome with the latest version (at least 51.0.2704.84).  
4. Make sure the chromedriver.exe(download it at https://sites.google.com/a/chromium.org/chromedriver/, version>=2.22) is at the same path as the main script while running

**Installation:**  
1. Clone the repository  
2. Navigate to Web_Scraping  
3. To install required libraries:
```
 pip install -r requirements.txt 
```

### Usage: 

```
python retraction_notices_generation.py
python generate_new_retractionlist.py
python retraction_notice_citations_generation.py
python retracted_articles_list_generation.py
python retracted_article_citations_generation.py
python web_scraping_miscitation.py
```

### 2 Modes:

General web scraping files generation(not miscitation): 

1. Run retraction_notices_generation 

2. Run generate_new_retractionlist 

3. Run one of retraction_notice_citations_generation.py, retracted_articles_list_generation.py 
   retracted_article_citations_generation.py, no specific orders needed for this step, make sure name each 
   file with different name in the config file. 

Miscitation part files generation: 

1. Naming the RETRACTION_NOTICES_FILE_PATH in the config file as the article list file that you want to use for search 

2. Run retraction_notices_generation 

3. Run generate_new_retractionlist 

4. Run retracted_articles_list_generation 

5. Rename RETRACTION_NOTICES_FILE_PATH as the one you just generate for step 4, then running retracted_article_citations_generation.py 

6. Run web_scraping_miscitation.py 



### config file:

Each parameters within the configuration file:

* RETRACTED_ARTICLES_FILE_PATH: How the user wants to name the retraced articles' list file (must end by .csv)

* RETRACTION_NOTICES_FILE_PATH: How the user wants to name the retraced notices' list file (must end by .csv)

* RETRACTION_NOTICE_CITATIONS_FILE_PATH: How the user wants to name the retraced notices' citaions' list file (must end by .csv)

* RETRACTED_ARTICLE_CITATIONS_FILE_PATH: How the user wants to name the retraced articles' citations' list file (must end by .csv)

* FAILED_FILE_NAME: How the user wants to name The file that stored the failed search information. (must end by .csv)

* MISCITATION_RESULT_FILE_PATH: How the user wants to name the file of the list of each article's citations' download link url (must end by .csv)

* WEB_SCIENCE_USERNAME & WEB_SCIENCE_PASSWORD: User's email address and password that used to log into Web of Science

* All the MAX_**_NUMBER: How many records the user want to get for running the scripts(each ** will correspond to each path file name)

* CONTINUE_WRITE: Do you want to overwrite the existing information or not, if set to be 0, the program will clean all the existing information within the generated file and replace with the new data.(Only available for citation list only mode or retraction list only mode)

* WHERE_TO_START: Only useful when CONTINUE_WRITE been set to 1, tell the program where to start (which row or title to be the first one used for search)

* CREATE_FAIL_FILE: If the user wants to create a file for recording the failed title search information, set this to 1, otherwise set it to 0 

* MISCITAION_OR_NOT: This will only set to be 1 if the user just want to generate files for miscitation part.


### Possible Failed Search Conditions: 

* Web of Science cannot find any record match the title.  

* The article used for search has been cited 0 time. 


### Potential problem with web scraping project:

* problem:
Search result number change problem:
for example, user search "retraction of" and then do the refine of "RETRACTION" and "CORRECTION ", 
then sort by "times cited-highest to lowest", it will show there are 9599 records in total on the left hand side, 
but when user does the marking, it shows there are only 5876 records instead(Specifically ,
if you click "Add to Marked list" and fill the condition with "from 5500 to 6000", 
then it will show you only 377 records get saved and the number (originally 9599) on the left side will become 5876. 

* reason:
the 9k results include duplications, when user doing the mark the web of science system might change the searched result to filter out the duplications. 

### Author and Contact Information

Xiaoran Huang. If you have any problems please contact through email: [wscqkevin@gmail.com](mailto:wscqkevin@gmail.com) or open an issue.
