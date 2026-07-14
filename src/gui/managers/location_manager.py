import threading
import requests
from PyQt6.QtCore import QObject, pyqtSignal
from src.database.db_manager import DBManager

class LocationManager(QObject):
    """
    מנהל המיקום הגיאוגרפי הרשמי של האפליקציה (SOLID - Single Responsibility Principle).
    אחראי בלעדית על דגימת ה-Live GPS מהרשת וסנכרונו מול בסיס הנתונים לצרכי ה-SOS.
    """
    # סיגנלים לעדכון המערכת בתוצאות המעקב
    location_synced = pyqtSignal(str)   # משדר את שם המיקום שחולץ (למשל: "Bnei Brak, Israel")
    tracking_failed = pyqtSignal(str)   # משדר הודעת שגיאה במקרה של תקלת תקשורת

    def __init__(self):
        super().__init__()
        self.db = DBManager()

    def trigger_live_geolocation_tracking(self, user_id):
        """
        מפעיל טרד רקע עצמאי שמאתר את המיקום הגיאוגרפי של המתאמנת ומעדכן את ה-DB.
        (בול כמו הלוגיקה המקורית במיין שלך, רק מבודד ומאובטח)
        """
        if user_id is None:
            self.tracking_failed.emit("No active user session for location tracking.")
            return

        def run():
            try:
                # פנייה ל-API הציבורי שבו השתמשת בקוד המקור
                response = requests.get("http://ip-api.com/json/", timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    lat = data.get("lat", 0.0)
                    lon = data.get("lon", 0.0)
                    city = data.get("city", "Unknown City")
                    country = data.get("country", "Unknown Country")
                    loc_name = f"{city}, {country}"
                    
                    # עדכון ישיר ב-DB באמצעות המתודה המקורית שלך
                    self.db.update_live_location(user_id, lat, lon, loc_name)
                    
                    # איתות לעולם שהסנכרון הצליח
                    print(f"[LOCATION] Live GPS successfully locked: {loc_name}")
                    self.location_synced.emit(loc_name)
                else:
                    raise requests.RequestException(f"Status code: {response.status_code}")
                    
            except Exception as e:
                error_msg = f"Geolocation ping failed (Offline?): {e}"
                print(f"[LOCATION MONITOR] {error_msg}")
                self.tracking_failed.emit(error_msg)

        # הפעלת הטרד כטרד-עבד (daemon) כדי שלא יתקע את סגירת האפליקציה
        threading.Thread(target=run, daemon=True).start()