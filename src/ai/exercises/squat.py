from src.ai.exercises.base_exercise import BaseExercise
from src.ai.angle_calculator import AngleCalculator
import numpy as np

class Squat(BaseExercise):
    """
    Rep-counting and form-checking logic for the squat exercise.
    """
    def __init__(self):
        super().__init__()
        self.feedback = ""
        self.has_welcomed = False
        self.error_frame_counter = 0

        self.target_goal = 0
        self.reps_left = "0"
        self.bonus_counter = 0
        self.goal_finished = False
        self.stage = None

    def set_target_goal(self, goal):
        """
        Sets a new rep goal for the session and resets all counters/feedback.
        """
        self.target_goal = goal
        self.reps_left = str(goal)
        self.counter = 0
        self.bonus_counter = 0
        self.goal_finished = False
        self.feedback = f"Goal: {goal} reps. Start!"
        self.has_welcomed = False

    def check(self, landmarks):
        """
        Analyzes the current frame's landmarks, updates rep count/feedback,
        and returns the current hip/knee angle and rep counter.
        """
        # Block initialization screen and maintain absolute silence
        if self.target_goal == 0:
            self.feedback = ""
            return 0, self.counter

        # Extract keypoints (shoulder, hip, knee, ankle)
        shoulder_lm = landmarks[12]
        hip_lm = landmarks[24]
        knee_lm = landmarks[26]
        ankle_lm = landmarks[28]

        # Safety check: ensure all required keypoints are visible in the frame
        if (shoulder_lm.visibility < 0.5 or
            hip_lm.visibility < 0.5 or
            knee_lm.visibility < 0.5 or
            ankle_lm.visibility < 0.5):

            self.error_frame_counter += 1
            if self.error_frame_counter > 10:
                self.feedback = "ERROR: Step back!"
            return 0, self.counter

        # Reset the error frame counter if the user is fully visible
        self.error_frame_counter = 0

        # Welcome the user once at the start of the exercise session
        if not self.has_welcomed:
            self.feedback = "Squat exercise initiated. Keep your back straight!"
            self.has_welcomed = True
            self.stage = 'up'  # assume the trainee starts the exercise standing
            return 0, self.counter

        # Convert landmarks to coordinate arrays
        hip = np.array([hip_lm.x, hip_lm.y])
        knee = np.array([knee_lm.x, knee_lm.y])
        ankle = np.array([ankle_lm.x, ankle_lm.y])

        # Calculate the knee/hip angle
        angle = AngleCalculator.calculate_angle(hip, knee, ankle)

        # Repetition counting and state machine tracking
        if angle > 160:
            if self.stage == 'down':
                self.stage = 'up'

                if self.target_goal > 0 and not self.goal_finished:
                    self.feedback = f"Good. {self.reps_left} left"
                else:
                    self.feedback = f"Plus {self.bonus_counter}"

        elif angle < 110 and self.stage == 'up':
            self.stage = 'down'
            self.counter += 1

            if self.target_goal > 0 and not self.goal_finished:
                current_left = int(self.reps_left) - 1
                self.reps_left = str(current_left)

                if current_left == 0:
                    self.goal_finished = True
                    self.feedback = "Bonus mode active!"
                    print("\n[LOG] Target goal reached! Switching to Bonus Mode.\n")
                else:
                    self.feedback = "Good rep!"
            else:
                # Bonus repetitions
                self.bonus_counter += 1
                self.reps_left = f"+{self.bonus_counter}"
                self.feedback = f"Plus {self.bonus_counter}"

            print(f"[LOG] Rep counted. Total: {self.counter}, Bonus: {self.bonus_counter}")

        elif 95 <= angle <= 160:
            if self.stage == 'up':
                self.feedback = "Go lower..."
            else:
                self.feedback = "Stand up..."

        return angle, self.counter

