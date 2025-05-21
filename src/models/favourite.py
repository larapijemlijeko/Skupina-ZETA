def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS favourite (
            id SERIAL PRIMARY KEY,
            uporabnik_id INTEGER NOT NULL REFERENCES uporabniki(id) ON DELETE CASCADE,
            recept_id INTEGER NOT NULL REFERENCES recepti(id) ON DELETE CASCADE,
            datum_shranjevanja TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (uporabnik_id, recept_id)
        );
    """)

