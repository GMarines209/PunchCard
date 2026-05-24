# PunchCard a ufc stats scraper and display

This project is a self-hoseted UFC stats display built on a Raspberry Pi Zero 2W and a 2.8" TFT screen. 
With python backend the project scrapes all historical fighter data and live event result,served via a REST api
onto a small color display.

> 🚧 **This is currently in active development** — backend pipeline complete, Pi client & live stats in progress

## Features

**Fighter stats mode** - This mode allows you to search any ufc fighter by name and have their information (portrait, record, and career stats)
displayed

**Live fight mode** - during active UFC events, the display updates round by round with live stats for both fighters pulled directly from UFC's CDN.

**Upcoming Card Mode** — when no fight is live, the display scrolls the upcoming event's full fight card.

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
                 ↓  SPI               ↓  polls every ~5s
        [ILI9341 2.8" TFT]     [Local Web UI]
          240x320 color               ↑
                           [Phone / Browser on LAN]
```

## User Flow

1. Open the web UI on any browser on your local network
2. Search a fighter by name — matching results appear with identifying info (nickname, record, weight class)
3. Select the correct fighter, their ID is set as active on the server
4. The Pi polls the server every ~5 seconds, detects the change, fetches full stats and displays them
5. Switch to Live mode during UFC events for round-by-round updates


## How it works

### Fighter stats pipeline
- A spider crawls on the ufcstats.com site and searchs alphabeticaly , cataloging each profile link and seeds a local SQLite database 
- On a name search, the backend queries SQLite with a fuzzy LIKE match and returns all candidates
- Fighter selection sets an active_fighter ID on the server — the Pi polls for changes
- A stats_map dictionary maps raw scraped labels to database column names
- A purify_stats() function handles all type conversion: height→inches, weight→lbs int, percentages→int, dates→ISO 8601, "--"→None

### Live stats pipeline
- Uses `ufc.com/events` to discover the current event dynamicly 
- Polls the UFC's cloudfront CDN for round by round results 
- Falls back to upcoming event card when no fight is active

### Caching / Updates
Two cases handled on every lookup:
- **Cold miss** — triggers find_by_name() — fetches the correct alphabetical page, matches by normalized name, scrapes and caches the fighter
- **Warm hit** — data is fresh → return from SQLite instantly
- A weekly cron job can be configured to run every Sunday morning (python main.py -u) to refresh stats for fighters who competed the previous Saturday night


### API Endpoints
| Method | Endpoint | Description |
| ------------- | ------------- |-------------|
| GET  | /  | Fighter search web UI |
| GET  | /fighters?name={name}  | Search fighters by name, returns a list|
| GET  | /set_active?id={fighterid} | Set the currently displayed fighter |
| GET  | /current  | Returns active fighter ID (Pi polls this) |
| GET  | /fighter?id={fighterid}  | Full stats for a specific fighter |
| GET  | /live  | Current live fight round stats |
| GET  | /upcoming  | Next event fight card |



## Setup 

### Prerequisites
* Python 3.10+
* Raspberry Pi Zero 2Ww