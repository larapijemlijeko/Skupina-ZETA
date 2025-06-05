def create_table(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS scraped (
    id SERIAL PRIMARY KEY,
    uporabnik_id INTEGER NOT NULL,
    naslov TEXT NOT NULL,
    url TEXT NOT NULL,
    datum_shranjevanja TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (uporabnik_id, url)
    );
    """)