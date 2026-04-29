from bs4 import BeautifulSoup
import requests
import datetime


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


def get_fighter_stats(url):

    messy_stats = {}
    clean_stats = {}

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    # fighter id
    url_array = url.split("/")
    fighter_id = url_array[-1]
    clean_stats["fighterid"] = fighter_id

    # fighter name
    name = soup.select_one(".b-content__title-highlight").text.strip()
    clean_stats["name"] = name
    
    # fighter record
    record = soup.select_one(".b-content__title-record")
    record_text = record.text.replace("Record: ", "").strip()

    record_arr = record_text.split('(')

    wins, losses, draws = record_arr[0].strip().split('-')
    clean_stats["wins"] = int(wins)
    clean_stats["losses"] = int(losses)
    clean_stats["draws"] = int(draws)

    if len(record_arr) == 2:
        nocontest_str = record_arr[1].replace(" NC)", "")
        clean_stats["nocontest"] = int(nocontest_str)
    else:
        clean_stats["nocontest"] = 0


    # fighter nickname
    nickname = soup.select_one(".b-content__Nickname").text.strip()
    clean_stats["nickname"] = nickname

    # gets all the stats by looping through the lists and adding them to a dict
    for ul in soup.findAll("ul","b-list__box-list"):
        for li in ul.findAll("li"):
            tag = li.find('i').text.strip()
            value = li.get_text().replace(tag,'').strip()
            messy_stats.update({tag:value})

    # fix up the key names and save to clean_stats
    for messy_key, messy_value in messy_stats.items():
        if messy_key in stats_map:
            clean_stats[stats_map[messy_key]] = messy_value

    clean_stats = purify_stats(clean_stats)

    
    print(clean_stats)


        

def purify_stats(clean_stats):

    # removes % signs
    for val in clean_stats:
        if isinstance(clean_stats[val], str) and "%" in clean_stats[val]:
            x = clean_stats[val].replace("%","")
            clean_stats[val] = int(x)

    # remove lbs from weight
    weight_val = clean_stats["weight"]
    clean_stats["weight"] = weight_val.replace("lbs.","")

    # store height as inches
    height = clean_stats["height"].split()
    feet = int(height[0].replace("'",""))
    inches = int(height[1].replace('"', ""))
    clean_stats["height"] = ((feet * 12) + (inches))

    #remove " from reach
    reach = clean_stats["reach"]
    clean_stats["reach"] = reach .replace('"', "")

    # convert date to ISO 8601
    date = clean_stats["dob"]
    date_format = "%b %d, %Y"
    iso_date = datetime.datetime.strptime(date,date_format)
    clean_stats["dob"] = iso_date.strftime("%Y-%m-%d")

    return clean_stats
