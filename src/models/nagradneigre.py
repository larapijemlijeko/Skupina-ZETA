def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS nagradne_prijave (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            prijavljen_ob TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
