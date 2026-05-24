import database
import scraper
import requests
from bs4 import BeautifulSoup



def get_stats(fighter_id):
    stats = database.get_fighter_by_id(fighter_id)
    return stats

def find_by_name(name):
    # EDGE CASE: if a figher only has a first or last name 

    # ufc site sorts by last name so this gets first letter of last name
    name_arr = name.split(' ')
    first_letter = name_arr[-1][0]
    

    r = requests.get(f"http://ufcstats.com/statistics/fighters?char={first_letter}&page=all")
    soup = BeautifulSoup(r.content, 'html.parser')

    first_name_url = soup.select(".b-statistics__table-row td:nth-child(1) a")
    last_name_url = soup.select(".b-statistics__table-row td:nth-child(2) a")

    for first,last in zip(first_name_url,last_name_url):
        loop_name = (first.text.strip() + ' ' + last.text.strip())
        if(normalize_text(name) == normalize_text(loop_name)):
            return first['href']

    return None

def handle_search(fighter_name):

    names = database.search_fighters(fighter_name)

    # (cold miss) if this figher isnt in the database at all search for them by name
    # then call scraper and add them to the db
    if(names == []):
        url = find_by_name(fighter_name)
        if(url == None):
            return []
        stats = scraper.get_fighter_stats(url)
        database.save_complete_fighter(stats)
        names = database.search_fighters(fighter_name)

    return names

def normalize_text(name):
    name = name.lower().strip()
    name_arr = name.split(' ')
    name = " ".join(name_arr)

    return name
 