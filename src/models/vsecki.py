def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vsecki (
            id SERIAL PRIMARY KEY,
            recept_id INTEGER NOT NULL REFERENCES recepti(id) ON DELETE CASCADE,
            like BOOLEAN NOT NULL,  -- True = like, False = dislike
        );
    """)
