from PyQt6.QtCore import QObject, pyqtSignal
from src.database.db_manager import DBManager

class AuthManager(QObject):
    """
    The system's official authentication/registration manager (SOLID - Single Responsibility Principle).
    Isolates the DBManager access and reports results to MainWindow via signals.
    """
    # Signals reporting action results back to MainWindow
    login_success = pyqtSignal(dict)      # Reports the user_data (dictionary with id and username)
    login_failed = pyqtSignal(str)        # Reports a specific error message to the login screen
    
    registration_success = pyqtSignal(dict) # Reports the new user's data after automatic login
    registration_failed = pyqtSignal(str)   # Reports a specific error message to the registration screen
    logout_success = pyqtSignal()  # New signal to indicate successful logout

    def __init__(self):
        super().__init__()
        self.db = DBManager()  # the app's data manager
        self.current_user = None # stores the data of the currently logged-in user (instead of self.current_user in main window)

    def login(self, username, password):
        """Handles the user authentication logic."""
        # Basic input validation
        if not username.strip() or not password.strip():
            self.login_failed.emit("Username and password cannot be empty.")
            return False

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
        """Handles the full registration flow, including automatic login afterwards."""
        success = self.db.register_user(
            username, password, gender, age, height, weight, ice_name, ice_phone, official_service
        )
        
        if success:
            print(f"[AUTH] New account successfully initialized in database for: {username}")
            user_data = self.db.authenticate_user(username, password)
            if user_data:
                self.current_user = user_data
                self.registration_success.emit(user_data)
                return True
        
        print(f"[AUTH] Registration rejected for username: {username}")
        self.registration_failed.emit("Username already exists. Choose another.")
        return False

    def logout(self):
        """Logs the user out and clears the current session data."""
        if self.current_user:
            print(f"[AUTH] Secure log out initialized for user: {self.current_user['username']}")
        self.current_user = None
        self.logout_success.emit()  # <-- להוסיף את השורה הזו כאן!

    def is_authenticated(self):
        """Returns whether a user is currently logged in."""
        return self.current_user is not None