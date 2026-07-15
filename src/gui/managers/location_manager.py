import threading
import requests
from PyQt6.QtCore import QObject, pyqtSignal
from src.database.db_manager import DBManager

class LocationManager(QObject):
    """
    The application's official location manager (SOLID - Single Responsibility Principle).
    Solely responsible for pulling live GPS from the network and syncing it to the database for SOS purposes.
    """
    # Signals for reporting tracking results
    location_synced = pyqtSignal(str)   # emits the resolved location name (e.g. "Bnei Brak, Israel")
    tracking_failed = pyqtSignal(str)   # emits an error message on a network failure

    def __init__(self):
        super().__init__()
        self.db = DBManager()

    def trigger_live_geolocation_tracking(self, user_id):
        """
        Starts a background thread that resolves the trainee's geographic
        location and updates the database.
        """
        if user_id is None:
            self.tracking_failed.emit("No active user session for location tracking.")
            return

        def run():
            try:
                # Call the public IP-geolocation API
                response = requests.get("http://ip-api.com/json/", timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    lat = data.get("lat", 0.0)
                    lon = data.get("lon", 0.0)
                    city = data.get("city", "Unknown City")
                    country = data.get("country", "Unknown Country")
                    loc_name = f"{city}, {country}"
                    
                    self.db.update_live_location(user_id, lat, lon, loc_name)
                    
                    # Emit a signal to indicate successful location update
                    print(f"[LOCATION] Live GPS successfully locked: {loc_name}")
                    self.location_synced.emit(loc_name)
                else:
                    raise requests.RequestException(f"Status code: {response.status_code}")
                    
            except Exception as e:
                error_msg = f"Geolocation ping failed (Offline?): {e}"
                print(f"[LOCATION MONITOR] {error_msg}")
                self.tracking_failed.emit(error_msg)

        # Run as a daemon thread so it doesn't block the app from closing
        threading.Thread(target=run, daemon=True).start()