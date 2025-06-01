import db

quotes = [
    {"navedek": "One cannot think well, love well, sleep well, if one has not dined well.", "avtor": "Virginia Woolf"},
    {"navedek": "Let food be thy medicine and medicine be thy food.", "avtor": "Hippocrates"},
    {"navedek": "People who love to eat are always the best people.", "avtor": "Julia Child"},
    {"navedek": "The only way to get rid of a temptation is to yield to it.", "avtor": "Oscar Wilde"},
    {"navedek": "Food is our common ground, a universal experience.", "avtor": "James Beard"},
    {"navedek": "Life is uncertain. Eat dessert first.", "avtor": "Ernestine Ulmer"},
    {"navedek": "All you need is love. But a little chocolate now and then doesn't hurt.", "avtor": "Charles M. Schulz"},
    {"navedek": "Tell me what you eat, and I will tell you what you are.", "avtor": "Jean Anthelme"}
]

def seed_quotes():
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        
        for quote in quotes:
            cur.execute("""
                SELECT 1 FROM navedki WHERE navedek = %s AND avtor = %s
            """, (quote['navedek'], quote['avtor']))
            
            exists = cur.fetchone()
            
            if not exists:
                cur.execute("""
                    INSERT INTO navedki (navedek, avtor)
                    VALUES (%s, %s)
                """, (quote['navedek'], quote['avtor']))
                print(f"Inserted: {quote['navedek']} — {quote['avtor']}")
            else:
                print(f"Skipped (already exists): {quote['navedek']} — {quote['avtor']}")
        
        conn.commit()
    except Exception as e:
        print(f"Error during seeding: {e}")
    finally:
        if conn:
            conn.close()

#if __name__ == '__main__':
    #seed_quotes()            