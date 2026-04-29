import sqlite3 
import datetime

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
            height INTEGER,
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
            lastfight TEXT,
            SLpM REAL,
            StrAcc INTEGER,
            SApM REAL,
            StrDef INTEGER,
            TdAvg REAL,
            TdAcc INTEGER,
            TdDef INTEGER,
            SubAvg REAL,
            trackfighter TEXT,
            FOREIGN KEY(trackfighter) REFERENCES fighters(fighterid)
            )""")

    conn.commit()

    conn.close()

def save_complete_fighter(stats):
    conn = get_connection()
    c = conn.cursor()
    insert_fighter(stats,c)
    insert_stats(stats,c)

    conn.commit()
    conn.close()

def insert_fighter(stats,c):
     c.execute("INSERT OR IGNORE INTO fighters VALUES (:fighterid, :name, :dob, :nickname, :height, :weight, :reach, :stance)", stats)


def insert_stats(stats,c):
    stats["lastChecked"] = datetime.datetime.today().isoformat()
    c.execute("""
        INSERT OR REPLACE INTO fighter_stats (
            wins, losses, draws, nocontest, lastChecked, lastfight, 
            SLpM, StrAcc, SApM, StrDef, TdAvg, TdAcc, TdDef, SubAvg, trackfighter
        ) VALUES (
            :wins, :losses, :draws, :nocontest, :lastChecked, :lastfight, 
            :SLpM, :StrAcc, :SApM, :StrDef, :TdAvg, :TdAcc, :TdDef, :SubAvg, :fighterid
        )
    """, stats)