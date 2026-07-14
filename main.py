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
    print("[INIT] QApplication created successfully.")
    
    # יצירת והצגת החלון הראשי (הוא כבר יטען את מסך ה-Login מעוצב על ההתחלה)
    print("[GUI] Constructing and displaying MainWindow...")
    window = MainWindow()
    window.show()
    
    print("[SYSTEM] Application is running. Background QThreads and Database are active.\n")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()





# import sys
# from PyQt6.QtWidgets import QApplication

# print("[STATUS] Starting script, importing core modules...")
# from src.gui.main_window import MainWindow
# from src.database.db_manager import DBManager

# def main():
#     print("\n" + "="*40)
#     print("[INIT] Launching Multi-Threaded AI Fitness Coach Application...")
#     print("="*40)
    
#     # אתחול וחיבור למסד הנתונים המשולש והחדש (SQLite)
#     print("[INIT] Connecting to SQLite local database file...")
#     db = DBManager() 
    
#     app = QApplication(sys.argv)
#     print("[INIT] QApplication created successfully.")
    
#     # יצירת והצגת החלון הראשי
#     print("[GUI] Constructing and displaying MainWindow...")
#     window = MainWindow()
#     window.show()
    
#     print("[SYSTEM] Application is running. Background QThreads and Database are active.\n")
#     sys.exit(app.exec())

# if __name__ == "__main__":
#     main()






# import sys
# from PyQt6.QtWidgets import QApplication

# print("[STATUS] Starting script, importing core modules...")
# from src.gui.main_window import MainWindow

# def main():
#     print("\n" + "="*40)
#     print("[INIT] Launching Multi-Threaded AI Fitness Coach Application...")
#     print("="*40)
    
#     app = QApplication(sys.argv)
#     print("[INIT] QApplication created successfully.")
    
#     # יצירת והצגת החלון הראשי (הוא כבר מפעיל את החוטים שלו באופן פנימי ומודולרי!)
#     print("[GUI] Constructing and displaying MainWindow...")
#     window = MainWindow()
#     window.show()
    
#     print("[SYSTEM] Application is running. Background QThreads are active.\n")
#     sys.exit(app.exec())

# if __name__ == "__main__":
#     main()











# import sys
# import cv2
# import os

# print("[STATUS] Starting script, importing PyQt6 modules...")
# from PyQt6.QtWidgets import QApplication, QMessageBox
# from PyQt6.QtCore import QTimer

# print("[STATUS] Importing GUI modules...")
# from src.gui.main_window import MainWindow

# print("[STATUS] Importing AI modules...")
# from src.ai.pose_detector import PoseDetector


# def main():
#     print("\n" + "="*40)
#     print("[INIT] Entering main() function...")
#     print("="*40)
    
#     sys_app = QApplication(sys.argv)
#     print("[INIT] QApplication created successfully.")
    
#     # אתחול מנוע ה-AI הראשי
#     print("[INIT] Initializing PoseDetector (MediaPipe backend)...")
#     detector = PoseDetector()
#     print("[INIT] PoseDetector initialized successfully.")
    
#     # פתיחת המצלמה
#     print("[CAMERA] Attempting to open Webcam (ID: 0) with CAP_DSHOW...")
#     cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
#     if not cap.isOpened():
#         print("[ERROR] CAMERA ACCESS FAILED! Webcam might be locked by another app.")
#         msg = QMessageBox()
#         msg.setIcon(QMessageBox.Icon.Critical)
#         msg.setText("Camera Access Error")
#         msg.setInformativeText("Webcam is being used by another application. Please close other apps.")
#         msg.exec()
#         sys.exit(1)
        
#     print("[CAMERA] Webcam opened successfully!")
    
#     # הצגת החלון הראשי של האפליקציה
#     print("[GUI] Constructing MainWindow...")
#     app = MainWindow()
#     print("[GUI] Displaying MainWindow...")
#     app.show()
    
#     # לולאת הוידאו הדינמית
#     print("[TIMER] Setting up QTimer for the video loop...")
#     timer = QTimer()
    
#     global is_first_frame
#     is_first_frame = True
    
#     def video_loop():
#         global is_first_frame
#         if is_first_frame:
#             print("[LOOP] Video loop running! Reading frames from camera...")
            
#         # טריק ריקון התור (Buffer Flushing) לפתרון הדיליי האקטיבי
#         for _ in range(4):
#             cap.grab()
            
#         ret, frame = cap.read()
#         if ret:
#             if is_first_frame:
#                 print("[LOOP] Successfully grabbed a frame. Sending to AI...")
                
#             # אנחנו שולחים ל-AI את התרגיל הנוכחי והדינמי שהחלון הראשי מחזיק באותו רגע!
#             current_exercise = app.exercise
#             frame = detector.process(frame, exercise=current_exercise)
            
#             # מעבירים את הפריים המעובד לחלון התצוגה
#             app.video_panel.update_frame(frame)
            
#             if is_first_frame:
#                 print("[LOOP] GUI updated with the first frame. Loop is healthy!\n")
#                 is_first_frame = False
            
#     timer.timeout.connect(video_loop)
#     print("[TIMER] Starting timer with 30ms interval...")
#     timer.start(30) 
    
#     # הפעלת לולאת האירועים של PyQt6
#     print("[SYSTEM] Entering system main event loop. App is running.\n")
#     exit_code = sys_app.exec()
    
#     print("\n" + "="*40)
#     print("[SHUTDOWN] Application closing, releasing resources...")
#     cap.release()
#     cv2.destroyAllWindows()
#     print("[SHUTDOWN] Cleanup complete. Exiting.")
#     print("="*40)
#     sys.exit(exit_code)

# if __name__ == "__main__":
#     main()




