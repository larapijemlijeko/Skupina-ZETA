def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS napake (
            id SERIAL PRIMARY KEY,
            tip_problema VARCHAR(50) NOT NULL,
            opis VARCHAR(255) NOT NULL,
            datum_kreiranja TIMESTAMP DEFAULT  CURRENT_TIMESTAMP               
        );
    """) 