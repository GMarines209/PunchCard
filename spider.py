import random
from bs4 import BeautifulSoup
import requests
import string
import time


def alpha_crawl():
    alpha = string.ascii_lowercase
    for char in alpha:
        r = requests.get(f"http://ufcstats.com/statistics/fighters?char={char}&page=all")
        soup = BeautifulSoup(r.content, 'html.parser')

        urls = soup.select(".b-statistics__table-row td:nth-child(1) a")
        for link in urls:
            yield link['href']
            time.sleep(random.uniform(1.5, 3.5))

