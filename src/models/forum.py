def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS forum (
            id SERIAL PRIMARY KEY,
            uporabnik_id INTEGER REFERENCES uporabniki(id),
            naslov VARCHAR(255) NOT NULL UNIQUE,
            vsebina TEXT NOT NULL,
            datum_objave TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS komentarji_forum (
            id SERIAL PRIMARY KEY,
            forum_id INTEGER NOT NULL REFERENCES forum(id),
            uporabnik_id INTEGER NOT NULL REFERENCES uporabniki(id),
            vsebina TEXT NOT NULL,
            datum_objave TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("""
        INSERT INTO forum (uporabnik_id, naslov, vsebina)
        VALUES (NULL, 'Dobrodošli na forumu', 'To je vaš prvi forum. Uživajte v klepetu!'),
        (NULL, 'Pomoč pri uporabi', 'Če potrebujete pomoč pri uporabi foruma, tukaj vprašajte!'),
        (NULL, 'Splošna razprava', 'Tukaj lahko razpravljate o splošnih temah.'),
        (NULL, 'Nasveti in triki', 'Delite svoje nasvete in trike za boljšo izkušnjo na forumu!'),
        (NULL, 'Povratne informacije', 'Imate povratne informacije o forumu? Tukaj jih delite!'),
        (NULL, 'Napovedi', 'Sledite najnovejšim napovedim in posodobitvam foruma!'),
        (NULL, 'Dogodki', 'Obveščajte se o prihajajočih dogodkih in srečanjih na forumu!'),
        (NULL, 'Tehnična podpora', 'Imate tehnične težave? Tukaj poiščite pomoč!'),
        (NULL, 'Sodelovanje', 'Želite sodelovati pri razvoju foruma? Tukaj so možnosti!'),
        (NULL, 'Skupnost', 'Povežite se s člani skupnosti in delite svoje izkušnje!'),
        (NULL, 'Ustvarjalnost', 'Delite svoje ustvarjalne projekte in ideje z drugimi!'),
        (NULL, 'Zabava', 'Poiščite zabavne vsebine in igre na forumu!'),
        (NULL, 'Kultura', 'Razpravljajte o kulturi, umetnosti in literaturi!'),
        (NULL, 'Šport', 'Pogovarjajte se o športu in spremljajte najnovejše dogodke!'),
        (NULL, 'Zdravje in dobro počutje', 'Delite nasvete za zdravje in dobro počutje!'),
        (NULL, 'Potovanja', 'Izmenjujte potovalne izkušnje in priporočila!'),
        (NULL, 'Tehnologija', 'Razpravljajte o najnovejših tehnoloških trendih!'),
        (NULL, 'Izobraževanje', 'Delite izobraževalne vire in priložnosti!'),
        (NULL, 'Poslovanje', 'Pogovarjajte se o poslovnih strategijah in priložnostih!');
    """)