import cv2
from PyQt6.QtCore import QThread, pyqtSignal

class VideoWorker(QThread):
    """חוט ייעודי שרץ ברקע, קורא מהמצלמה ומעבד את ה-AI בלי לתקוע את ה-GUI לעולם"""
    frame_ready = pyqtSignal(object) 
    metrics_ready = pyqtSignal(float, str) 
    
    # 🚨 סיגנלים של פרוטוקול החירום שלכן - נשמרים במלואם!
    sos_countdown_started = pyqtSignal()
    emergency_detected = pyqtSignal(str)
    emergency_trigger = pyqtSignal()

    def __init__(self):
        super().__init__()
        from src.ai.pose_detector import PoseDetector
        from src.ai.safety_protocols.fall_detector import FallDetector
        
        self.detector = PoseDetector()
        self.detector.worker_ref = self 
        self.fall_detector = FallDetector() # אתחול רכיב הבטיחות שלכן
        
        self.cap = None
        self.running = False
        self.current_exercise = None
        self.main_window_ref = None 

    def set_exercise(self, exercise):
        self.current_exercise = exercise

    def run(self):
        print("[THREAD] Background camera thread active.")
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.running = True
        
        while self.running:
            if self.cap and self.cap.isOpened():
                for _ in range(4):
                    self.cap.grab()
                    
                ret, frame = self.cap.read()
                if ret:
                    # 1. הרצת פרוטוקול הבטיחות והחירום שלכן
                    frame, alarm_triggered = self.fall_detector.process_frame(
                        frame, is_workout_active=self.current_exercise is not None
                    )

                    # 2. הקראת אזהרה ראשונית במידה ונוצרה
                    if getattr(self.fall_detector, 'pending_speech', None):
                        self.sos_countdown_started.emit()
                        self.fall_detector.pending_speech = None

                    # 3. בדיקת מצב Pause בחלון הראשי
                    is_paused_now = False
                    if self.main_window_ref and hasattr(self.main_window_ref, 'session_manager'):
                        is_paused_now = self.main_window_ref.session_manager.is_paused

                    # 4. עיבוד ה-AI (ספירת חזרות וציור שלד) - מתבצע פעם אחת בלבד!
                    if not is_paused_now and not self.fall_detector.was_low_in_last_frame and not alarm_triggered:
                        frame = self.detector.process(frame, exercise=self.current_exercise)
                    elif is_paused_now:
                        # במצב פאוז מאפסים מדדים ב-UI
                        self.metrics_ready.emit(0.0, "")

                    # 5. הפעלת אזעקת החירום הסופית שלכן במידה והטיימר של ה-10 שניות עבר
                    if alarm_triggered:
                        self.emergency_detected.emit("Fall detected!")
                        self.emergency_trigger.emit()

                    # 6. שידור גרפי יחיד ומסונכרן למסך ה-GUI (מעלים את הכפל לחלוטין!)
                    self.frame_ready.emit(frame)
            
            # מנוחה קבועה לשמירה על מעבד רגוע
            self.msleep(20) 
                
        if self.cap and self.cap.isOpened():
            self.cap.release()
        print("[THREAD] Background camera thread stopped safely.")

    def stop(self):
        self.running = False
        self.wait()