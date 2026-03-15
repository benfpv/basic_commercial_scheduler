# database.py
import sqlite3
import os

# Hard-coded path — change this one line if you ever want a different filename
DB_PATH = "data_pilot/scheduler.db"


def get_db():
    """Returns a connection with FK enforcement on. Always use 'with'."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # lets you do row['name'] instead of row[0]
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """
    Create all tables (safe to call every time — uses IF NOT EXISTS).

    Schema overview
    ---------------
    users                   — person master record
    user_availabilities     — per-person available time windows
    commitments             — group-level committed slot (replaces global_commitments.csv)
    commitment_participants  — which users are in each commitment
                              (normalises the CSV "51&38&39" id field into proper rows)
    meetings                — actual meetings; FK back to the commitment they came from
                              (nullable so ad-hoc meetings without a prior commitment are allowed)
    meeting_participants    — who was *scheduled* for the meeting AND whether they *attended*
                              (attended = 0/1 — answers the "who actually showed up?" question)
    balance_history         — per-person financial trail, linked to a specific meeting
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db() as conn:
        conn.executescript('''
            PRAGMA foreign_keys = ON;

            -- ----------------------------------------------------------------
            -- Users
            -- ----------------------------------------------------------------
            CREATE TABLE IF NOT EXISTS users (
                id                INTEGER PRIMARY KEY,
                role              TEXT    NOT NULL,
                first_name        TEXT    NOT NULL,
                last_name         TEXT    NOT NULL,
                family_id         INTEGER,
                date_registered   TEXT    NOT NULL DEFAULT (date('now')),
                date_of_birth     TEXT    NOT NULL,
                address           TEXT,
                phone_number      TEXT,
                email             TEXT    UNIQUE,
                rate              REAL    NOT NULL DEFAULT 0.0,
                balance           REAL    NOT NULL DEFAULT 0.0,
                timezone          TEXT    NOT NULL,
                comments          TEXT
            );

            -- ----------------------------------------------------------------
            -- Availability  (per-person)
            -- ----------------------------------------------------------------
            CREATE TABLE IF NOT EXISTS user_availabilities (
                avail_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                start_utc   TEXT    NOT NULL,
                end_utc     TEXT    NOT NULL,
                CHECK (end_utc > start_utc)
            );

            -- ----------------------------------------------------------------
            -- Commitments  (group-level — a confirmed intersection)
            -- ----------------------------------------------------------------
            CREATE TABLE IF NOT EXISTS commitments (
                commitment_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                start_utc       TEXT NOT NULL,
                end_utc         TEXT NOT NULL,
                notes           TEXT,
                CHECK (end_utc > start_utc)
            );

            -- who is committed to each slot
            CREATE TABLE IF NOT EXISTS commitment_participants (
                commitment_id   INTEGER NOT NULL REFERENCES commitments(commitment_id) ON DELETE CASCADE,
                user_id         INTEGER NOT NULL REFERENCES users(id)                 ON DELETE CASCADE,
                PRIMARY KEY (commitment_id, user_id)
            );

            -- ----------------------------------------------------------------
            -- Meetings  (group-level — a commitment that happened, or ad-hoc)
            --
            -- commitment_id is NULLABLE:
            --   - set     → meeting was derived from a tracked commitment
            --   - NULL    → ad-hoc meeting (no prior commitment record)
            -- ----------------------------------------------------------------
            CREATE TABLE IF NOT EXISTS meetings (
                meeting_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                commitment_id   INTEGER REFERENCES commitments(commitment_id) ON DELETE SET NULL,
                start_utc       TEXT NOT NULL,
                end_utc         TEXT NOT NULL,
                title           TEXT,
                notes           TEXT,
                CHECK (end_utc > start_utc)
            );

            -- who was scheduled AND did they attend
            -- attended: 0 = no-show / unknown, 1 = attended
            CREATE TABLE IF NOT EXISTS meeting_participants (
                meeting_id  INTEGER NOT NULL REFERENCES meetings(meeting_id) ON DELETE CASCADE,
                user_id     INTEGER NOT NULL REFERENCES users(id)            ON DELETE CASCADE,
                attended    INTEGER NOT NULL DEFAULT 0 CHECK (attended IN (0, 1)),
                PRIMARY KEY (meeting_id, user_id)
            );

            -- ----------------------------------------------------------------
            -- Balance history  (per-person financial trail)
            -- ----------------------------------------------------------------
            CREATE TABLE IF NOT EXISTS balance_history (
                entry_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER NOT NULL REFERENCES users(id)       ON DELETE CASCADE,
                meeting_id      INTEGER          REFERENCES meetings(meeting_id) ON DELETE SET NULL,
                associate_ids   TEXT,
                start_utc       TEXT NOT NULL,
                end_utc         TEXT NOT NULL,
                amount          REAL NOT NULL,
                balance_after   REAL NOT NULL
            );
        ''')
    print(f"[OK] Database ready -> {DB_PATH}")


def execute(sql, params=()):
    """INSERT / UPDATE / DELETE"""
    with get_db() as conn:
        conn.execute(sql, params)
        conn.commit()


def insert(sql, params=()):
    """INSERT a single row; returns the new row's lastrowid."""
    with get_db() as conn:
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor.lastrowid


def fetch_all(sql, params=()):
    """SELECT many rows"""
    with get_db() as conn:
        return conn.execute(sql, params).fetchall()


def fetch_one(sql, params=()):
    """SELECT one row (or None)"""
    with get_db() as conn:
        return conn.execute(sql, params).fetchone()