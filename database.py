import sqlite3 

DB_FILENAME = 'fighters.db'

def get_connection():
    conn = sqlite3.connect(DB_FILENAME)
    return conn


def init_db():

    conn = get_connection()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS fighters (
            
            fighterid TEXT PRIMARY KEY,
            name TEXT,
            dob  TEXT,
            nickname TEXT,
            height REAL,
            weight INTEGER,
            reach INTEGER,
            stance TEXT
            )""")

    conn.commit()

    c.execute("""CREATE TABLE IF NOT EXISTS fighter_stats (
            
            statsid INTEGER PRIMARY KEY,
            wins INTEGER,
            losses INTEGER,
            draws INTEGER,
            nocontest INTEGER,
            lastChecked TEXT,
            SLpM REAL,
            StrAcc INTEGER,
            SApM REAL,
            StrDef INTEGER,
            TdAvg REAL,
            TdAcc INTEGER,
            TdDef INTEGER,
            SubAvg REAL,
            trackfighter INTEGER,
            FOREIGN KEY(trackfighter) REFERENCES fighters(fighterid)
            )""")

    conn.commit()

