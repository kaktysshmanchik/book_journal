# db_setup.py
import sqlite3

def execmany(cur, sql, rows):
    cur.executemany(sql, [(r,) if not isinstance(r, tuple) else r for r in rows])

def main():
    conn = sqlite3.connect("journal.db")
    cur = conn.cursor()

    # Be strict, be proud
    cur.execute("PRAGMA foreign_keys = ON;")

    # -----------------------------
    # Lookup / reference tables
    # -----------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS author (
        id INTEGER PRIMARY KEY,
        author_name TEXT NOT NULL UNIQUE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS size (
        id INTEGER PRIMARY KEY,
        size_name TEXT NOT NULL UNIQUE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS category (
        id INTEGER PRIMARY KEY,
        category_name TEXT NOT NULL UNIQUE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS genre (
        id INTEGER PRIMARY KEY,
        category_id INTEGER NOT NULL,
        genre_name TEXT NOT NULL,
        UNIQUE(category_id, genre_name),
        FOREIGN KEY(category_id) REFERENCES category(id) ON DELETE RESTRICT ON UPDATE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS subgenre (
        id INTEGER PRIMARY KEY,
        genre_id INTEGER NOT NULL,
        subgenre_name TEXT NOT NULL,
        UNIQUE(genre_id, subgenre_name),
        FOREIGN KEY(genre_id) REFERENCES genre(id) ON DELETE RESTRICT ON UPDATE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS source (
        id INTEGER PRIMARY KEY,
        source TEXT NOT NULL UNIQUE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS discovery (
        id INTEGER PRIMARY KEY,
        discovery_name TEXT NOT NULL UNIQUE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS icon (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        path TEXT NOT NULL,
        builtin INTEGER NOT NULL DEFAULT 0  -- 0/1 boolean
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS vibe (
        id INTEGER PRIMARY KEY,
        vibe_name TEXT NOT NULL UNIQUE,
        prefilled INTEGER NOT NULL DEFAULT 1  -- 0/1
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS months_later (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reread (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings_options (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        parameter_id INTEGER PRIMARY KEY,   -- one row per option
        value INTEGER NOT NULL DEFAULT 1,   -- 0/1
        FOREIGN KEY(parameter_id) REFERENCES settings_options(id) ON DELETE CASCADE ON UPDATE CASCADE
    );
    """)

    # Many-to-many: books ↔ vibes (since you defined a vibe dictionary but no single FK on books)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS book_vibes (
        book_id INTEGER NOT NULL,
        vibe_id INTEGER NOT NULL,
        PRIMARY KEY (book_id, vibe_id),
        FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY(vibe_id) REFERENCES vibe(id) ON DELETE RESTRICT ON UPDATE CASCADE
    );
    """)

    # -----------------------------
    # Books (main table)
    # -----------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY,
        dnf INTEGER NOT NULL DEFAULT 0,                 -- boolean 0/1
        name TEXT NOT NULL,
        author INTEGER,                                 -- FK author.id
        size INTEGER,                                   -- FK size.id
        category INTEGER,                               -- FK category.id
        genre INTEGER,                                  -- FK genre.id
        subgenre INTEGER,                               -- FK subgenre.id
        source INTEGER,                                 -- FK source.id
        discovery INTEGER,                              -- FK discovery.id
        discovery_text TEXT,
        icon INTEGER,                                   -- FK icon.id
        expectations TEXT,
        expectations_failed TEXT,
        date_start DATE,
        date_finish DATE,
        rating INTEGER,
        crush_list TEXT,
        months_later INTEGER,                           -- FK months_later.id
        reread INTEGER,                                 -- FK reread.id
        line TEXT,
        reminded TEXT,
        phys_copy INTEGER NOT NULL DEFAULT 0,           -- boolean 0/1
        notes TEXT,
        remember_check_due_at DATE,                     -- computed by trigger when date_finish set
        FOREIGN KEY(author) REFERENCES author(id) ON DELETE SET NULL ON UPDATE CASCADE,
        FOREIGN KEY(size) REFERENCES size(id) ON DELETE SET NULL ON UPDATE CASCADE,
        FOREIGN KEY(category) REFERENCES category(id) ON DELETE SET NULL ON UPDATE CASCADE,
        FOREIGN KEY(genre) REFERENCES genre(id) ON DELETE SET NULL ON UPDATE CASCADE,
        FOREIGN KEY(subgenre) REFERENCES subgenre(id) ON DELETE SET NULL ON UPDATE CASCADE,
        FOREIGN KEY(source) REFERENCES source(id) ON DELETE SET NULL ON UPDATE CASCADE,
        FOREIGN KEY(discovery) REFERENCES discovery(id) ON DELETE SET NULL ON UPDATE CASCADE,
        FOREIGN KEY(icon) REFERENCES icon(id) ON DELETE SET NULL ON UPDATE CASCADE,
        FOREIGN KEY(months_later) REFERENCES months_later(id) ON DELETE SET NULL ON UPDATE CASCADE,
        FOREIGN KEY(reread) REFERENCES reread(id) ON DELETE SET NULL ON UPDATE CASCADE
    );
    """)

    # Indexes that actually help
    cur.execute("CREATE INDEX IF NOT EXISTS idx_books_name ON books(name);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_books_dates ON books(date_start, date_finish);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_books_genres ON books(category, genre, subgenre);")

    # -----------------------------
    # Triggers: remember_check_due_at = date_finish + 90 days
    # -----------------------------
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS trg_books_set_remember_after_insert
    AFTER INSERT ON books
    WHEN NEW.date_finish IS NOT NULL
    BEGIN
      UPDATE books
      SET remember_check_due_at = date(NEW.date_finish, '+90 day')
      WHERE id = NEW.id;
    END;
    """)
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS trg_books_set_remember_after_update
    AFTER UPDATE OF date_finish ON books
    WHEN NEW.date_finish IS NOT NULL
    BEGIN
      UPDATE books
      SET remember_check_due_at = date(NEW.date_finish, '+90 day')
      WHERE id = NEW.id;
    END;
    """)

    # -----------------------------
    # Prefill data
    # -----------------------------
    # size
    sizes = [
        'Short story — 4-30 pages',
        'Novelette — 30-80 pages',
        'Novella — 80-200 pages',
        'Novel — 200-450 pages',
        'Epic — 450+ pages'
    ]
    execmany(cur, "INSERT OR IGNORE INTO size(size_name) VALUES (?);", sizes)

    # category
    categories = ['Fiction', 'Non-fiction']
    execmany(cur, "INSERT OR IGNORE INTO category(category_name) VALUES (?);", categories)

    # source
    sources = ['E-book', 'Audiobook', 'Physical (mine)', 'Physical (borrowed)']
    execmany(cur, "INSERT OR IGNORE INTO source(source) VALUES (?);", sources)

    # discovery
    discoveries = ['Friend', 'Social media', 'Review', 'Store', 'Library', 'Other']
    execmany(cur, "INSERT OR IGNORE INTO discovery(discovery_name) VALUES (?);", discoveries)

    # months_later
    months_later_vals = ['Hell yes', 'Vaguely', 'Who???']
    execmany(cur, "INSERT OR IGNORE INTO months_later(name) VALUES (?);", months_later_vals)

    # reread
    reread_vals = ['Absolutely', 'Maybe in crisis', 'Nah']
    execmany(cur, "INSERT OR IGNORE INTO reread(name) VALUES (?);", reread_vals)

    # vibe
    vibes = [
        'Dark','Gritty','Light','Epic','Intimate','Creepy','Playful','Witty',
        'Passionate','Tragic','Melancholy','Hopeful','Optimistic','Cynical',
        'Satirical','Tense','Fast-paced','Slow-burn','Chaotic','Wild','Cozy'
    ]
    execmany(cur, "INSERT OR IGNORE INTO vibe(vibe_name) VALUES (?);", vibes)

    # settings_options (field toggles for Add book)
    settings_names = [
        'Icon','DNF','Author','Size','Category','Genre','Subgenre','Source',
        'Where did I hear about it','My expectations','Date started','Date finished',
        'Rating','How different it is from my expectations','Vibe','Character crush list',
        'Do I remember it three months later?','Would I reread it?','That line that got me',
        'What it reminded me of','Do I need a physical copy?','Notes','Rating_scale'
    ]
    execmany(cur, "INSERT OR IGNORE INTO settings_options(name) VALUES (?);", settings_names)
    # default all settings ON (1)
    cur.execute("INSERT OR IGNORE INTO settings(parameter_id, value) SELECT id, 1 FROM settings_options;")

    # -----------------------------
    # Genres and Subgenres (prefilled)
    # -----------------------------
    # helper: get id by name
    def get_id(table, col, val):
        cur.execute(f"SELECT id FROM {table} WHERE {col} = ?;", (val,))
        row = cur.fetchone()
        return row[0] if row else None

    fiction_id = get_id("category", "category_name", "Fiction")
    nonfiction_id = get_id("category", "category_name", "Non-fiction")

    # Genres by category
    fiction_genres = [
        'literary','fantasy','science fiction','romance','mystery','crime','thriller',
        'horror','historical','adventure','young adult'
    ]
    nonfiction_genres = [
        'Biography','Memoir','History','Self-help','Personal development','Science','Popular science',
        'Philosophy','Religion','Politics','Business','Economics','Travel writing','Essays','True crime','Guides'
    ]

    for g in fiction_genres:
        cur.execute("INSERT OR IGNORE INTO genre(category_id, genre_name) VALUES (?, ?);", (fiction_id, g))
    for g in nonfiction_genres:
        cur.execute("INSERT OR IGNORE INTO genre(category_id, genre_name) VALUES (?, ?);", (nonfiction_id, g))

    # Map: genre name -> list of subgenres
    subgenres_map = {
        ('Fiction','literary'): [
            'Psychological fiction','Social commentary','Experimental/Avant-garde','Philosophical fiction',
            'Stream of consciousness','Bildungsroman (coming-of-age)','Metafiction'
        ],
        ('Fiction','fantasy'): [
            'High/Epic fantasy','Low fantasy','Urban fantasy','Dark fantasy','Sword & sorcery',
            'Fairy tale retelling','Grimdark','Historical fantasy','Mythic fantasy','Portal fantasy'
        ],
        ('Fiction','science fiction'): [
            'Hard sci-fi','Soft sci-fi','Space opera','Cyberpunk','Biopunk','Dystopian','Utopian',
            'Time travel','Alternate history','Post-apocalyptic'
        ],
        ('Fiction','romance'): [
            'Contemporary romance','Historical romance','Regency romance','Paranormal romance',
            'Fantasy romance','Romantic suspense','Erotica','Comedy romance (romcom)',
            'Inspirational romance','Gothic romance'
        ],
        ('Fiction','mystery'): [
            'Cozy mystery','Whodunit','Police procedural','Amateur sleuth','Locked-room mystery',
            'Historical mystery','Noir mystery','Paranormal mystery'
        ],
        ('Fiction','crime'): [
            'Detective fiction','Noir / Hardboiled','Legal thriller','Mafia / Organized crime',
            'Heist / Caper','Psychological crime','Domestic crime'
        ],
        ('Fiction','thriller'): [
            'Psychological thriller','Political thriller','Spy/Espionage','Techno-thriller',
            'Legal thriller','Conspiracy thriller','Medical thriller','Action thriller','Eco-thriller'
        ],
        ('Fiction','horror'): [
            'Gothic horror','Supernatural horror','Psychological horror','Body horror','Splatterpunk',
            'Cosmic horror','Folk horror','Survival horror'
        ],
        ('Fiction','historical'): [
            'Historical romance','Historical adventure','Historical mystery','Historical fantasy',
            'Alternate history','War fiction','Biographical historical novels','Family sagas'
        ],
        ('Fiction','adventure'): [
            'Survival adventure','Swashbuckler','Quest adventure','Lost world adventure',
            'Military adventure','Sea adventure','Pulp adventure','Exploration'
        ],
        ('Fiction','young adult'): [
            'Contemporary YA','Fantasy YA','Sci-Fi YA','Dystopian YA','Romance YA',
            'Paranormal YA','Mystery/Thriller YA','Coming-of-age YA'
        ],
        # Non-fiction usually doesn’t have “subgenre” in the same way; we leave empty by default.
    }

    # Insert subgenres
    for (cat_name, gname), subs in subgenres_map.items():
        cat_id = fiction_id if cat_name == 'Fiction' else nonfiction_id
        # canonical genre key: for fiction we stored lowercase names
        lookup_gname = gname
        if cat_name == 'Fiction':
            lookup_gname = gname.lower()
        cur.execute("SELECT id FROM genre WHERE category_id=? AND genre_name=?;", (cat_id, lookup_gname))
        row = cur.fetchone()
        if row:
            gid = row[0]
            for s in subs:
                cur.execute("INSERT OR IGNORE INTO subgenre(genre_id, subgenre_name) VALUES (?, ?);", (gid, s))

    # Commit all that beauty
    conn.commit()

    # Smoke test insert (optional; comment out if you’re picky)
    cur.execute("INSERT OR IGNORE INTO author(author_name) VALUES (?)", ("J.R.R. Tolkien",))
    cur.execute("SELECT id FROM author WHERE author_name = ?", ("J.R.R. Tolkien",))
    tolkien = cur.fetchone()[0]
    cur.execute("SELECT id FROM size WHERE size_name=?", ("Novel — 200-450 pages",))
    size_id = cur.fetchone()[0]
    cur.execute("SELECT id FROM category WHERE category_name=?", ("Fiction",))
    cat_id = cur.fetchone()[0]
    cur.execute("SELECT id FROM genre WHERE category_id=? AND genre_name=?", (cat_id, 'fantasy'))
    genre_id = cur.fetchone()[0]
    cur.execute("SELECT id FROM subgenre WHERE genre_id=? AND subgenre_name=?", (genre_id, 'High/Epic fantasy'))
    subgenre_id = cur.fetchone()[0]
    cur.execute("SELECT id FROM source WHERE source=?", ("Physical (mine)",))
    source_id = cur.fetchone()[0]
    cur.execute("SELECT id FROM discovery WHERE discovery_name=?", ("Friend",))
    disc_id = cur.fetchone()[0]
    cur.execute("SELECT id FROM months_later WHERE name=?", ("Hell yes",))
    ml_id = cur.fetchone()[0]
    cur.execute("SELECT id FROM reread WHERE name=?", ("Absolutely",))
    rr_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO books (dnf, name, author, size, category, genre, subgenre, source, discovery,
                           date_start, date_finish, rating, months_later, reread, phys_copy)
        VALUES (0, ?, ?, ?, ?, ?, ?, ?, ?, date('2025-01-01'), date('2025-02-01'), 10, ?, ?, 1)
    """, ("The Lord of the Rings", tolkien, size_id, cat_id, genre_id, subgenre_id, source_id, disc_id, ml_id, rr_id))
    conn.commit()

    print("journal.db created and prefilled. Go raise some hell.")

if __name__ == "__main__":
    main()
