import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
from flask_login import UserMixin
from flask import current_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import psycopg2
from psycopg2.extras import RealDictCursor
def create_table(cur):
        cur.execute("""
            CREATE TABLE IF NOT EXISTS uporabniki (
                id SERIAL PRIMARY KEY,
                uporabnisko_ime VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                geslo VARCHAR(255) NOT NULL,
                datum_registracije TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
class User(UserMixin):
    """
    Razred uproabnik
    """
    
    def __init__(self, user_id=None, username=None, email=None, password_hash=None):
        self.id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.reset_token = None
        self.reset_token_expiry = None
    
    @staticmethod
    def hash_password(password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    #@staticmethod    
    
    
    def verify_password(self, password):
        """Verify password against stored hash"""
        return self.password_hash == self.hash_password(password)
    
    @staticmethod
    def validate_email(email):
        """TODO: Pomozna metoda za preverjanje email naslova, tretnutna implementacija ne podpira še te zmogljivosti"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_username(username):
        """Validate username (alphanumeric, 3-20 characters)"""
        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        return re.match(pattern, username) is not None
    
    @staticmethod
    def validate_password(password):
        """Validate password strength (min 8 chars, contains number and letter)"""
        if len(password) < 8:
            return False, "Geslo mora vsebovati vsaj 8 znakov"
        if not any(c.isdigit() for c in password):
            return False, "Geslo mora vsebovati vsaj eno številko"
        if not any(c.isalpha() for c in password):
            return False, "Geslo mora vsebovati vsaj eno črko"
        return True, "Geslo je veljavno"
    
    def check_user_exists(self, conn):
        """
        Check if user with same username or email already exists
        Returns: (exists, message)
        """
        cur = conn.cursor()
        
        # Check username
        cur.execute("SELECT id FROM uporabniki WHERE uporabnisko_ime = %s", (self.username,))
        if cur.fetchone():
            cur.close()
            return True, "Uporabniško ime že obstaja"
        
        
        # TODO: Pomozna metoda za preverjanje email naslova, tretnutna implementacija ne podpira še te zmogljivosti
        #cur.execute("SELECT id FROM uporabniki WHERE email = %s", (self.email,))
        #if cur.fetchone():
        #    cur.close()
        #    return True, "Email naslov že obstaja"
        
        cur.close()
        return False, "Uporabnik ne obstaja"
    
    def validate_registration_data(self):
        """
        Validate all registration data
        Returns: (is_valid, error_message)
        """
        if not self.username or not self.email:
            return False, "Vsa polja morajo biti izpolnjena"
        
        if not self.validate_username(self.username):
            return False, "Uporabniško ime mora vsebovati 3-20 znakov (črke, številke, _)"
        
        #if not self.validate_email(self.email):
        #    return False, "Neveljaven email naslov"
        
        return True, "Podatki so veljavni"
    
    def register(self, conn, password):
        """
        Register new user
        Returns: (success, message)
        """
        # Validate password
        valid, msg = self.validate_password(password)
        if not valid:
            return False, msg
        
        # Validate other data
        valid, msg = self.validate_registration_data()
        if not valid:
            return False, msg
        
        # Check if user exists
        exists, msg = self.check_user_exists(conn)
        if exists:
            return False, msg
        
        # Hash password
        self.password_hash = self.hash_password(password)
        
        # Insert into database
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO uporabniki (uporabnisko_ime, email, geslo)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (self.username, self.email, self.password_hash))
            
            self.id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            return True, "Registracija uspešna"
        except Exception as e:
            conn.rollback()
            return False, f"Napaka pri registraciji: {str(e)}"
    
    @staticmethod
    def login(conn, username_or_email, password):
        """
        Login user
        Returns: (user_object, success, message)
        """
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Try to find user by username or email
        cur.execute("""
            SELECT id, uporabnisko_ime, email, geslo 
            FROM uporabniki 
            WHERE uporabnisko_ime = %s OR email = %s
        """, (username_or_email, username_or_email))
        
        row = cur.fetchone()
        cur.close()
        
        if not row:
            return None, False, "Napačno uporabniško ime ali geslo"
        
        # Create user object
        user = User(
            user_id=row['id'],
            username=row['uporabnisko_ime'],
            email=row['email'],
            password_hash=row['geslo']
        )
        
        # Verify password
        if not user.verify_password(password):
            return None, False, "Napačno uporabniško ime ali geslo"
        
        return user, True, "Prijava uspešna"
    
    def generate_reset_token(self):
        """Generate password reset token"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.now() + timedelta(hours=1)
        return self.reset_token
    
    def save_reset_token(self, conn):
        """Save reset token to database"""
        cur = conn.cursor()
        
        # First, check if columns exist and add them if they don't
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='uporabniki' AND column_name='reset_token'
        """)
        
        if not cur.fetchone():
            # Add reset token columns
            cur.execute("""
                ALTER TABLE uporabniki 
                ADD COLUMN IF NOT EXISTS reset_token VARCHAR(255),
                ADD COLUMN IF NOT EXISTS reset_token_expiry TIMESTAMP
            """)
            conn.commit()
        
        # Update reset token
        cur.execute("""
            UPDATE uporabniki 
            SET reset_token = %s, reset_token_expiry = %s
            WHERE id = %s
        """, (self.reset_token, self.reset_token_expiry, self.id))
        
        conn.commit()
        cur.close()
    
    @staticmethod
    def find_by_email(conn, email):
        """Find user by email"""
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id, uporabnisko_ime, email, geslo 
            FROM uporabniki 
            WHERE email = %s
        """, (email,))
        
        row = cur.fetchone()
        cur.close()
        
        if not row:
            return None
        
        return User(
            user_id=row['id'],
            username=row['uporabnisko_ime'],
            email=row['email'],
            password_hash=row['geslo']
        )
    
    @staticmethod
    def find_by_reset_token(conn, token):
        """Find user by reset token"""
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if reset_token column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='uporabniki' AND column_name='reset_token'
        """)
        
        if not cur.fetchone():
            cur.close()
            return None
        
        cur.execute("""
            SELECT id, uporabnisko_ime, email, geslo 
            FROM uporabniki 
            WHERE reset_token = %s AND reset_token_expiry > %s
        """, (token, datetime.now()))
        
        row = cur.fetchone()
        cur.close()
        
        if not row:
            return None
        
        return User(
            user_id=row['id'],
            username=row['uporabnisko_ime'],
            email=row['email'],
            password_hash=row['geslo']
        )
    
    def reset_password(self, conn, new_password):
        """Reset user password"""
        valid, msg = self.validate_password(new_password)
        if not valid:
            return False, msg
        
        self.password_hash = self.hash_password(new_password)
        
        cur = conn.cursor()
        cur.execute("""
            UPDATE uporabniki 
            SET geslo = %s, reset_token = NULL, reset_token_expiry = NULL
            WHERE id = %s
        """, (self.password_hash, self.id))
        
        conn.commit()
        cur.close()
        
        return True, "Geslo uspešno spremenjeno"
    
    def send_reset_email(self, reset_url):
        """TODO: Pomozna metoda za pošiljanje emaila za ponastavitev gesla, tretnutna implementacija ne podpira še te zmogljivosti"""
        sender_email = current_app.config.get('MAIL_USERNAME', 'noreply@example.com')
        sender_password = current_app.config.get('MAIL_PASSWORD', '')
        smtp_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
        smtp_port = current_app.config.get('MAIL_PORT', 587)
        
        message = MIMEMultipart('alternative')
        message['Subject'] = 'Ponastavitev gesla'
        message['From'] = sender_email
        message['To'] = self.email
        
        text = f"""
        Pozdravljeni {self.username},
        
        Prejeli smo zahtevo za ponastavitev vašega gesla.
        
        Za ponastavitev gesla kliknite na naslednjo povezavo:
        {reset_url}
        
        Povezava bo veljavna 1 uro.
        
        Če niste zahtevali ponastavitve gesla, ignorirajte to sporočilo.
        
        Lep pozdrav,
        Ekipa Skupina ZETA
        """
        
        html = f"""
        <html>
            <body>
                <h2>Ponastavitev gesla</h2>
                <p>Pozdravljeni {self.username},</p>
                <p>Prejeli smo zahtevo za ponastavitev vašega gesla.</p>
                <p>Za ponastavitev gesla kliknite na naslednjo povezavo:</p>
                <p><a href="{reset_url}">Ponastavi geslo</a></p>
                <p>Povezava bo veljavna 1 uro.</p>
                <p>Če niste zahtevali ponastavitve gesla, ignorirajte to sporočilo.</p>
                <p>Lep pozdrav,<br>Ekipa Skupina ZETA</p>
            </body>
        </html>
        """
        
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        
        message.attach(part1)
        message.attach(part2)
        
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)
            return True, "Email poslan"
        except Exception as e:
            return False, f"Napaka pri pošiljanju emaila: {str(e)}"
    
    # Likes methods
    def add_like(self, conn, recipe_id):
        """Add like to recipe"""
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO vsecki (uporabnik_id, recept_id)
                VALUES (%s, %s)
                ON CONFLICT (uporabnik_id, recept_id) DO NOTHING
            """, (self.id, recipe_id))
            
            affected = cur.rowcount
            conn.commit()
            cur.close()
            
            if affected > 0:
                return True, "Všeček dodan"
            else:
                return False, "Recept ste že všečkali"
        except Exception as e:
            conn.rollback()
            return False, f"Napaka pri dodajanju všečka: {str(e)}"
    
    def remove_like(self, conn, recipe_id):
        """Remove like from recipe"""
        try:
            cur = conn.cursor()
            cur.execute("""
                DELETE FROM vsecki 
                WHERE uporabnik_id = %s AND recept_id = %s
            """, (self.id, recipe_id))
            
            affected = cur.rowcount
            conn.commit()
            cur.close()
            
            if affected > 0:
                return True, "Všeček odstranjen"
            else:
                return False, "Všeček ne obstaja"
        except Exception as e:
            conn.rollback()
            return False, f"Napaka pri odstranjevanju všečka: {str(e)}"
    
    # Flask-Login required methods
    def get_id(self):
        return str(self.id)
    
    @staticmethod
    def get(conn, user_id):
        """Get user by ID for Flask-Login"""
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id, uporabnisko_ime, email, geslo 
            FROM uporabniki 
            WHERE id = %s
        """, (int(user_id),))
        
        row = cur.fetchone()
        cur.close()
        
        if not row:
            return None
        
        return User(
            user_id=row['id'],
            username=row['uporabnisko_ime'],
            email=row['email'],
            password_hash=row['geslo']
        )