from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv
import time

class ACM_Scraper:
    # this variable will store the numbers of the pages that were visited so that the scraper know when to stop
    page_numbers_visited = []

    # gets a connection to the environment variables and sets up the webdriver
    def __init__(self, search):
        # setup the env variables
        load_dotenv()
        CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH')
        self.USERNAME = os.getenv('LOGIN_USERNAME')
        self.PASSWORD = os.getenv('LOGIN_PASSWORD')
        self.URL = os.getenv('ACM_URL')

        self.search_query = search

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

        # filter for only research articles
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
        # print('1')
        # self.load_checker()
        # print('2')
        # a_tags = self.driver.find_elements(By.TAG_NAME,"a")
        # print(len(a_tags))
        # print('3')
        # links = []
        # for a in a_tags:
        #     print(a.get_attribute("href"))
        # print('4')
        print('1')
        self.load_checker()
        print("2")
        h5 = self.driver.find_elements(By.CLASS_NAME, "issue-item__title")
        print('3')
        print("H5:" + str(len(h5)))
        spans = []
        for h in h5:
            spans.append(h.find_elements(By.XPATH, ".//*"))
        print('4')
        print("SPANS: " + str(len(spans)))
        a = []
        for s in spans:
            a.append(s.find_elements(By.XPATH, ".//*"))
        print(len(a))
    
        
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
        load_checker = WebDriverWait(self.driver,30).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="pb-page-content"]/div/main/div[1]/div/div[2]/div/ul/li[21]/div[2]/div[1]'))
        )