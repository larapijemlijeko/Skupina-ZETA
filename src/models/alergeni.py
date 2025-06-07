def create_table(cur):
    # Tabela za alergene
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alergeni (
            id SERIAL PRIMARY KEY,
            ime VARCHAR(100) NOT NULL UNIQUE
        );
    """)
    # Povezovalna tabela med sestavinami in alergeni
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sestavine_alergeni (
            id SERIAL PRIMARY KEY,
            sestavina_id INTEGER REFERENCES sestavine(id) ON DELETE CASCADE,
            alergen_id INTEGER REFERENCES alergeni(id) ON DELETE CASCADE
        );
    """)

  # Vstavi osnovne alergene (če še niso tam)
    osnovni_alergeni = [
        'Gluten', 'Jajca', 'Mleko', 'Oreščki', 'Arašidi', 'Soja',
        'Ribe', 'Mehkužci', 'Gorčica', 'Sezam', 'Žveplov dioksid',
        'Volčji bob', 'Listna zelena'
    ]
    for alergen in osnovni_alergeni:
        cur.execute("""
            INSERT INTO alergeni (ime) VALUES (%s)
            ON CONFLICT (ime) DO NOTHING;
        """, (alergen,))