def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS navedki (
            id SERIAL PRIMARY KEY,
            navedek VARCHAR(255) NOT NULL,
            avtor VARCHAR(255),
            datum_kreiranja TIMESTAMP DEFAULT CURRENT_TIMESTAMP                 
        );
    """)