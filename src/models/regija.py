def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS regije (
            id SERIAL PRIMARY KEY,
            ime VARCHAR(100) UNIQUE NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS recepti_regije (
            id SERIAL PRIMARY KEY,
            recept_id INTEGER REFERENCES recepti(id) ON DELETE CASCADE,
            regija_id INTEGER REFERENCES regije(id) ON DELETE CASCADE
        );
    """)

    regije = ["Europe", "North America", "North Asia", "South Asia", "Africa and the Middle East", "South America",]
    for regija in regije:
        cur.execute("""
            INSERT INTO regije (ime) VALUES (%s)
            ON CONFLICT (ime) DO NOTHING
        """, (regija,))
        print("Vstavil regijo:", regija)

    print("Tabele regije in privzete regije so pripravljene.")

