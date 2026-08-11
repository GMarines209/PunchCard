from bs4 import BeautifulSoup
import datetime
from playwright.sync_api import sync_playwright
import nest_asyncio
import database

# stops playwright from fighting with Flask for the event loop
nest_asyncio.apply()

stats_map = {
    "Height:": "height",
    "Weight:": "weight",
    "Reach:": "reach",
    "STANCE:": "stance",
    "DOB:": "dob",
    "SLpM:": "SLpM",
    "Str. Acc.:": "StrAcc", 
    "SApM:": "SApM",
    "Str. Def:": "StrDef",
    "TD Avg.:" : "TdAvg",
    "TD Acc.:" : "TdAcc",
    "TD Def.:" : "TdDef",
    "Sub. Avg.:" : "SubAvg"   
}

def safe_extract(soup, css_selector):
    # tries to extract text, used to fix 'has no attribute 'text' errors . Returns 'N/A' if the HTML tag doesn't exist
    # replaces that manual stripping i was doing per stat
    element = soup.select_one(css_selector)
    if element:
        return element.text.strip()
    return "N/A"

def scrape_all(links):
    count = 1
    stats = []


    with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            # loop from main ===================
            for link in links:
                page.goto(link)
                try:
                    # Wait for the fighter name to pass cloudflare 
                    page.wait_for_selector(".b-content__title-highlight", timeout=15000)
                except Exception:
                    print(f"DEBUG: Timeout/Blocked on {link}")
                    continue 
                
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')

                print(f"[{count}] Fetching: {link}")
                count += 1
                try:
                    clean_stats = get_fighter_stats(link,soup)  
                    fighter_name = clean_stats.get("name", "Unknown Fighter")
                    print(f"    -> Saving {fighter_name} to database...")
                    stats.append(clean_stats)
                except Exception as e:
                    # error handeling stuff
                    print(f"    -> [!] FAILED to scrape {link}. Error: {e}")
                    continue # skips the rest of this loop and moves to the next URL

                

            browser.close()
            return stats

def get_fighter_stats(url,soup):
    clean_stats = {}
    messy_stats = {}

    url_array = url.split("/")
    fighter_id = url_array[-1]
    clean_stats["fighterid"] = fighter_id

    # fighter name
    name = safe_extract(soup, ".b-content__title-highlight")
    if name == "N/A":
        return None # Abort if page loaded but name is missing for some reason
    clean_stats["name"] = name
    
    # fighter record
    record_text = safe_extract(soup, ".b-content__title-record").replace("Record: ", "").strip()
    if record_text != "N/A" and record_text:
        record_arr = record_text.split('(')
        
        try:
            wins, losses, draws = record_arr[0].strip().split('-')
            clean_stats["wins"] = int(wins)
            clean_stats["losses"] = int(losses)
            clean_stats["draws"] = int(draws)
        except Exception:
            clean_stats["wins"], clean_stats["losses"], clean_stats["draws"] = 0, 0, 0 # default to a 0,0,0 record if theres a sort of error

        if len(record_arr) == 2:
            nocontest_str = record_arr[1].replace(" NC)", "")
            clean_stats["nocontest"] = int(nocontest_str)
        else:
            clean_stats["nocontest"] = 0
    else:
         clean_stats["wins"], clean_stats["losses"], clean_stats["draws"], clean_stats["nocontest"] = 0, 0, 0, 0

    # fighter nickname
    clean_stats["nickname"] = safe_extract(soup, ".b-content__Nickname")

    # gets all the stats by looping through the lists and adding them to a dict
    for ul in soup.findAll("ul","b-list__box-list"):
        for li in ul.findAll("li"):
            i_tag = li.find('i')
            if i_tag: # Safety check inside the loop
                tag = i_tag.text.strip()
                value = li.get_text().replace(tag,'').strip()
                messy_stats.update({tag:value})

    # fix up the key names and save to clean_stats
    for messy_key, messy_value in messy_stats.items():
        if messy_key in stats_map:
            clean_stats[stats_map[messy_key]] = messy_value

    # latest fight
    clean_stats["lastfight"] = safe_extract(soup, ".b-fight-details__table-row td:nth-of-type(7) p:nth-of-type(2)")

    clean_stats = purify_stats(clean_stats)
    return clean_stats

def purify_stats(clean_stats):

    for key in clean_stats:
        if clean_stats[key] == "--" or clean_stats[key] == "N/A" or clean_stats[key] == "":
            clean_stats[key] = None

    # removes % signs
    for val in clean_stats:
        if isinstance(clean_stats[val], str) and "%" in clean_stats[val]:
            x = clean_stats[val].replace("%","")
            try:
                clean_stats[val] = int(x)
            except Exception:
                clean_stats[val] = None

    # remove lbs from weight and cast
    if clean_stats.get("weight") is not None:
        weight_val = str(clean_stats["weight"])
        try:
            clean_stats["weight"] = int(weight_val.replace("lbs.", "").strip())
        except Exception:
            clean_stats["weight"] = None

    # store height as inches
    if clean_stats.get("height") is not None:
        try:
            height = clean_stats["height"].split()
            feet = int(height[0].replace("'", ""))
            inches = int(height[1].replace('"', ""))
            clean_stats["height"] = (feet * 12) + inches
        except Exception:
            clean_stats["height"] = None

    #remove " from reach
    if clean_stats.get("reach") is not None:
        reach = str(clean_stats["reach"])
        try:
            clean_stats["reach"] = int(reach.replace('"', "").strip())
        except Exception:
            clean_stats["reach"] = None

    # convert dob to ISO 8601
    if clean_stats.get("dob") is not None:
        date = clean_stats["dob"]
        date_format = "%b %d, %Y"
        try:
            iso_date = datetime.datetime.strptime(date, date_format)
            clean_stats["dob"] = iso_date.strftime("%Y-%m-%d")
        except Exception:
            clean_stats["dob"] = None

    if clean_stats.get("lastfight") is not None:
        date = clean_stats["lastfight"]
        date_format = "%b. %d, %Y"
        try:
            iso_date = datetime.datetime.strptime(date, date_format)
            clean_stats["lastfight"] = iso_date.strftime("%Y-%m-%d")
        except Exception:
            clean_stats["lastfight"] = None

    return clean_stats