import scraper, spider, database



def get_stats(fighter_id):
    stats = database.get_fighter_by_id(fighter_id)
    return stats

def handle_search(fighter_name):

    names = database.search_fighters(fighter_name)

    # (cold miss) if this figher isnt in the database at all search for them by name
    # then call scraper and add them to the db
    if(names == []):
        url = spider.find_by_name(fighter_name)
        if(url == None):
            return []
        stats = scraper.scrape_all([url]) # update the parameters 
        database.save_complete_fighter(stats[0])
        names = database.search_fighters(fighter_name)

    return names