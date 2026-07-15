from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class StatsCard(QFrame):
    """A small dashboard card showing a title and a large live-updating value."""
    def __init__(self, title, initial_value, parent=None):
        super().__init__(parent)
        self.setFixedSize(280, 110)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(2)
        
        self.title_label = QLabel(title.upper())
        self.title_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.value_label = QLabel(str(initial_value))
        self.value_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        layout.addWidget(self.value_label, alignment=Qt.AlignmentFlag.AlignRight)
      
        self.setObjectName("StatsCard")
        self.title_label.setObjectName("StatsTitle")
        self.value_label.setObjectName("StatsValue")

    def update_value(self, new_value):
        self.value_label.setText(str(new_value))


