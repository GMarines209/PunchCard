from bs4 import BeautifulSoup
import string
from playwright.sync_api import sync_playwright
import utils
import nest_asyncio

nest_asyncio.apply()


def alpha_crawl():
    alpha = string.ascii_lowercase
    with sync_playwright() as p:
        # launch chromium
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("DEBUG: Browser launched. Waiting for Cloudflare...")
        fighter_links = []
        for char in alpha:
            page.goto(f"http://ufcstats.com/statistics/fighters?char={char}&page=all")
            try:
                page.wait_for_selector(".b-statistics__table-row td:nth-child(1) a", timeout=15000)
            except Exception as e:
                print(f"DEBUG: Timeout waiting for Cloudflare to pass. {e}")
                continue
            
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            urls = soup.select(".b-statistics__table-row td:nth-child(1) a")
            fighter_links += [link['href'] for link in urls]

        browser.close()

    for link in fighter_links:
        yield link

def event_scan():

    with sync_playwright() as p:
        # launch chromium
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("DEBUG: Browser launched. Waiting for Cloudflare...")
        page.goto("http://ufcstats.com/statistics/events/completed")
        
        try:
            page.wait_for_selector(".b-statistics__table-row", timeout=15000)
        except Exception as e:
            print(f"DEBUG: Timeout waiting for Cloudflare to pass. {e}")
            browser.close()
            return

        # Extract loaded HTML from the browser
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')

        title = soup.title.text.strip() if soup.title else "No Title Found"
        print(f"DEBUG: The page title is: {title}")

        # get the latest completed event url
        event_tags = soup.select("a[href*='event-details']")
        
        if len(event_tags) > 1:
            event_tag = event_tags[1]['href']
        else:
            print("DEBUG: Failed to find event link.")
            browser.close()
            return

        print(f"DEBUG: Successfully found event link: {event_tag}")

        # Navigate to the specific event page
        page.goto(event_tag)
        
        try:
            page.wait_for_selector("a[href*='fighter-details']", timeout=15000)
        except Exception as e:
            print("DEBUG: Timeout waiting for fighters to load.")
            browser.close()
            return

        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')

        urls = soup.select("a[href*='fighter-details']")        
        fighter_links = [link['href'] for link in urls]
        
        browser.close()

    for link in fighter_links:
        yield link

def find_by_name(name):
    # EDGE CASE: if a figher only has a first or last name 

    # ufc site sorts by last name so this gets first letter of last name
    name_arr = name.split(' ')
    first_letter = name_arr[-1][0]
    match = None
    with sync_playwright() as p:
            # launch chromium
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
    
            print("DEBUG: Browser launched. Waiting for Cloudflare...")            

            page.goto(f"http://ufcstats.com/statistics/fighters?char={first_letter}&page=all")
            try:
                page.wait_for_selector(".b-statistics__table-row td:nth-child(1) a", timeout=15000)
            except Exception as e:
                print(f"DEBUG: Timeout waiting for Cloudflare to pass. {e}")

            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')

            first_name_url = soup.select(".b-statistics__table-row td:nth-child(1) a")
            last_name_url = soup.select(".b-statistics__table-row td:nth-child(2) a")

            for first,last in zip(first_name_url,last_name_url):
                    loop_name = (first.text.strip() + ' ' + last.text.strip())
                    if(utils.normalize_text(name) == utils.normalize_text(loop_name)):
                        match =  first['href']
                        break
            browser.close()
    return match


