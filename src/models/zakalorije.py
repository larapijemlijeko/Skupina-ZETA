def create_user_data_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS uporabniki_podatki (
            uporabnik_id INTEGER PRIMARY KEY REFERENCES uporabniki(id) ON DELETE CASCADE,
            visina INTEGER CHECK (visina > 0),
            teza NUMERIC(5,2) CHECK (teza > 0),
            starost INTEGER CHECK (starost >= 0)
        );
    """)
