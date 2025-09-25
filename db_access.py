# db_access.py
import sqlite3
from typing import List, Tuple, Optional

DB_PATH = "journal.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def fetch_all(sql: str, params: tuple = ()) -> List[sqlite3.Row]:
    with get_conn() as c:
        cur = c.execute(sql, params)
        return cur.fetchall()

def upsert_author(name: str) -> int:
    if not name:
        return None
    with get_conn() as c:
        cur = c.execute("SELECT id FROM author WHERE author_name = ?", (name.strip(),))
        row = cur.fetchone()
        if row:
            return row["id"]
        cur = c.execute("INSERT INTO author(author_name) VALUES (?)", (name.strip(),))
        return cur.lastrowid

def list_sizes() -> List[Tuple[int,str]]:
    rows = fetch_all("SELECT id, size_name FROM size ORDER BY id")
    return [(r["id"], r["size_name"]) for r in rows]

def list_categories() -> List[Tuple[int,str]]:
    rows = fetch_all("SELECT id, category_name FROM category ORDER BY id")
    return [(r["id"], r["category_name"]) for r in rows]

def list_genres_by_category(cat_id: int) -> List[Tuple[int,str]]:
    rows = fetch_all("SELECT id, genre_name FROM genre WHERE category_id = ? ORDER BY genre_name", (cat_id,))
    return [(r["id"], r["genre_name"]) for r in rows]

def list_subgenres_by_genre(genre_id: int) -> List[Tuple[int,str]]:
    rows = fetch_all("SELECT id, subgenre_name FROM subgenre WHERE genre_id = ? ORDER BY subgenre_name", (genre_id,))
    return [(r["id"], r["subgenre_name"]) for r in rows]

def list_sources() -> List[Tuple[int,str]]:
    rows = fetch_all("SELECT id, source FROM source ORDER BY id")
    return [(r["id"], r["source"]) for r in rows]

def list_discoveries() -> List[Tuple[int,str]]:
    rows = fetch_all("SELECT id, discovery_name FROM discovery ORDER BY id")
    return [(r["id"], r["discovery_name"]) for r in rows]

def list_months_later() -> List[Tuple[int,str]]:
    rows = fetch_all("SELECT id, name FROM months_later ORDER BY id")
    return [(r["id"], r["name"]) for r in rows]

def list_reread() -> List[Tuple[int,str]]:
    rows = fetch_all("SELECT id, name FROM reread ORDER BY id")
    return [(r["id"], r["name"]) for r in rows]

def insert_book(data: dict) -> int:
    sql = """
    INSERT INTO books (
        dnf, name, author, size, category, genre, subgenre, source, discovery, discovery_text,
        date_start, date_finish, rating, months_later, reread, phys_copy, notes, expectations,
        expectations_failed, crush_list, line, reminded
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """
    vals = (
        data.get("dnf", 0),
        data["name"],
        data.get("author"),
        data.get("size"),
        data.get("category"),
        data.get("genre"),
        data.get("subgenre"),
        data.get("source"),
        data.get("discovery"),
        data.get("discovery_text"),
        data.get("date_start"),
        data.get("date_finish"),
        data.get("rating"),
        data.get("months_later"),
        data.get("reread"),
        data.get("phys_copy", 0),
        data.get("notes"),
        data.get("expectations"),
        data.get("expectations_failed"),
        data.get("crush_list"),
        data.get("line"),
        data.get("reminded"),
    )
    with get_conn() as c:
        cur = c.execute(sql, vals)
        return cur.lastrowid
