def create_faq_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS faq (
            id SERIAL PRIMARY KEY,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            uporabnik_id INTEGER REFERENCES uporabniki(id) ON DELETE SET NULL
        );
    """)
