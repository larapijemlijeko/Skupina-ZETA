def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS recepti (
            id SERIAL PRIMARY KEY,
            naslov VARCHAR(100) NOT NULL,
            opis TEXT,
            priprava TEXT NOT NULL,
            cas_priprave INTEGER,
            tezavnost INT,
            slika_url VARCHAR(255),
            uporabnik_id INTEGER REFERENCES uporabniki(id),
            datum_kreiranja TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
