from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import ili9341
from PIL import Image
import requests, time, io

serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25)
device = ili9341(serial, rotate=1)
server = "http://127.0.0.1:5000"

poll_time = 5
stat_time = 30

fighter = 0;page_index = 0;last_render = 0

pages = ["physical", "striking", "grappling"]

def main():

    global fighter
    global page_index
    global last_render

    while True:
        current = check_cur()
        if current is None:
            time.sleep(poll_time)
            continue

        # if the current fighter is the same upon recheck
        if current == fighter:
            # if its time for a render change 
            if (time.time() - last_render >= stat_time):
                cycle_page()
                last_render = time.time()
            time.sleep(poll_time)
        # if the fighter is now different     
        else :
            page_index = 0
            fighter = current
            last_render = time.time()
            time.sleep(poll_time)
        

def check_cur():
    r = requests.get(f"{server}/current")
    id = r.json()["active_fighter_id"]

    return id

def cycle_page():
    global page_index

    try:
        r = requests.get(f"{server}/serve?id={fighter}&page={pages[page_index]}")
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content)).convert("RGB")
        device.display(img)
    except ConnectionError as e:
        time.sleep(stat_time)        
    

    if page_index >= 2:
       page_index = 0
    else: page_index += 1


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass