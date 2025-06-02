def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS forum (
            id SERIAL PRIMARY KEY,
            uporabnik_id INTEGER NOT NULL REFERENCES uporabniki(id),
            naslov VARCHAR(255) NOT NULL UNIQUE,
            vsebina TEXT NOT NULL,
            datum_objave TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS komentarji (
            id SERIAL PRIMARY KEY,
            forum_id INTEGER NOT NULL REFERENCES forum(id),
            uporabnik_id INTEGER NOT NULL REFERENCES uporabniki(id),
            vsebina TEXT NOT NULL,
            datum_objave TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("""
        INSERT INTO forum (uporabnik_id, naslov, vsebina)
        VALUES (1, 'Dobrodošli na forumu', 'To je vaš prvi forum. Uživajte v klepetu!'),
        (1, 'Pomoč pri uporabi', 'Če potrebujete pomoč pri uporabi foruma, tukaj vprašajte!'),
        (1, 'Splošna razprava', 'Tukaj lahko razpravljate o splošnih temah.'),
        (1, 'Nasveti in triki', 'Delite svoje nasvete in trike za boljšo izkušnjo na forumu!'),
        (1, 'Povratne informacije', 'Imate povratne informacije o forumu? Tukaj jih delite!'),
        (1, 'Napovedi', 'Sledite najnovejšim napovedim in posodobitvam foruma!'),
        (1, 'Dogodki', 'Obveščajte se o prihajajočih dogodkih in srečanjih na forumu!'),
        (1, 'Tehnična podpora', 'Imate tehnične težave? Tukaj poiščite pomoč!'),
        (1, 'Sodelovanje', 'Želite sodelovati pri razvoju foruma? Tukaj so možnosti!'),
        (1, 'Skupnost', 'Povežite se s člani skupnosti in delite svoje izkušnje!'),
        (1, 'Ustvarjalnost', 'Delite svoje ustvarjalne projekte in ideje z drugimi!'),
        (1, 'Zabava', 'Poiščite zabavne vsebine in igre na forumu!'),
        (1, 'Kultura', 'Razpravljajte o kulturi, umetnosti in literaturi!'),
        (1, 'Šport', 'Pogovarjajte se o športu in spremljajte najnovejše dogodke!'),
        (1, 'Zdravje in dobro počutje', 'Delite nasvete za zdravje in dobro počutje!'),
        (1, 'Potovanja', 'Izmenjujte potovalne izkušnje in priporočila!'),
        (1, 'Tehnologija', 'Razpravljajte o najnovejših tehnoloških trendih!'),
        (1, 'Izobraževanje', 'Delite izobraževalne vire in priložnosti!'),
        (1, 'Poslovanje', 'Pogovarjajte se o poslovnih strategijah in priložnostih!');
    """)
    cur.execute("""
        INSERT INTO komentarji (forum_id, uporabnik_id, vsebina)
        VALUES 
        (1, 1, 'Hvala za dobrodošlico!'),
        (2, 1, 'Kako naj začnem uporabljati forum?'),
        (3, 1, 'Kakšne teme so najbolj priljubljene?'),
        (4, 1, 'Kje lahko delim svoje nasvete?'),
        (5, 1, 'Kako lahko dam povratne informacije?'),
        (6, 1, 'Kje najdem najnovejše napovedi?'),
        (7, 1, 'Ali so načrtovani kakšni dogodki?'),
        (8, 1, 'Kako naj rešim tehnične težave?'),
        (9, 1, 'Kje lahko sodelujem pri razvoju foruma?'),
        (10, 1, 'Kako naj se povežem z drugimi člani skupnosti?');
    """)
    cur.commit()