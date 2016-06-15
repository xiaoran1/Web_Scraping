## Scrape Web of Science

**Author:** Xiaoran Huang

**Aim:** This project is for collecting the retracted articles' information and the articles that cite them.

**Preparation:**  
1. Please have Python(2.7) and selenium installed  
2. In order to run the program smoothly, please make sure it is running with a stable and high internet speed.  
3. This program needs the user to have Chrome with the latest version (at least 51.0.2704.84).  
4. Make sure the chromedriver.exe is at the same path as the main script while running

**Installation:**  
1. Clone the repository  
2. Navigate to Web_Scraping
3. Follow the requirements

### How to run: 

just click the web_scraping.py or run command by 
```
python web_scraping.py
```

### Configuration.config file information:

The program provides 4 different modes as the user can decide to use which one by change the configuration file:

* **Mode 1:**  
  * CITATION_LIST_ONLY: This parameter can be either 1 or 0, if the user choose to set it as 1, the program will consider the user only want to do the citation list generation (Please pay attention that if you want to use this mode there must be a retracted article list file that already existed in the directory path that same as the script)
  
  * MAX_CITATION_NUMBER: This parameter can only be set to an integer that greater than 0, it shows that maximum title number (within the retraction list) that the user wants to search for citation list generation.

* **Mode 2:**   
  * RETRACTION_LIST_ONLY: This parameter can be either 1 or 0, if the user choose to set it as 1, the program will consider the user only want to do the retraction list generation

  * MAX_RETRACTION_NUMBER: This parameter can only be set to an integer that greater than 0, it shows that maximum retracted article number that the user wants to get for retracted article information list generation. (For example, if it is setting to 500 means you want to have 500 rows of records in your generated retracted article list file)

* **Mode 3:** If the above 2 parameters (CITATION_LIST_ONLY and RETRACTION_LIST_ONLY) both set to 0, the program will just execute both file's generation without any upper bound limitation( in this case, the variable MAX_CITATION_NUMBER and MAX_RETRACTION_NUMBER won't affect the program any more)

* **Mode 4:** If the above 2 variables both set to 1. This is for the test only.

Other parameters within the configuration file:

* RETRACTION_LIST_NAME: How the user wants to name the retraced article information list file (must end by .csv)

* CITATION_LIST_NAME: How the user wants to name the cited article information list file (must end by .csv)

* WEB_SCIENCE_USERNAME & WEB_SCIENCE_PASSWORD: User's email address and password that used to log into Web of Science

* TITLE_WITH_DATE: For the cited article information collection only, the user can decides to include the retraction/correction date within the article title for search (set to 1 then) or not(set to 0 then)

* CONTINUE_WRITE: Do you want to overwrite the existing information or not, if set to be 0, the program will clean all the existing information within the generated file and replace with the new data.(Only available for citation list only mode or retraction list only mode)

If you have any problems please contact through email: [wscqkevin@gmail.com](mailto:wscqkevin@gmail.com) or open an issue.
