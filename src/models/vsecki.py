from datetime import datetime, timedelta
import calendar
from psycopg2.extras import RealDictCursor
def create_table(conn):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vsecki (
                id SERIAL PRIMARY KEY,
                uporabnik_id INTEGER NOT NULL REFERENCES uporabniki(id) ON DELETE CASCADE,
                recept_id INTEGER NOT NULL REFERENCES recepti(id) ON DELETE CASCADE,
                datum_vsecka TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (uporabnik_id, recept_id)
            );
        """)
class LikeSystem:
    """
    System for managing recipe likes with PostgreSQL
    """
    
    #@staticmethod
    
    
    @staticmethod
    def add_like(conn, user_id, recipe_id):
        """
        Add a like for a recipe
        Returns: (success, message)
        """
        cur = conn.cursor()
        
        try:
            # PostgreSQL handles ON CONFLICT
            cur.execute("""
                INSERT INTO vsecki (uporabnik_id, recept_id)
                VALUES (%s, %s)
                ON CONFLICT (uporabnik_id, recept_id) DO NOTHING
                RETURNING id
            """, (user_id, recipe_id))
            
            result = cur.fetchone()
            conn.commit()
            cur.close()
            
            if result:
                return True, "Všeček dodan"
            else:
                return False, "Recept ste že všečkali"
        except Exception as e:
            conn.rollback()
            cur.close()
            return False, f"Napaka pri dodajanju všečka: {str(e)}"
    
    @staticmethod
    def remove_like(conn, user_id, recipe_id):
        """
        Remove a like from a recipe
        Returns: (success, message)
        """
        cur = conn.cursor()
        
        try:
            cur.execute("""
                DELETE FROM vsecki 
                WHERE uporabnik_id = %s AND recept_id = %s
                RETURNING id
            """, (user_id, recipe_id))
            
            result = cur.fetchone()
            conn.commit()
            cur.close()
            
            if result:
                return True, "Všeček odstranjen"
            else:
                return False, "Všeček ne obstaja"
        except Exception as e:
            conn.rollback()
            cur.close()
            return False, f"Napaka pri odstranjevanju všečka: {str(e)}"
    
    @staticmethod
    def toggle_like(conn, user_id, recipe_id):
        """
        Toggle like status for a recipe
        Returns: (liked, success, message)
        """
        cur = conn.cursor()
        
        # Check current status
        cur.execute("""
            SELECT id FROM vsecki 
            WHERE uporabnik_id = %s AND recept_id = %s
        """, (user_id, recipe_id))
        
        exists = cur.fetchone()
        cur.close()
        
        if exists:
            # Unlike
            success, message = LikeSystem.remove_like(conn, user_id, recipe_id)
            return False, success, message
        else:
            # Like
            success, message = LikeSystem.add_like(conn, user_id, recipe_id)
            return True, success, message
    
    @staticmethod
    def get_recipe_likes_count(conn, recipe_id):
        """
        Get total number of likes for a recipe
        """
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM vsecki 
            WHERE recept_id = %s
        """, (recipe_id,))
        
        count = cur.fetchone()[0]
        cur.close()
        return count
    
    @staticmethod
    def get_recipe_likes_by_month(conn, recipe_id, year, month):
        """
        Get number of likes for a recipe in a specific month
        Args:
            recipe_id: ID of the recipe
            year: Year (e.g., 2024)
            month: Month (1-12)
        """
        # Get first and last day of month
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)
        
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM vsecki 
            WHERE recept_id = %s 
            AND datum_vsecka >= %s 
            AND datum_vsecka <= %s
        """, (recipe_id, first_day, last_day))
        
        count = cur.fetchone()[0]
        cur.close()
        return count
    
    @staticmethod
    def get_monthly_likes_report(conn, recipe_id, year):
        """
        Get likes count for each month of a year
        Returns: Dictionary with month names as keys and like counts as values
        """
        months = {
            1: 'Januar', 2: 'Februar', 3: 'Marec', 4: 'April',
            5: 'Maj', 6: 'Junij', 7: 'Julij', 8: 'Avgust',
            9: 'September', 10: 'Oktober', 11: 'November', 12: 'December'
        }
        
        report = {}
        for month_num, month_name in months.items():
            count = LikeSystem.get_recipe_likes_by_month(conn, recipe_id, year, month_num)
            report[month_name] = count
        
        return report
    
    @staticmethod
    def user_has_liked(conn, user_id, recipe_id):
        """
        Check if user has liked a specific recipe
        """
        cur = conn.cursor()
        cur.execute("""
            SELECT id FROM vsecki 
            WHERE uporabnik_id = %s AND recept_id = %s
        """, (user_id, recipe_id))
        
        result = cur.fetchone() is not None
        cur.close()
        return result
    
    @staticmethod
    def get_user_liked_recipes(conn, user_id):
        """
        Get all recipes liked by a user
        """
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT r.id, r.naslov, r.opis, v.datum_vsecka,
                   u.uporabnisko_ime as avtor
            FROM vsecki v
            JOIN recepti r ON v.recept_id = r.id
            LEFT JOIN uporabniki u ON r.uporabnik_id = u.id
            WHERE v.uporabnik_id = %s
            ORDER BY v.datum_vsecka DESC
        """, (user_id,))
        
        results = cur.fetchall()
        cur.close()
        return results
    
    @staticmethod
    def get_most_liked_recipes(conn, limit=10):
        """
        Get most liked recipes
        """
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT r.id, r.naslov, r.opis, 
                   COUNT(v.id) as like_count,
                   u.uporabnisko_ime as avtor
            FROM recepti r
            LEFT JOIN vsecki v ON r.id = v.recept_id
            LEFT JOIN uporabniki u ON r.uporabnik_id = u.id
            GROUP BY r.id, r.naslov, r.opis, u.uporabnisko_ime
            ORDER BY like_count DESC
            LIMIT %s
        """, (limit,))
        
        results = cur.fetchall()
        cur.close()
        return results
    
    @staticmethod
    def get_recent_likes(conn, recipe_id, limit=10):
        """
        Get recent likes for a recipe with user info
        """
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT u.uporabnisko_ime, v.datum_vsecka
            FROM vsecki v
            JOIN uporabniki u ON v.uporabnik_id = u.id
            WHERE v.recept_id = %s
            ORDER BY v.datum_vsecka DESC
            LIMIT %s
        """, (recipe_id, limit))
        
        results = cur.fetchall()
        cur.close()
        return results
    
    @staticmethod
    def get_like_statistics(conn, recipe_id):
        """
        Get comprehensive statistics for a recipe
        """
        stats = {
            'total_likes': LikeSystem.get_recipe_likes_count(conn, recipe_id),
            'current_year_monthly': LikeSystem.get_monthly_likes_report(conn, recipe_id, datetime.now().year),
            'recent_likes': LikeSystem.get_recent_likes(conn, recipe_id, 5)
        }
        
        # Get likes for last 30 days
        cur = conn.cursor()
        thirty_days_ago = datetime.now().replace(hour=0, minute=0, second=0) - timedelta(days=30)
        cur.execute("""
            SELECT COUNT(*) FROM vsecki 
            WHERE recept_id = %s AND datum_vsecka >= %s
        """, (recipe_id, thirty_days_ago))
        stats['last_30_days'] = cur.fetchone()[0]
        
        # Get likes for today
        today_start = datetime.now().replace(hour=0, minute=0, second=0)
        cur.execute("""
            SELECT COUNT(*) FROM vsecki 
            WHERE recept_id = %s AND datum_vsecka >= %s
        """, (recipe_id, today_start))
        stats['today'] = cur.fetchone()[0]
        
        cur.close()
        return stats
    
    @staticmethod
    def get_recipes_with_like_status(conn, user_id=None, limit=None):
        """
        Get recipes with like counts and user's like status
        """
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                r.id, 
                r.naslov, 
                r.opis,
                r.slika_url,
                r.cas_priprave,
                r.tezavnost,
                r.datum_kreiranja,
                u.uporabnisko_ime as avtor,
                COUNT(DISTINCT v.id) as like_count
        """
        
        if user_id:
            query += """
                ,CASE WHEN EXISTS (
                    SELECT 1 FROM vsecki 
                    WHERE uporabnik_id = %s AND recept_id = r.id
                ) THEN true ELSE false END as user_has_liked
            """
        
        query += """
            FROM recepti r
            LEFT JOIN uporabniki u ON r.uporabnik_id = u.id
            LEFT JOIN vsecki v ON r.id = v.recept_id
            GROUP BY r.id, u.uporabnisko_ime
            ORDER BY r.datum_kreiranja DESC
        """
        
        if limit:
            query += " LIMIT %s"
        
        params = [user_id] if user_id else []
        if limit:
            params.append(limit)
        
        cur.execute(query, params)
        results = cur.fetchall()
        cur.close()
        
        return results