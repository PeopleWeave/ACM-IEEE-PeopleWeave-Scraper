import concurrent.futures
from ACM_Scraper import ACM_Scraper

def main(search):
    acm_scraper = ACM_Scraper(search)
    print("Starting Login...")
    acm_scraper.login()
    print("Ending Login")
    acm_scraper.search_and_filter()
    print("Ending Filter")
    acm_scraper.download_papers()
    print("Ending Downloading")

searches = ["networking"]
with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
    executor.submit(main, "networking")
