import scraper
import database

url = 'http://ufcstats.com/fighter-details/0d8011111be000b2'
scraper.get_fighter_stats(url)