import scraper
import database
import spider
import argparse
import api

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-u","--update",help="run fighter scraping for the most recent fight",action='store_true')
    args = parser.parse_args()

    print("Initializing database...")
    database.init_db()
    conn = database.get_connection()
    c = conn.cursor()

    # if the db is empty start up a full scrape
    c.execute("SELECT COUNT(*) FROM fighters")
    if c.fetchone()[0] == 0:
        print("database is empty... starting complete fighter catalog\n")
        print("this may take 2-4 hours. Have fun!")
        full_scrape()

    # if -u flag in called scrape recent fight stats
    if(args.update):
        for link in spider.event_scan():
            try:
                clean_stats = scraper.get_fighter_stats(link)
                
                fighter_name = clean_stats.get("name", "Unknown Fighter")
                print(f"    -> Updating stats for {fighter_name}")
                
                database.save_complete_fighter(clean_stats)
            except Exception as e:
                # error handeling stuff
                print(f"    -> [!] FAILED to scrape {link}. Error: {e}")
                continue # skips the rest of this loop and moves to the next URL
    conn.close()
    


def full_scrape():
    print("Initializing database...")
    database.init_db()
    print("Starting crawl...\n")

    count = 1
    for link in spider.alpha_crawl():
        print(f"[{count}] Fetching: {link}")
        count += 1
        try:
            clean_stats = scraper.get_fighter_stats(link)
            
            fighter_name = clean_stats.get("name", "Unknown Fighter")
            print(f"    -> Saving {fighter_name} to database...")
            
            database.save_complete_fighter(clean_stats)
            
        except Exception as e:
            # error handeling stuff
            print(f"    -> [!] FAILED to scrape {link}. Error: {e}")
            continue # skips the rest of this loop and moves to the next URL

if __name__ == "__main__":
    main()


api.app.run()
