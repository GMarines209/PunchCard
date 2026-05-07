import random
from bs4 import BeautifulSoup
import requests
import string
import time


def alpha_crawl():
    alpha = string.ascii_lowercase
    for char in alpha:
        r = requests.get(f"http://ufcstats.com/statistics/fighters?char={char}&page=all",timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser')

        urls = soup.select(".b-statistics__table-row td:nth-child(1) a")
        for link in urls:
            yield link['href']
            time.sleep(random.uniform(1.5, 3.5))


def event_scan():
    r = requests.get("http://ufcstats.com/statistics/events/completed", timeout=10)
    soup = BeautifulSoup(r.content, 'html.parser')

    # gets the latest completed event url to keep up to date on the fighters stats
    event_tag = soup.select_one(".b-statistics__table-row:nth-child(3) a")
    event_tag = event_tag['href']

    r = requests.get(event_tag, timeout=10)
    soup = BeautifulSoup(r.content, 'html.parser')

    urls = soup.select("a[href*='fighter-details']")
    for link in urls:
        yield link['href']
