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

    cur.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='recepti' AND column_name='drzava'
            ) THEN
                ALTER TABLE recepti ADD COLUMN drzava VARCHAR(100);
            END IF;
        END$$;
    """)
