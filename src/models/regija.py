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

def inicializiraj_regije_in_povezave():
    from . import db  # če db ni še uvožen
    conn = db.get_connection()
    cur = conn.cursor()
    
    # Dodaj regije
    regije = ["Europe", "North America", "Asia", "Africa", "South America"]
    for regija in regije:
        cur.execute("INSERT INTO regije (ime) VALUES (%s) ON CONFLICT (ime) DO NOTHING", (regija,))
    
    # Poveži prvi recept z Evropo (primer)
    cur.execute("SELECT id FROM regije WHERE ime = %s", ("Europe",))
    regija_id = cur.fetchone()[0]
    cur.execute("INSERT INTO recepti_regije (recept_id, regija_id) VALUES (%s, %s)", (1, regija_id))

    conn.commit()
    conn.close()