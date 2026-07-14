import sys
from PyQt6.QtWidgets import QApplication

print("[STATUS] Starting script, importing core modules...")
# עדכון נתיב הייבוא: MainWindow יושב כעת בתוך התיקייה המאורגנת החדשה של ה-GUI
from src.gui.main_window import MainWindow
from src.database.db_manager import DBManager

def main():
    print("\n" + "="*40)
    print("[INIT] Launching Multi-Threaded AI Fitness Coach Application...")
    print("="*40)
    
    # אתחול וחיבור למסד הנתונים המשולש והמאובטח (SQLite)
    print("[INIT] Connecting to SQLite local database file...")
    db = DBManager() 
    
    app = QApplication(sys.argv)
    try:
        with open("src/gui/styles/style.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
        print("[INIT] Custom stylesheet (QSS) loaded successfully.")
    except Exception as e:
        print(f"[WARNING] Could not load stylesheet: {e}")
        
    print("[INIT] QApplication created successfully.")
    
    # יצירת והצגת החלון הראשי (הוא כבר יטען את מסך ה-Login מעוצב על ההתחלה)
    print("[GUI] Constructing and displaying MainWindow...")
    window = MainWindow()
    window.show()
    
    print("[SYSTEM] Application is running. Background QThreads and Database are active.\n")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()