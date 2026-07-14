import cv2
import time 
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class FallDetector:
    def __init__(self):
        print("[SAFETY] Initializing Emergency Fall Detector...")
        model_path = 'pose_landmarker_full.task'
        options = vision.PoseLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=model_path), 
            running_mode=vision.RunningMode.IMAGE
        )
        self.detector = vision.PoseLandmarker.create_from_options(options)
        
        # משתני מצב של המערכת המקורית
        self.is_locked = False 
        self.system_initialized = False 
        self.was_low_in_last_frame = False 
        self.fall_start_time = None
        self.pending_speech = None

        # משתנים חדשים ללוגיקת ה"איש מת" (זיהוי תנועה בשכיבה)
        self.inactivity_timer_start = None
        self.prev_landmarks = None

    # ==========================================
    # פונקציות עזר לניהול זמנים ומצבים
    # ==========================================
    def reset_timers(self):
        """פונקציה שמאפסת את כל הטיימרים כשיש סימני חיים או כשקמים"""
        self.inactivity_timer_start = None
        self.fall_start_time = None

    def lock_system(self):
        """פונקציה שנועלת את המערכת במצב חירום"""
        self.is_locked = True
        self.reset_timers()
        self.system_initialized = False # דורש אתחול מחדש לאחר הנעילה
        print("[ALERT] Emergency protocol activated - LOCKING SYSTEM")

    def safe_lock_system(self):
        """פונקציה שנועלת את המערכת למנוחה (ללא קריאה לעזרה)"""
        self.is_locked = True
        self.reset_timers()
        self.system_initialized = False # דורש שהמתאמן יקום כדי לאתחל
        print("[SAFETY] Vital signs confirmed. Workout paused. Please stand up to resume.")


    # ==========================================
    # פונקציות לטיפול במצבי המתאמן
    # ==========================================
    def handle_missing_user(self, frame):
        """פונקציה שמנתחת מצב בו המתאמן נעלם בפתאומיות מהפריים"""
        if not self.system_initialized:
            cv2.putText(frame, "Waiting for user to enter...", (30, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
            return frame, False
            
        # אם הוא היה מאותחל ונעלם לאחר שהיה נמוך - זו סכנת נפילה!
        if self.was_low_in_last_frame:
            if self.fall_start_time is None:
                self.fall_start_time = time.time()
                self.pending_speech = "Fall detected. Emergency protocol will be activated in 10 seconds. Please show signs of life."
                print("[DEBUG] 1. FallDetector created speech note ONLY ONCE!")
            
            elapsed = time.time() - self.fall_start_time
            if elapsed >= 10.0:
                self.lock_system()
                return frame, True
            else:
                cv2.putText(frame, f"SOS in: {10.0 - elapsed:.1f}s", 
                            (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
        
        return frame, False

    def calculate_max_distance(self, current_landmarks, reference_landmarks):
        """פונקציית עזר לחישוב מרחק מקסימלי מהתנוחה השמורה (תנוחת הבסיס על הרצפה)"""
        if reference_landmarks is None:
            return 0
            
        points_to_check = [15, 16, 27, 28, 23, 24] # פרקי ידיים, קרסוליים, אגן
        max_dist = 0
        
        for idx in points_to_check:
            if current_landmarks[idx].visibility > 0.5:
                dist = ((current_landmarks[idx].x - reference_landmarks[idx].x)**2 + 
                        (current_landmarks[idx].y - reference_landmarks[idx].y)**2)**0.5
                if dist > max_dist:
                    max_dist = dist
        return max_dist

    def handle_lying_state(self, frame, current_landmarks):
        """מנתחת שכיבה - כולל זמן התייצבות למניעת זיהוי תנועת הנפילה כסימן חיים"""
        if self.inactivity_timer_start is None:
            self.inactivity_timer_start = time.time()
            self.prev_landmarks = current_landmarks # קביעת רפרנס התחלתי
            
        elapsed = time.time() - self.inactivity_timer_start
        
        # חישוב התזוזה מהרגע שהתייצבנו על הרצפה
        dist = self.calculate_max_distance(current_landmarks, self.prev_landmarks)
        
        if elapsed < 2.0:
            # ב-2 השניות הראשונות מאז שהאגן ירד נמוך, המתאמן עוד נופל/מתייצב.
            # לכן אנחנו מעדכנים את תמונת ה"רפרנס" ולא מחפשים סימני חיים עדיין.
            self.prev_landmarks = current_landmarks
        else:
            # עברו 2 שניות. הגוף נח. עכשיו כל תזוזה של מעל 0.05 מהרפרנס היא סימן חיים!
            if dist > 0.05:
                print(f"[DEBUG] Vital signs detected! (Moved: {dist:.3f}). Entering Safe-Lock.")
                self.safe_lock_system()
                return frame, False
                
        if elapsed >= 10.0:  # 10 שניות מהנפילה - אזעקה!
            self.lock_system()
            return frame, True
            
        # מציג את הספירה על המסך כדי שתוכלי לדבג ולראות מתי זה מזהה תנועה
        cv2.putText(frame, f"SOS in: {10.0 - elapsed:.1f}s", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
        return frame, False

    def handle_present_user(self, frame, detection_result):
        """פונקציה שמאתחלת או מנתחת מתאמן שנמצא כרגע בפריים"""
        landmarks_list = detection_result.pose_landmarks[0]
        current_landmarks = landmarks_list.landmark if hasattr(landmarks_list, 'landmark') else landmarks_list
        
        left_hip = current_landmarks[23]
        right_hip = current_landmarks[24]

        # תיקון בעיית ההסתרה: אם לא רואים את האגן, אבל כבר היינו בשכיבה - תמשיך לספור!
        if left_hip.visibility < 0.5 or right_hip.visibility < 0.5:
            if self.was_low_in_last_frame and not self.is_locked:
                return self.handle_lying_state(frame, current_landmarks)
            return frame, False

        mid_hip_y = (left_hip.y + right_hip.y) / 2

        if self.is_locked:
            if mid_hip_y < 0.8:
                self.is_locked = False
                self.was_low_in_last_frame = False
                self.system_initialized = True
                print("[SAFETY] System unlocked. User is standing.")
            return frame, False

        if mid_hip_y <= 0.8:
            # המתאמן עומד
            if not self.system_initialized:
                print("[SAFETY] User stabilized. Protection ACTIVE.")
            self.system_initialized = True
            self.was_low_in_last_frame = False
            self.reset_timers()
            return frame, False
        else:
            # המתאמן ירד נמוך
            self.was_low_in_last_frame = True
            if self.system_initialized:
                return self.handle_lying_state(frame, current_landmarks)
            
        return frame, False

    # ==========================================
    # הפונקציה הראשית שמנהלת את הכל
    # ==========================================
    def process_frame(self, frame, is_workout_active=False):
        if not is_workout_active:
            # איפוס מוחלט בתום האימון
            self.is_locked = False
            self.was_low_in_last_frame = False
            self.system_initialized = False 
            self.reset_timers()
            return frame, False
        
        # המרת תמונה ל-MediaPipe
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        detection_result = self.detector.detect(mp_image)
        
        # פיצול לוגי: יש או אין אדם בפריים
        if not detection_result.pose_landmarks:
            return self.handle_missing_user(frame)
        else:
            return self.handle_present_user(frame, detection_result)