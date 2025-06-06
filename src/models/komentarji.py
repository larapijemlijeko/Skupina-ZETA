def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS komentarji (
            id SERIAL PRIMARY KEY,
            recept_id INTEGER NOT NULL REFERENCES recepti(id) ON DELETE CASCADE,
            komentar TEXT NOT NULL,
            avtor VARCHAR(100),
            datum TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
