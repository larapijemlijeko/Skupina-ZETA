def create_user_data_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS uporabniki_podatki (
            id SERIAL PRIMARY KEY,
            visina INTEGER CHECK (visina > 0),
            teza NUMERIC(5,2) CHECK (teza > 0),
            starost INTEGER CHECK (starost >= 0),
            spol VARCHAR(10) CHECK (spol IN ('moski', 'zenska')),
            aktivnost VARCHAR(20) CHECK (aktivnost IN ('malo', 'lahka', 'zmerna', 'visoka','zelo_visoka')),    
            kalorije_za_vzdrzevanje INTEGER,
            kalorije_za_hujsanje INTEGER,
            datum TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)    

