import database
import scraper
import requests
from bs4 import BeautifulSoup



def get_stats(fighter_name):

    fighter_name = normalize_text(fighter_name)
    conn = database.get_connection()
    c = conn.cursor()
    

    c.execute("""SELECT * FROM fighters 
              INNER JOIN fighter_stats ON fighters.fighterid = fighter_stats.trackfighter
              WHERE LOWER(fighters.name) = ? """,(fighter_name,))
    stats= c.fetchone()

    # (cold miss) if this figher isnt in the database at all search for them by name
    # then call scraper and add them to the db
    if(stats == None):
        url = find_by_name(fighter_name)
        if(url == None):
            return None
        stats = scraper.get_fighter_stats(url)
        database.save_complete_fighter(stats)


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

def normalize_text(name):
    name = name.lower().strip()
    name_arr = name.split(' ')
    name = " ".join(name_arr)

    return name
 