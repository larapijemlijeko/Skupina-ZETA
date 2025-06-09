def create_table(cur):
    cur.execute("""
        CREATE TABLE cooking_tips (
        id SERIAL PRIMARY KEY,
        tip TEXT NOT NULL
      );
                      
      INSERT INTO cooking_tips (tip) VALUES
      ('Vedno segrej ponev pred dodajanjem olja, da se hrana ne prime.'),
      ('Soli vodo za kuhanje testenin – naj bo kot morska voda.'),
      ('Uporabljaj ostro rezilo – bolj varno in natančno kot topo.'),
      ('Pusti meso počivati po pečenju za bolj sočen rezultat.'),
      ('Limona ali kis lahko osvežita skoraj vsako jed.'),
      ('Pri peki vedno predhodno segrej pečico.'),
      ('Shrani vodo od testenin – vsebuje škrob in zgošči omake.'),
      ('Ne preobremenjuj ponve – sestavine se bodo kuhale, ne pekle.'),
      ('Okušaj hrano med kuhanjem, ne šele na koncu.'),
      ('Dodaj ščepec soli tudi v sladice – poudari okus.');


      """)