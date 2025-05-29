def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sestavine (
            id SERIAL PRIMARY KEY,
            recept_id INTEGER NOT NULL REFERENCES recepti(id) ON DELETE CASCADE,
            ime VARCHAR(50) NOT NULL,
            kolicina VARCHAR(50),
            enota VARCHAR(20),
            st_oseb INT
        );
    """)
