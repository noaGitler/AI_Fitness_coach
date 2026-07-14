import sqlite3

class DBManager:
    def __init__(self, db_name="fitness_app.db"):
        self.db_path = db_name
        self.init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """מייצר את 3 הטבלאות המשודרגות עם תמיכה ב- contact_type ומיקום דינמי"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        # 1. טבלת auth
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)

        # 2. טבלת profiles - כולל שדות למיקום הגיאוגרפי הדינמי האחרון!
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                gender TEXT,
                age INTEGER,
                height REAL,
                weight REAL,
                last_latitude REAL,
                last_longitude REAL,
                last_location_name TEXT,
                FOREIGN KEY (user_id) REFERENCES auth (id) ON DELETE CASCADE
            )
        """)

        # 3. טבלת emergency_contacts - הוספת contact_type (private / official)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emergency_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                contact_name TEXT NOT NULL,
                contact_phone TEXT NOT NULL,
                contact_type TEXT NOT NULL, 
                FOREIGN KEY (user_id) REFERENCES auth (id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()
        print("[DATABASE] SQLite Premium Split-SOS Schema initialized successfully.")

    def register_user(self, username, password, gender, age, height, weight, ice_name, ice_phone, official_service):
        """שומר במכה אחת את המשתמש, המדדים הפיזיולוגיים ושני אנשי הקשר (אבא + שירות רשמי)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # א) טבלת auth
            cursor.execute("INSERT INTO auth (username, password) VALUES (?, ?)", (username, password))
            user_id = cursor.lastrowid

            # ב) טבלת profiles (מיקום ריק בהתחלה, נדגום אותו דינמית באימון)
            cursor.execute("""
                INSERT INTO profiles (user_id, gender, age, height, weight, last_latitude, last_longitude, last_location_name)
                VALUES (?, ?, ?, ?, ?, NULL, NULL, 'Not Tracked Yet')
            """, (user_id, gender, age, height, weight))

            # ג) הכנסת איש קשר פרטי (אבא / שכן)
            cursor.execute("""
                INSERT INTO emergency_contacts (user_id, contact_name, contact_phone, contact_type)
                VALUES (?, ?, ?, 'private')
            """, (user_id, ice_name, ice_phone))

            # ד) הכנסת שירות הצלה רשמי נבחר (מד"א או משטרה)
            off_phone = "101" if "MADA" in official_service or "מד\"א" in official_service else "100"
            cursor.execute("""
                INSERT INTO emergency_contacts (user_id, contact_name, contact_phone, contact_type)
                VALUES (?, ?, ?, 'official')
            """, (user_id, official_service, off_phone))

            conn.commit()
            print(f"[DATABASE] Dual-SOS Records locked for '{username}' (Private + Official).")
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def authenticate_user(self, username, password):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM auth WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        return {"id": user[0], "username": user[1]} if user else None

    def update_live_location(self, user_id, lat, lon, loc_name):
        """מעדכן בלייב את המיקום הגיאוגרפי האוטומטי שהמערכת זיהתה בתחילת האימון"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE profiles 
            SET last_latitude = ?, last_longitude = ?, last_location_name = ?
            WHERE user_id = ?
        """, (lat, lon, loc_name, user_id))
        conn.commit()
        conn.close()
        print(f"[DATABASE] Live GPS tracking synced for User ID {user_id}: {loc_name}")

    def get_all_emergency_contacts(self, user_id):
        """שולף את שני אנשי הקשר (גם את אבא וגם את מד"א) ברגע האמת של ה-SOS"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT contact_name, contact_phone, contact_type 
            FROM emergency_contacts WHERE user_id = ?
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        contacts = {}
        for row in rows:
            contacts[row[2]] = {"name": row[0], "phone": row[1]}
        return contacts


