from playwright.sync_api import sync_playwright
import datetime, glob, os 
import cache

def render_and_save(fighter_id,stat_page, out_path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 240, "height": 320}, device_scale_factor=1)
        page.goto(f"http://localhost:5000/render?id={fighter_id}&type={stat_page}&view=pi")
        page.wait_for_selector(".screen")
        page.locator(".screen").screenshot(path=out_path)
        browser.close()

def stale_check(fighter_id):
    stats = cache.get_stats(fighter_id)
    if not stats or not stats.get("lastChecked"):
        return 1
    fighter_date = datetime.datetime.fromisoformat(stats["lastChecked"])

    for stat_page in ["physical", "striking", "grappling"]:

        file_String = glob.glob(f"renders/{fighter_id}_{stat_page}_*.png")
        if not file_String:
            return 1
        if file_String:
            newest = max(file_String)
            date_string = newest.rsplit("_", 1)[1].removesuffix(".png")
            file_date = datetime.datetime.fromisoformat(date_string)
            if file_date < fighter_date:
                return 1 # if the rendering is older than the last checked, regen them

    return 0

def del_stale(fighter_id):

    for stat_page in ["physical", "striking", "grappling"]:
        file_String = glob.glob(f"renders/{fighter_id}_{stat_page}_*.png")
        for path in file_String:
            os.remove(path)

def main(fighter_id):
    time = datetime.datetime.today().strftime("%Y%m%dT%H%M%S")
    if (stale_check(fighter_id) == 1):
        del_stale(fighter_id) # delete old renders
        for stat_page in ["physical", "striking", "grappling"]:
            render_and_save(fighter_id,stat_page, f"renders/{fighter_id}_{stat_page}_{time}.png") # save the new ones
        print(f"Saved 3 renders for {fighter_id}")