from PyQt6.QtCore import QObject, QTimer, pyqtSignal

class TimerManager(QObject):
    """
    The application's official session timer manager (SOLID - Single Responsibility Principle).
    Drives the workout countdown, matching the original MainWindow logic.
    """
    # Signals for updating the GUI and the rest of the system
    time_updated = pyqtSignal(int)          # emits the remaining seconds
    timeout_triggered = pyqtSignal()        # fires the moment time runs out
    pause_state_changed = pyqtSignal(bool)  # emits whether the workout is currently frozen

    def __init__(self):
        super().__init__()
        self.session_time_left = 0
        self.is_paused = False
        
        # The underlying QTimer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._handle_tick)

    def start_workout(self, time_limit_seconds):
        """Initializes and starts the workout countdown based on the specified time limit"""
        self.session_time_left = time_limit_seconds
        self.is_paused = False
        self.timer.start(1000) # Tick every second (1000 milliseconds)
        self.time_updated.emit(self.session_time_left)
        self.pause_state_changed.emit(self.is_paused)
        print(f"[TIMER] Countdown started for {self.session_time_left} seconds.")

    def toggle_pause(self):
        """Toggles the pause state of the timer"""
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.timer.stop()
            print("[TIMER] Workout countdown frozen.")
        else:
            self.timer.start(1000)
            print("[TIMER] Workout countdown resumed.")
            
        self.pause_state_changed.emit(self.is_paused)
        return self.is_paused

    def stop_workout(self):
        """Stops the timer completely and resets the state"""
        self.timer.stop()
        self.is_paused = False
        print(f"[TIMER] Workout countdown stopped safely. Remaining time was: {self.session_time_left}s")
        return self.session_time_left

    def _handle_tick(self):
        """Internal function that manages the timer ticks and decrements seconds"""
        if self.is_paused:
            return

        self.session_time_left -= 1
        self.time_updated.emit(self.session_time_left)
        
        if self.session_time_left <= 0:
            self.timer.stop()
            print("[TIMER] Countdown expired! Triggering timeout event.")
            self.timeout_triggered.emit()