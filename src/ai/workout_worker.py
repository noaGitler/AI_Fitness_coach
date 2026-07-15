import cv2
from PyQt6.QtCore import QThread, pyqtSignal

class VideoWorker(QThread):
    """A dedicated background thread that reads from the camera and runs the
    AI pipeline, so the GUI never freezes."""
    frame_ready = pyqtSignal(object) 
    metrics_ready = pyqtSignal(float, str) 
    
    # Emergency protocol signals
    sos_countdown_started = pyqtSignal()
    emergency_detected = pyqtSignal(str)
    emergency_trigger = pyqtSignal()

    def __init__(self):
        super().__init__()
        from src.ai.pose_detector import PoseDetector
        from src.ai.safety_protocols.fall_detector import FallDetector
        
        self.detector = PoseDetector()
        self.detector.worker_ref = self 
        self.fall_detector = FallDetector() # initialize the safety component
        
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
                    # Run the safety/emergency protocol
                    frame, alarm_triggered = self.fall_detector.process_frame(
                        frame, is_workout_active=self.current_exercise is not None
                    )

                    # Speak the initial warning, if one was created
                    if getattr(self.fall_detector, 'pending_speech', None):
                        self.sos_countdown_started.emit()
                        self.fall_detector.pending_speech = None

                    # Check the Pause state in the main window
                    is_paused_now = False
                    if self.main_window_ref and hasattr(self.main_window_ref, 'session_manager'):
                        is_paused_now = self.main_window_ref.session_manager.is_paused

                    # Run the AI (rep counting + skeleton drawing) - only once!
                    if not is_paused_now and not self.fall_detector.was_low_in_last_frame and not alarm_triggered:
                        frame = self.detector.process(frame, exercise=self.current_exercise)
                    elif is_paused_now:
                        self.metrics_ready.emit(0.0, "")

                    # Trigger the final emergency alarm once the 10-second timer has elapsed
                    if alarm_triggered:
                        self.emergency_detected.emit("Fall detected!")
                        self.emergency_trigger.emit()

                    # Single, synchronized frame emit to the GUI (avoids double updates)
                    self.frame_ready.emit(frame)
            
            # Fixed sleep to keep the CPU calm
            self.msleep(20) 
                
        if self.cap and self.cap.isOpened():
            self.cap.release()
        print("[THREAD] Background camera thread stopped safely.")

    def stop(self):
        self.running = False
        self.wait()