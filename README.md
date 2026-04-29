# PunchCard a ufc stats scraper and display

This project is a self-hoseted UFC stats display built on a Raspberry Pi Zero 2W and a 2.8" TFT screen. 
With python backend the project scrapes all historical fighter data and live event result,served via a REST api
onto a small color display.

> 🚧 **This is currently in active development** — backend pipeline complete, Pi client & live stats in progress

## Features

**Fighter stats mode** - This mode allows you to search any ufc fighter by name and have their information (portrait, record, and career stats)
displayed

**Live fight mode** - during active UFC events, the display updates round by round with live stats for both fighters pulled directly from UFC's CDN.

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
                       (4065+ fighters cached)
                                ↓
                         [REST API (Flask)]
                                ↓
            [Raspberry Pi Zero 2W — WiFi client]
                 ↓  SPI               ↓  serves
        [ILI9341 2.8" TFT]     [Local Web UI]
          240x320 color               ↑
                           [Phone / Browser on LAN]
```


## How it works

### Fighter stats pipeline
- A spider crawls on the ufcstats.com site and searchs alphabeticaly , cataloging each profile link and seeds a local SQLite database 
- For a individual figher lookup, a cache is called to check for the freshness of the data (is this fighters last fight after when they were last scraped)
it then rescrapes the data it deems to be out of date.
- Fighter portraits are fetched from the UFC website and downscaled server side before being served to the pi

### Live stats pipeline
- Uses `ufc.com/events` to discover the current event dynamicly 
- Polls the UFC's cloudfront CDN for round by round results 

### Caching
Three cases handled on every lookup:
- **Cold miss** — fighter not in database → targeted scrape of their letter page → insert → return
- **Warm hit** — data is fresh → return from SQLite instantly
- **Stale hit** — fighter has fought since last check → re-scrape profile → update database → return


## Setup 

TBD