def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vsecki (
            id SERIAL PRIMARY KEY,
            uporabnik_id INTEGER NOT NULL REFERENCES uporabniki(id) ON DELETE CASCADE,
            recept_id INTEGER NOT NULL REFERENCES recepti(id) ON DELETE CASCADE,
            datum_vsecka TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (uporabnik_id, recept_id)
        );
    """)
