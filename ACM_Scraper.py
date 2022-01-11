from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv
import json

class ACM_Scraper:
    # this variable will store the numbers of the pages that were visited so that the scraper know when to stop
    page_numbers_visited = []
    paper_information_dictionary = []
    # gets a connection to the environment variables and sets up the webdriver
    def __init__(self, search, paper_information):
        # setup the env variables
        load_dotenv()
        CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH')
        self.USERNAME = os.getenv('LOGIN_USERNAME')
        self.PASSWORD = os.getenv('LOGIN_PASSWORD')
        self.URL = os.getenv('ACM_URL')

        self.search_query = search

        # load the json file
        # with open("paper_information.json", "r") as f:
        #     self.paper_information_dictionary = json.load(f)
        self.paper_information_dictionary = paper_information
        #setup the driver
        download_dir = "Papers" # for linux/*nix, download_dir="/usr/Public"
        options = webdriver.ChromeOptions()
        profile = {
            "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
            "download.default_directory": download_dir , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        }
        options.add_experimental_option("prefs", profile)
        self.driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)
    # logs in to the website
    def login(self):
        self.driver.get(self.URL)

        # Login
        username = WebDriverWait(self.driver,30).until(
            EC.presence_of_element_located((By.ID, "j_username"))
        )

        password = WebDriverWait(self.driver,30).until(
            EC.presence_of_element_located((By.ID, "j_password"))
        )

        username.send_keys(self.USERNAME)
        password.send_keys(self.PASSWORD)

        submit = WebDriverWait(self.driver,30).until(
            EC.presence_of_element_located((By.NAME, "_eventId_proceed"))
        )

        submit.click()
    # inputs the search query and the filter on research articles
    def search_and_filter(self):
        # type in the search field and go
        search_field = WebDriverWait(self.driver,30).until(
            EC.presence_of_element_located((By.ID, "text1"))
        )

        search_field.send_keys(self.search_query)

        submit = WebDriverWait(self.driver,30).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="frmSearch"]/div[5]/div/div[2]/button'))
        )
        submit.click()

        # # filter for only research articles
        # content_type = WebDriverWait(self.driver,30).until(
        #     EC.presence_of_element_located((By.XPATH, '//*[@id="filter"]/div/div/div[2]/div[2]/div[1]/div[4]/a'))
        # )
        # content_type.click()

        # research_article = WebDriverWait(self.driver,30).until(
        #     EC.presence_of_element_located((By.XPATH, '//*[@id="ContentType"]/ul/li[1]/a'))
        # )
        # research_article.click()
    # goes through the pages and downloads all of the papers
    def download_papers(self):
        page_count = 1
        first_arrow = WebDriverWait(self.driver,60).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="pb-page-content"]/div/main/div[1]/div/div[2]/div/nav/span/a'))
        )
        link = first_arrow.get_attribute("href")
        link = link[0:link.index("startPage=") + 10]
   
        while True:
            self.download_single_page()
            self.driver.get(link + str(page_count))
            page_count += 1

            if page_count > 100:
                break


    def download_single_page(self):
        # checks that the page has loaded
        self.load_checker()
        # identifies each card
        lists = self.driver.find_elements(By.TAG_NAME, "ul")
        card_list = None
        for list in lists:
            if list.get_attribute("class") == "search-result__xsl-body  items-results rlist--inline ":
                card_list = list
        cards = card_list.find_elements(By.XPATH, "./*")
        
        for c in cards:
            if c.get_attribute("class") != "search__item issue-item-container":
                cards.remove(c)
        
        # loop through each card and gather data
        for card in cards:
            try:
                doi_div = card.find_element(By.CLASS_NAME, 'issue-item__detail')
                doi_link = doi_div.find_elements(By.TAG_NAME, "a")[1].get_attribute("href")
                doi = doi_link[doi_link.index("illinois.edu/") + 13:]
            except:
                continue

            paper_exists = False
            for item in self.paper_information_dictionary:
                if item["doi"] == doi:
                    paper_exists = True
                    
            if not paper_exists:
                title = ""
                try:
                    # gets the title
                    h5 = card.find_element(By.CLASS_NAME, 'issue-item__title')
                    title = h5.find_elements(By.TAG_NAME, "a")[0].get_attribute("text")
                except: pass
                # gets the authors
                try:
                    show_authors_button = card.find_element(By.CLASS_NAME, "count-list").find_element(By.TAG_NAME, "a")
                    show_authors_button.click()
                except:
                    pass

                authors = []
                try:
                    author_list = card.find_element(By.CLASS_NAME, "issue-item__content-right").find_element(By.TAG_NAME, "ul").find_elements(By.TAG_NAME, "li")
                    
                    
                    for a in author_list:
                        a_tag = a.find_element(By.TAG_NAME, "a")
                        if a_tag.get_attribute("class") != "read-less":
                            authors.append(a_tag.get_attribute("title"))
                except: pass

                # get the date
                date = ""

                try:
                    date_div = card.find_element(By.CLASS_NAME, 'issue-item__detail')
                    date = date_div.find_element(By.CLASS_NAME, "dot-separator").find_elements(By.TAG_NAME, "span")[0].text
                    date = date[:date.index(",")]
                except: pass

                # get the journal
                journal = ""
                try:
                    journal_div = card.find_element(By.CLASS_NAME, 'issue-item__detail')
                    journal = journal_div.find_elements(By.TAG_NAME, "a")[0].get_attribute("title")
                except: pass
                    

                paper_info =  {"doi" : doi, "title" : title, "date" : date, "authors" : authors, "journal" : journal}

                
                self.paper_information_dictionary.append(paper_info)

                # get the download button
                try:
                    a_tags = card.find_elements(By.TAG_NAME, "a")
                    for a in a_tags:
                        if a.get_attribute("class") == "btn--icon simple-tooltip__block--b red btn":
                            pass
                            # a.click()
                except: pass
           
        # self.save_paper_dictionary()
    # this function determines if the paper already has been downloaded and if not then gathers information and downloads the paper
    def download_single_paper(self, link):
        print(link)
    # scrapes and stores all of the data about a paper
    def gather_information(self):
        pass
    # this clicks the right arrow button at the bottom of the page
    def click_next_arrow(self):
        right_arrow = WebDriverWait(self.driver,30).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="pb-page-content"]/div/main/div[1]/div/div[2]/div/nav/span/a'))
        )
        right_arrow.click()
    # checks if the page has loaded for the papers page
    def load_checker(self):
        load_checker = WebDriverWait(self.driver,60).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="pb-page-content"]/div/main/div[1]/div/div[2]/div/div[1]/div[1]/span[2]/span[4]'))
        )

    def save_paper_dictionary(self):
        with open("paper_information.json", "a") as f:
            json.dump(self.paper_information_dictionary, f)