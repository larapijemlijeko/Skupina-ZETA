def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS recept_slike (
            id SERIAL PRIMARY KEY,
            recept_id INTEGER REFERENCES recepti(id),
            slika_pot TEXT
        );
    """)