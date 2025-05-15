def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS oznake (
            id SERIAL PRIMARY KEY,
            recept_id INTEGER NOT NULL REFERENCES recepti(id) ON DELETE CASCADE,
            oznaka VARCHAR(30) NOT NULL
        );
    """)
