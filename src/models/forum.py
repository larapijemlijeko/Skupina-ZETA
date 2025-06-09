def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS forum (
            id SERIAL PRIMARY KEY,
            uporabnik_id INTEGER NOT NULL REFERENCES uporabniki(id),
            naslov VARCHAR(255) NOT NULL UNIQUE,
            vsebina TEXT NOT NULL,
            datum_objave TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS komentarji_forum (
            id SERIAL PRIMARY KEY,
            forum_id INTEGER NOT NULL REFERENCES forum(id),
            uporabnik_id INTEGER NOT NULL REFERENCES uporabniki(id),
            vsebina TEXT NOT NULL,
            datum_objave TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)