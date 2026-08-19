from bs4 import BeautifulSoup
import requests, json


def get_upcomming():
    r = requests.get('https://www.ufc.com/events')
    soup = BeautifulSoup(r.content, 'html.parser')

    events = soup.select_one("a.e-button--white[href*='/event/']")
    event_link = events["href"]

    if not events:
        return None

    if event_link:
        r = requests.get(event_link)
        soup = BeautifulSoup(r.content, 'html.parser')
        blob = soup.find('script', attrs={'data-drupal-selector': 'drupal-settings-json'})

        if not blob:
            return None
        data = json.loads(blob.string)
        event_fmid = data["eventLiveStats"]["event_fmid"]
        if not event_fmid:
            return None

        return event_fmid

def live():
    event_id = get_upcomming()
    fight_link = f"https://d29dxerjsp82wz.cloudfront.net/api/v3/event/live/{event_id}.json"
    r = requests.get(fight_link)
    page = r.json()

    detail = page['LiveEventDetail']

    live_page = {
        "event" : detail['EventId'],
        "name" : detail['Name'],
        "location": f"{detail['Location']['City']}, {detail['Location']['State']}",
        "status": detail['Status'],
        "live": True if detail.get("LiveFightId") is not None else False,
        "fights": build_fights(detail.get("FightCard", []))
    }

    return live_page

def build_fights(fight_card):

    # Nested funcs to make getting the names and functions cleaner 
    def fighter_name(f):
        name = f.get("Name",{})
        return f"{name.get('FirstName','')} {name.get('LastName','')}".strip() or "TBD"

    def fighter_record(f):
        r = f.get("Record",{})
        record = f"{r.get('Wins',0)}-{r.get('Losses',0)}-{r.get('Draws',0)}"
        if r.get('NoContests'):
            record += f" ({r['NoContests']} NC)"
        return record


    fights = []
    for fight in fight_card:
        fighters = fight.get("Fighters",[])
        a = fighters[0] if len(fighters) > 0 else {}
        b = fighters[1] if len(fighters) > 1 else {}
        wc = fight.get("WeightClass", {})
        fights.append({
            "fighter_a": {"name": fighter_name(a), "record": fighter_record(a)},
            "fighter_b": {"name": fighter_name(b), "record": fighter_record(b)},
            "weightclass": wc.get("Description"),
            "status": "live" if fight.get("Status") == "Live" else ""
        })
    return fights