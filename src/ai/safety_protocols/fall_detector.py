import cv2
import time 
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class FallDetector:
    """
    Safety component: detects falls/lying-on-the-floor states from pose
    landmarks and drives the emergency SOS countdown.
    """
    def __init__(self):
        print("[SAFETY] Initializing Emergency Fall Detector...")
        model_path = 'pose_landmarker_full.task'
        options = vision.PoseLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=model_path), 
            running_mode=vision.RunningMode.IMAGE
        )
        self.detector = vision.PoseLandmarker.create_from_options(options)
        
        # Core state variables
        self.is_locked = False 
        self.system_initialized = False 
        self.was_low_in_last_frame = False 
        self.fall_start_time = None
        self.pending_speech = None

        # "Dead-man" logic state (detecting movement while lying down)
        self.inactivity_timer_start = None
        self.prev_landmarks = None

    # Timer / state helper functions
    def reset_timers(self):
        self.inactivity_timer_start = None
        self.fall_start_time = None

    def lock_system(self):
        self.is_locked = True
        self.reset_timers()
        self.system_initialized = False 
        print("[ALERT] Emergency protocol activated - LOCKING SYSTEM")

    def safe_lock_system(self):
        self.is_locked = True
        self.reset_timers()
        self.system_initialized = False 
        print("[SAFETY] Vital signs confirmed. Workout paused. Please stand up to resume.")


    # Functions handling the trainee's state
    def handle_missing_user(self, frame):
        if not self.system_initialized:
            cv2.putText(frame, "Waiting for user to enter...", (30, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
            return frame, False
            
        # If the system was initialized and the user disappeared after being low - fall risk!
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
        """Helper: calculates the max distance moved from the saved reference pose (the pose on the floor)."""
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
        """Helper function to handle the lying state - including inactivity timer to prevent false fall detections"""
        if self.inactivity_timer_start is None:
            self.inactivity_timer_start = time.time()
            self.prev_landmarks = current_landmarks 
            
        elapsed = time.time() - self.inactivity_timer_start
        
        dist = self.calculate_max_distance(current_landmarks, self.prev_landmarks)
        
        if elapsed < 2.0:
            # During the first 2 seconds after the hip dropped low, the trainee may
            # still be falling/settling. So we keep updating the reference pose and
            # don't look for signs of life yet.
            self.prev_landmarks = current_landmarks
        else:
            if dist > 0.05:
                print(f"[DEBUG] Vital signs detected! (Moved: {dist:.3f}). Entering Safe-Lock.")
                self.safe_lock_system()
                return frame, False
                
        if elapsed >= 10.0:  
            self.lock_system()
            return frame, True
            
        cv2.putText(frame, f"SOS in: {10.0 - elapsed:.1f}s", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
        return frame, False

    def handle_present_user(self, frame, detection_result):
        landmarks_list = detection_result.pose_landmarks[0]
        current_landmarks = landmarks_list.landmark if hasattr(landmarks_list, 'landmark') else landmarks_list
        
        if not self.is_partially_visible(current_landmarks):
            return self.handle_missing_user(frame)
        
        left_hip = current_landmarks[23]
        right_hip = current_landmarks[24]


        if left_hip.visibility < 0.5 or right_hip.visibility < 0.5:
            cv2.putText(frame, "Adjust camera: Need full body for tracking", (30, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            self.reset_timers()
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
            # Trainee is standing
            if not self.system_initialized:
                print("[SAFETY] User stabilized. Protection ACTIVE.")
            self.system_initialized = True
            self.was_low_in_last_frame = False
            self.reset_timers()
            return frame, False
        else:
            # Trainee dropped low
            self.was_low_in_last_frame = True
            if self.system_initialized:
                return self.handle_lying_state(frame, current_landmarks)
            
        return frame, False

    def is_partially_visible(self, landmarks):
        """Checks if at least part of the body is visible (head or shoulders)"""
        # Nose (0), Left Shoulder (11), Right Shoulder (12)
        # Check if at least one of these points is clearly visible
        return (landmarks[0].visibility > 0.5 or 
                landmarks[11].visibility > 0.5 or 
                landmarks[12].visibility > 0.5)
    

    # The main function that manages everything
    def process_frame(self, frame, is_workout_active=False):
        if not is_workout_active:
            self.is_locked = False
            self.was_low_in_last_frame = False
            self.system_initialized = False 
            self.reset_timers()
            return frame, False
        
        # Convert the image for MediaPipe
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        detection_result = self.detector.detect(mp_image)
        
        # Logical split: there is or is not a person in the frame
        if not detection_result.pose_landmarks:
            return self.handle_missing_user(frame)
        else:
            return self.handle_present_user(frame, detection_result)