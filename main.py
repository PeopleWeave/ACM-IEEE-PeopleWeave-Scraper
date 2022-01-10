import concurrent.futures
from ACM_Scraper import ACM_Scraper
import json

with open("paper_information.json", "r") as f:
    paper_information = json.load(f)


def main(search):
    acm_scraper = ACM_Scraper(search, paper_information)
    print("Starting Login...")
    acm_scraper.login()
    print("Ending Login")
    acm_scraper.search_and_filter()
    print("Ending Filter")
    acm_scraper.download_papers()
    print("Ending Downloading")

searches = ["networking", "artificial intelligence"]
with concurrent.futures.ThreadPoolExecutor(max_workers=len(searches)) as executor:
    executor.map(main, searches)

with open("paper_information.json", "w") as f:
    json.dump(paper_information, f)