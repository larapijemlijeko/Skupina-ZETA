def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admin_questions (
            id SERIAL PRIMARY KEY,
            question TEXT NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            email VARCHAR(255) NOT NULL
        );
    """)
