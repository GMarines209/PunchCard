import scraper
import database
import spider

def main():
    print("Initializing database...")
    database.init_db()
    conn = database.get_connection()
    c = conn.cursor()

    # if the db is empty start up a full scrape
    # this takes like 3 or so hours so have fun!
    c.execute("SELECT COUNT(*) FROM fighters")
    if c.fetchone()[0] == 0:
        full_scrape()
    

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
            # The Danger Zone (Things that rely on the internet)
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