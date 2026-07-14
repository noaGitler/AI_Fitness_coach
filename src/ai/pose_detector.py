
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class PoseDetector:
    def __init__(self):
        print("[AI] Initializing Modern MediaPipe Landmarker...")
        model_path = 'pose_landmarker_full.task'
        options = vision.PoseLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.IMAGE
        )
        self.detector = vision.PoseLandmarker.create_from_options(options)
        self.worker_ref = None # רפרנס לחוט הוידאו לצורך שידור סיגנלים ותקשורת
        print("[AI] Modern Core Engine Ready.")

    def process(self, frame, exercise=None):
        if exercise is None:
            return frame

        h, w, _ = frame.shape
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        detection_result = self.detector.detect(mp_image)
        
        current_angle = 0
        feedback_text = ""
        skeleton_layer = frame.copy()

        if exercise is not None:
            feedback_text = exercise.feedback

        if detection_result.pose_landmarks:
            for landmark_list in detection_result.pose_landmarks:
                if exercise is not None:
                    # 🛡️ שילוב פרוטוקול הבטיחות והחירום שלכן:
                    is_paused = False
                    
                    # בדיקה בטוחה של הסטטוס דרך ה-worker המקושר לחלון הראשי
                    if self.worker_ref is not None and hasattr(self.worker_ref, 'main_window_ref') and self.worker_ref.main_window_ref is not None:
                        main_win = self.worker_ref.main_window_ref
                        
                        # גישה למנהל הסשן (SessionManager) כדי לבדוק Pause או Countdown אקטיבי
                        if hasattr(main_win, 'session_manager') and main_win.session_manager is not None:
                            sm = main_win.session_manager
                            if sm.is_paused or not sm.is_workout_active:
                                is_paused = True

                    # הפעלת לוגיקת תצוגת החירום / ההכנה בהתאם לפרוטוקול שלכן
                    if is_paused:
                        if self.worker_ref and self.worker_ref.main_window_ref and self.worker_ref.main_window_ref.session_manager.is_paused:
                            feedback_text = "SESSION PAUSED"
                        else:
                            feedback_text = "GET READY!"
                        current_angle = 0
                    else:
                        # רק כשהכל תקין והאימון רץ אקטיבית - סופרים חזרות ומחשבים זווית ביו-מכנית
                        angle, reps = exercise.check(landmark_list)
                        feedback_text = exercise.feedback
                        current_angle = angle
                
                # עיצוב UI/UX חכם: אדום לשגיאה/אזהרה, תכלת/ירוק לתנועה תקינה
                # קובעים צבע ברירת מחדל (ירוק/צהבהב: 200, 255, 0)
                color = (200, 255, 0) 
                
                # לוגיקה מקצועית: האם התרגיל מדווח על בעיית יציבה?
                if exercise is not None and hasattr(exercise, 'is_posture_bad') and exercise.is_posture_bad:
                    color = (0, 0, 255) # אדום בוהק!
                elif feedback_text and "ERROR" in feedback_text:
                    color = (0, 0, 255) # אדום גם אם הפידבק מכיל את המילה ERROR

                joints = {}
                for idx, lm in enumerate(landmark_list):
                    if lm.visibility >= 0.5:
                        joints[idx] = (int(lm.x * w), int(lm.y * h))

                connections = [
                    (11, 12), (11, 23), (12, 24), (23, 24),
                    (11, 13), (13, 15), (12, 14), (14, 16),
                    (23, 25), (25, 27), (24, 26), (26, 28)
                ]

                for start_idx, end_idx in connections:
                    if start_idx in joints and end_idx in joints:
                        cv2.line(skeleton_layer, joints[start_idx], joints[end_idx], color, 24)

                for idx in joints:
                    if idx in [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]:
                        cv2.circle(skeleton_layer, joints[idx], 18, color, cv2.FILLED)
                        cv2.circle(skeleton_layer, joints[idx], 8, (255, 255, 255), cv2.FILLED)

                alpha = 0.70
                frame = cv2.addWeighted(skeleton_layer, 1 - alpha, frame, alpha, 0)
        else:
            if exercise is not None and exercise.target_goal > 0:
                exercise.feedback = "ERROR: Step back!"
                feedback_text = exercise.feedback

        # שידור המדדים בצורה אסינכרונית בטוחה לחלון הראשי ללא חסימת ה-GUI
        if self.worker_ref is not None:
            self.worker_ref.metrics_ready.emit(current_angle, feedback_text)
        
        if exercise is not None and self.worker_ref is not None:
            # משדרים את הזווית העדכנית ואת מחרוזת הפידבק שנבנתה בתרגיל
            self.worker_ref.metrics_ready.emit(float(current_angle), str(feedback_text))
            
        return frame