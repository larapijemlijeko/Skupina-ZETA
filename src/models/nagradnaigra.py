def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS nagradna_igra (
            id SERIAL PRIMARY KEY,
            uporabnik_id INTEGER REFERENCES uporabniki(id) ON DELETE CASCADE,
            cas_prijave TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)