# PunchCard - a ufc stats scraper and display

This project is a self-hosted UFC stats display built on a Raspberry Pi Zero 2W and a 2.8" TFT screen.
The python backend scrapes all historical fighter data plus live event results, serves it through a REST API,
and renders it onto a small color display. You pick a fighter from a web page on your phone and it shows up on the screen.

> 🚧 **This is currently in active development** — backend pipeline is done, image download works, Pi client & live stats are in progress

> quick disclosure: the web dashboard (index.html) was AI generated, frontend isn't my focus and I just dont really enjoy it as much. The backend, scraping, database, and Pi client are my own work.

## Features

**Fighter stats mode** - search any UFC fighter by name and have their info (portrait, record, and career stats) shown on the display.

**Live fight mode** - during active UFC events the display updates round by round with live stats for both fighters, pulled straight from UFC's CDN.

**Upcoming card mode** - when nothing is live, the display falls back to the upcoming event's fight card.

## Demo

> Images and everything will come when i get the hardware going :grinning:

## Architecture

```
[ufc.com/events]         [ufcstats.com]        [UFC Cloudfront CDN]
      ↓ scrape                ↓ scrape               ↓ GET (no auth)
  event discovery         fighter stats         fight/live/{id}.json
      └─────────────────────────┬─────────────────────────┘
                                ↓
           [Python Backend — Docker on home server]
                                ↓
                         [SQLite Database]
                       (4000+ fighters cached)
                                ↓
                         [REST API (Flask)]
                                ↓
            [Raspberry Pi Zero 2W — WiFi client]
                 ↓  SPI               ↓  polls every ~5s
        [ILI9341 2.8" TFT]     [Local Web UI]
          240x320 color               ↑
                           [Phone / Browser on LAN]
```

## User Flow

1. Open the web UI on any browser on your local network
2. Search a fighter by name — matching results show up with identifying info (nickname, record, weight class)
3. Pick the right one, their ID gets set as active on the server
4. The Pi polls the server every ~5 seconds, notices the change, grabs the full stats and displays them
5. Switch to live mode during UFC events for round by round updates

## How it works

### Fighter stats pipeline
- A spider crawls ufcstats.com alphabetically, catalogs every profile link, and seeds a local SQLite database
- ufcstats.com sits behind Cloudflare, so the scraping runs through Playwright (a headless browser) to get past the challenge instead of plain requests
- On a name search the backend queries SQLite with a fuzzy LIKE match and returns all the candidates
- Picking a fighter sets an active_fighter ID on the server — the Pi polls for changes
- A stats_map dictionary maps the messy scraped labels to clean database column names
- A purify_stats() function handles all the type conversion: height→inches, weight→lbs int, percentages→int, dates→ISO 8601, "--"→None

### Fighter images
- Portraits aren't on ufcstats.com, so they get pulled from ufc.com/athlete pages instead
- Fighter names get turned into a URL slug (accents and punctuation stripped, spaces to hyphens) to find their athlete page
- The image URL carries a token so it can't be guessed — the page has to be loaded and the URL pulled out of it
- Images save as images/{fighterid}.png. Fighters with no ufc.com page just fall back to a default portrait

### Live stats pipeline
- Uses ufc.com/events to discover the current event dynamically
- Polls UFC's Cloudfront CDN for round by round results
- Falls back to the upcoming event card when no fight is active

### Caching / Updates
Two cases handled on every lookup:
- **Cold miss** — triggers find_by_name(), which fetches the correct alphabetical page, matches by normalized name, scrapes and caches the fighter
- **Warm hit** — data is already there → return from SQLite instantly
- A weekly cron job can be set up to run every Sunday morning (python main.py -u) to refresh stats for whoever fought the previous Saturday night

## Command Line Flags

The backend runs through main.py. On first run with an empty database it kicks off a full scrape automatically (this takes a few hours because it throttles requests on purpose). After that, these flags control the maintenance jobs:

| Flag | Long form | What it does |
| ---- | --------- | ------------ |
| `-u` | `--update` | Scrapes stats for every fighter on the most recent completed event. Meant for the weekly Sunday cron so records stay current after fight night. |
| `-i` | `--images` | Downloads fighter portraits from ufc.com for everyone in the database. Skips anyone already downloaded, so it's safe to rerun and safe to cancel partway through. |

Running with no flags just initializes the database and starts the Flask server. Flags can be combined (e.g. `python main.py -u -i`), and any run starts the server afterward.

## API Endpoints
| Method | Endpoint | Description |
| ------------- | ------------- |-------------|
| GET  | /  | Fighter search web UI |
| GET  | /fighters?name={name}  | Search fighters by name, returns a list |
| GET  | /current  | Returns active fighter ID (Pi polls this) |
| GET  | /fighter?id={fighterid}  | Full stats for a specific fighter, and sets the currently displayed fighter |
| GET  | /live  | Current live fight round stats |
| GET  | /upcoming  | Next event fight card |

## Setup

### Prerequisites
```
pip install -r requirements.txt
playwright install chromium
```

Note: `playwright install chromium` is not optional. Installing the playwright package alone doesn't grab the browser it needs, and the scraper will fail without it.

## Future updates / features
* Once im done with everything to do with the pi and display, I plan to train a ML model on all these stats and see if i can get 
some predictions going  

