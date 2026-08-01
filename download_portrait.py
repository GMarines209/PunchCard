import requests, unicodedata
from random import uniform
from time import sleep
from bs4 import BeautifulSoup

def strip_name(name):
    # strip special chars from name string
    stripped_name = unicodedata.normalize('NFKD', name)
    stripped_name = stripped_name.encode('ascii', 'ignore')
    stripped_name = stripped_name.decode('ascii')

    # remove spaces / apostraohe's and combine with - to make slug
    stripped_name = stripped_name.replace(' ','-')
    stripped_name = stripped_name.replace("'", "").replace(".", "")
    stripped_name = stripped_name.lower()

    return stripped_name


def image_download(name,fighterid):
    try:
        r = requests.get(f"https://www.ufc.com/athlete/{name}")
    except Exception as e:
        print(e)
        return 
    
    soup = BeautifulSoup(r.content, 'html.parser')
    image = soup.select_one('.hero-profile__image')

    if image is None:
        return 0
    image_url = image['src']

    try:
        r = requests.get(image_url)
    except Exception as e:
        print(e)
        return 

    with open(f"images/{fighterid}.png", 'wb') as f:
        f.write(r.content)

    sleep(uniform(1, 3))
    return 1
