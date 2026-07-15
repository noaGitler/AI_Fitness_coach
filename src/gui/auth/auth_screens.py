from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QRadioButton, QButtonGroup, QComboBox
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal as Signal
from PyQt6.QtGui import QFont

class LoginScreen(QWidget):
    """The login screen: username/password fields and a link to registration."""
    login_requested = Signal(str, str)
    go_to_register = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        title = QLabel("NEXUS LOGIN")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("SECURE ACCESS PORTAL")
        subtitle.setFont(QFont("Segoe UI", 10))
        layout.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFixedWidth(280)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedWidth(280)

        

        layout.addWidget(self.username_input, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.password_input, alignment=Qt.AlignmentFlag.AlignCenter)

        self.error_label = QLabel("")
        layout.addWidget(self.error_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.login_btn = QPushButton("CONNECT TO SYSTEM")
        self.login_btn.setFixedWidth(280)
        self.login_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.register_link = QPushButton("New user? Create a secure profile →")
        self.register_link.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_link.clicked.connect(self.go_to_register.emit)
        layout.addWidget(self.register_link, alignment=Qt.AlignmentFlag.AlignCenter)


        title.setObjectName("LoginTitle")
        subtitle.setObjectName("LoginSubtitle")
        self.error_label.setObjectName("ErrorLabel")
        self.login_btn.setObjectName("ConnectBtn")
        self.register_link.setObjectName("LinkBtn")


    def handle_login(self):
        user = self.username_input.text().strip()
        pwd = self.password_input.text().strip()
        if user and pwd:
            self.login_requested.emit(user, pwd)
        else:
            self.error_label.setText("Please fill in all security fields.")


class RegisterScreen(QWidget):
    """The registration screen: account details, bio fields, and emergency contacts."""
    register_requested = Signal(str, str, str, int, float, float, str, str, str)
    go_to_login = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        title = QLabel("CREATE PROFILE")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Choose Username")
        self.user_input.setFixedWidth(300)
        layout.addWidget(self.user_input, alignment=Qt.AlignmentFlag.AlignCenter)

        self.pwd_input = QLineEdit()
        self.pwd_input.setPlaceholderText("Choose Password")
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setFixedWidth(300)
        layout.addWidget(self.pwd_input, alignment=Qt.AlignmentFlag.AlignCenter)

        gender_box = QWidget()
        gender_box.setFixedWidth(300)
        gender_layout = QHBoxLayout(gender_box)
        gender_layout.setContentsMargins(0, 0, 0, 0)
        gender_layout.setSpacing(15)

        self.gender_group = QButtonGroup(self)
        self.rb_female = QRadioButton("Female")
        self.rb_male = QRadioButton("Male")
        self.rb_other = QRadioButton("Other")
        self.rb_female.setChecked(True)

        radio_style = """
            QRadioButton { color: #8a99a6; font-size: 13px; background: transparent; }
            QRadioButton:checked { color: #00f3ff; font-weight: bold; }
        """
        for rb in [self.rb_female, self.rb_male, self.rb_other]:
            self.gender_group.addButton(rb)
            gender_layout.addWidget(rb)
        layout.addWidget(gender_box, alignment=Qt.AlignmentFlag.AlignCenter)

        row_bio = QHBoxLayout()
        row_bio.setSpacing(10)
        
        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("Age")
        self.age_input.setFixedWidth(145)
        
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Height (cm)")
        self.height_input.setFixedWidth(145)
        
        row_bio.addWidget(self.age_input)
        row_bio.addWidget(self.height_input)
        layout.addLayout(row_bio)

        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText("Weight (kg)")
        self.weight_input.setFixedWidth(300)
        layout.addWidget(self.weight_input, alignment=Qt.AlignmentFlag.AlignCenter)

        # Part 3: emergency contacts
        contact_title = QLabel("IN CASE OF EMERGENCY (SOS)")
        contact_title.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        layout.addWidget(contact_title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.ice_name_input = QLineEdit()
        self.ice_name_input.setPlaceholderText("Private Contact Name (e.g., Father)")
        self.ice_name_input.setFixedWidth(300)
        layout.addWidget(self.ice_name_input, alignment=Qt.AlignmentFlag.AlignCenter)

        self.ice_phone_input = QLineEdit()
        self.ice_phone_input.setPlaceholderText("Private Contact Phone")
        self.ice_phone_input.setFixedWidth(300)
        layout.addWidget(self.ice_phone_input, alignment=Qt.AlignmentFlag.AlignCenter)

        service_title = QLabel("SELECT NATIONAL EMERGENCY SERVICE")
        service_title.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        layout.addWidget(service_title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.official_service_input = QComboBox()
        self.official_service_input.setFixedWidth(300)
        
        
        self.official_service_input.addItems(["MADA Ambulance (101)", "Israel Police (100)"])
        layout.addWidget(self.official_service_input, alignment=Qt.AlignmentFlag.AlignCenter)

        self.error_label = QLabel("")
        layout.addWidget(self.error_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.register_btn = QPushButton("INITIALIZE SECURE PROFILE")
        self.register_btn.setFixedWidth(300)
        self.register_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_btn.clicked.connect(self.handle_registration)
        layout.addWidget(self.register_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.back_btn = QPushButton("← Already registered? Log in")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self.go_to_login.emit)
        layout.addWidget(self.back_btn, alignment=Qt.AlignmentFlag.AlignCenter)


        title.setObjectName("RegisterTitle")
        contact_title.setObjectName("ContactTitle")
        service_title.setObjectName("ServiceTitle")
        self.error_label.setObjectName("ErrorLabel")
        self.register_btn.setObjectName("RegisterBtn")
        self.back_btn.setObjectName("LinkBtn")


    def handle_registration(self):
        user = self.user_input.text().strip()
        pwd = self.pwd_input.text().strip()
        
        gender = "Female"
        if self.rb_male.isChecked(): gender = "Male"
        elif self.rb_other.isChecked(): gender = "Other"
        
        age_text = self.age_input.text().strip()
        h_text = self.height_input.text().strip()
        w_text = self.weight_input.text().strip()
        ice_name = self.ice_name_input.text().strip()
        ice_phone = self.ice_phone_input.text().strip()
        official_service = self.official_service_input.currentText()

        if not (user and pwd and age_text and h_text and w_text and ice_name and ice_phone):
            self.error_label.setText("All security fields are required.")
            return

        try:
            age = int(age_text)
            height = float(h_text)
            weight = float(w_text)
        except ValueError:
            self.error_label.setText("Age, Height, and Weight must be numbers.")
            return

        self.register_requested.emit(user, pwd, gender, age, height, weight, ice_name, ice_phone, official_service)



