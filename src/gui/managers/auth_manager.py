from PyQt6.QtCore import QObject, pyqtSignal
from src.database.db_manager import DBManager

class AuthManager(QObject):
    """
    מנהל האימות והרישום הרשמי של המערכת (SOLID - Single Responsibility Principle).
    מבודד את הלוגיקה והגישה ל-DBManager ומחזיר תוצאות ל-MainWindow באמצעות סיגנלים.
    """
    # סיגנלים המדווחים ל-MainWindow על תוצאות הפעולות
    login_success = pyqtSignal(dict)      # משדר את ה-user_data (מילון עם id ו-username)
    login_failed = pyqtSignal(str)        # משדר הודעת שגיאה ממוקדת למסך הכניסה
    
    registration_success = pyqtSignal(dict) # משדר את ה-user_data של המשתמש החדש לאחר כניסה אוטומטית
    registration_failed = pyqtSignal(str)   # משדר הודעת שגיאה ממוקדת למסך ההרשמה
    logout_success = pyqtSignal()  # סיגנל חדש שיסמן למיין שהתנתקנו בהצלחה

    def __init__(self):
        super().__init__()
        self.db = DBManager() # שימוש במנהל הנתונים של האפליקציה
        self.current_user = None # שומר את המידע על המשתמש המחובר כרגע (במקום self.current_user במיין)

    def login(self, username, password):
        """
        מטפל בלוגיקת אימות המשתמש (במקום process_login במיין).
        """
        # בדיקת תקינות בסיסית של קלט
        if not username.strip() or not password.strip():
            self.login_failed.emit("Username and password cannot be empty.")
            return False

        # פנייה לפונקציה המדויקת מהדאטאבייס שלך
        user_data = self.db.authenticate_user(username, password)
        
        if user_data:
            self.current_user = user_data
            print(f"[AUTH] User verified successfully: {user_data['username']} (ID: {user_data['id']})")
            self.login_success.emit(user_data)
            return True
        else:
            print(f"[AUTH] Authentication failed for username: {username}")
            self.login_failed.emit("Invalid username or password.")
            return False

    def register(self, username, password, gender, age, height, weight, ice_name, ice_phone, official_service):
        """
        מטפל בלוגיקת הרישום המורכבת של המערכת (במקום process_registration במיין).
        """
        # קריאה לפונקציית הרישום הרשמית והענקית מהדאטאבייס שלך (register_user)
        success = self.db.register_user(
            username, password, gender, age, height, weight, ice_name, ice_phone, official_service
        )
        
        if success:
            print(f"[AUTH] New account successfully initialized in database for: {username}")
            # בול כמו במיין המקורי שלך: מיד אחרי רישום מוצלח, מבצעים כניסה אוטומטית (authenticate)
            user_data = self.db.authenticate_user(username, password)
            if user_data:
                self.current_user = user_data
                self.registration_success.emit(user_data)
                return True
        
        # אם הרישום נכשל (למשל IntegrityError כשהשם תפוס)
        print(f"[AUTH] Registration rejected for username: {username}")
        self.registration_failed.emit("Username already exists. Choose another.")
        return False

    def logout(self):
        """מנתק את המשתמש ומנקה את נתוני הסשן הנוכחי"""
        if self.current_user:
            print(f"[AUTH] Secure log out initialized for user: {self.current_user['username']}")
        self.current_user = None
        self.logout_success.emit()  # <-- להוסיף את השורה הזו כאן!

    def is_authenticated(self):
        """מחזיר האם יש משתמש שמחובר כרגע במערכת"""
        return self.current_user is not None