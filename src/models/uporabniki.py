def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS uporabniki (
            id SERIAL PRIMARY KEY,
            uporabnisko_ime VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            geslo VARCHAR(255) NOT NULL,
            datum_registracije TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
