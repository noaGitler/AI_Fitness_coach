from src.ai.exercises.base_exercise import BaseExercise
from src.ai.angle_calculator import AngleCalculator
import numpy as np

class StandingKneeExtension(BaseExercise):
    """
    Rep-counting and form-checking logic for the standing knee extension
    exercise (leg lifted to passé, then kicked forward).
    """
    def __init__(self):
        super().__init__()
        self.feedback = "Stand in profile to the camera." 
        self.has_welcomed = False 
        
        self.target_goal = 0      
        self.reps_left = "0"      
        self.goal_finished = False 
        
        self.stage = 'START' 
        
        # Frame counters used to smooth out noisy on-screen posture warnings
        self.leg_error_frames = 0
        self.back_error_frames = 0
        self.front_facing_frames = 0
        
        # Voting filter that stabilizes which side (left/right) profile is detected
        self.profile_voting = 0
        self.detected_profile = None 
        
        # Tracks whether the current rep should count
        self.current_rep_invalid = False
        self.is_posture_bad = False

    def set_target_goal(self, goal):
        self.target_goal = goal
        self.reps_left = str(goal)
        self.counter = 0
        self.goal_finished = False
        self.feedback = f"Goal: {goal} reps. Stand in profile and lift to Passé!"
        self.stage = 'START'
        self.has_welcomed = False
        self.current_rep_invalid = False
        self.profile_voting = 0
        self.detected_profile = None  
        self.is_posture_bad = False
        
        # Reset frame counters for the new session
        self.leg_error_frames = 0
        self.back_error_frames = 0
        self.front_facing_frames = 0

    def check(self, landmarks):
        if self.target_goal == 0:
            self.feedback = ""
            return 0, self.counter
            
        try:
            left_shoulder_z = landmarks[11].z
            right_shoulder_z = landmarks[12].z
            
            
            if self.stage == 'START':
                if left_shoulder_z < right_shoulder_z:
                    self.profile_voting = min(15, self.profile_voting + 1)
                else:
                    self.profile_voting = max(-15, self.profile_voting - 1)
                
                if self.profile_voting >= 5:
                    self.detected_profile = 'LEFT'
                elif self.profile_voting <= -5:
                    self.detected_profile = 'RIGHT'
                else:
                    if self.detected_profile is None:
                        self.detected_profile = 'LEFT' if left_shoulder_z < right_shoulder_z else 'RIGHT'
            
            # Pick the biomechanical landmarks according to the detected profile
            if self.detected_profile == 'LEFT':
                shoulder_w = [landmarks[11].x, landmarks[11].y]
                hip_w = [landmarks[23].x, landmarks[23].y]
                knee_w = [landmarks[25].x, landmarks[25].y]
                ankle_w = [landmarks[27].x, landmarks[27].y]
                
                hip_s = [landmarks[24].x, landmarks[24].y]
                knee_s = [landmarks[26].x, landmarks[26].y]
                ankle_s = [landmarks[28].x, landmarks[28].y]
            else:
                shoulder_w = [landmarks[12].x, landmarks[12].y]
                hip_w = [landmarks[24].x, landmarks[24].y]
                knee_w = [landmarks[26].x, landmarks[26].y]
                ankle_w = [landmarks[28].x, landmarks[28].y]
                
                hip_s = [landmarks[23].x, landmarks[23].y]
                knee_s = [landmarks[25].x, landmarks[25].y]
                ankle_s = [landmarks[27].x, landmarks[27].y]
            
            hip_angle = AngleCalculator.calculate_angle(shoulder_w, hip_w, knee_w)
            working_knee_angle = AngleCalculator.calculate_angle(hip_w, knee_w, ankle_w)
            standing_knee_angle = AngleCalculator.calculate_angle(hip_s, knee_s, ankle_s)
            
            # Posture calibration thresholds (tuned to avoid falsely flagging bad
            # posture during the starting stance)            
            back_straight = abs(shoulder_w[0] - hip_w[0]) < 0.18  
            facing_camera = abs(landmarks[11].x - landmarks[12].x) > 0.22 
            
        except Exception as e:
            self.feedback = "Ensure your full body is visible."
            self.is_posture_bad = True
            return 0, self.counter

        posture_warning = ""
        is_bad_now = False

        # Facing the camera vs. profile check
        if facing_camera:
            self.front_facing_frames += 1
            if self.front_facing_frames >= 4 and self.stage in ['PASSE', 'EXTENDED']:
                self.current_rep_invalid = True
            if self.front_facing_frames >= 8:
                posture_warning = "⚠️ Turn to the side! Profile only."
                is_bad_now = True
        else:
            self.front_facing_frames = max(0, self.front_facing_frames - 1)

        # Straight back check
        if not back_straight:
            self.back_error_frames += 1
            if self.back_error_frames >= 4 and self.stage in ['PASSE', 'EXTENDED']:
                self.current_rep_invalid = True
            if self.back_error_frames >= 8:
                posture_warning = "⚠️ Keep your back straight!"
                is_bad_now = True
        else:
            self.back_error_frames = max(0, self.back_error_frames - 1)

        # Standing leg lock check (fully disabled during the static starting stance)
        if self.stage != 'START' and standing_knee_angle < 145:
            self.leg_error_frames += 1
            if self.leg_error_frames >= 4 and self.stage in ['PASSE', 'EXTENDED']:
                self.current_rep_invalid = True
            if self.leg_error_frames >= 8:
                posture_warning = "⚠️ Straighten your standing leg!"
                is_bad_now = True
        else:
            self.leg_error_frames = max(0, self.leg_error_frames - 1)

        self.is_posture_bad = is_bad_now

        # Main rep state machine
        
        if self.stage in ['PASSE', 'EXTENDED'] and hip_angle > 145 and working_knee_angle > 145:
            self.stage = 'START'
            self.current_rep_invalid = False
            self.leg_error_frames = 0
            self.back_error_frames = 0
            self.front_facing_frames = 0
            self.feedback = "Rep reset. Stand straight."
            return working_knee_angle, self.counter

        if self.stage == 'START':
            if is_bad_now:
                self.feedback = posture_warning
            else:
                self.feedback = "Good posture. Lift to Passé!"
            
            if hip_angle < 130 and working_knee_angle < 115:
                self.stage = 'PASSE'
                self.current_rep_invalid = False 

        elif self.stage == 'PASSE':
            if is_bad_now:
                self.feedback = posture_warning
            else:
                self.feedback = "Kick forward until straight!"
            
            if working_knee_angle >= 135 and hip_angle <= 135:
                self.stage = 'EXTENDED'
                self.feedback = "Brilliant extension! Hold it..."

        elif self.stage == 'EXTENDED':
            if is_bad_now:
                self.feedback = posture_warning
            else:
                self.feedback = "Now bend the knee back."
            
            if working_knee_angle < 120 and hip_angle <= 135:
                self.stage = 'RETRACTED'
                self.feedback = "Nice control! Now lower smoothly."

        elif self.stage == 'RETRACTED':
            if is_bad_now:
                self.feedback = posture_warning
            else:
                self.feedback = "Lower your leg completely to finish."
            
            # Detect the movement is fully done (leg is back down and straight)
            if hip_angle > 145 and working_knee_angle > 145:
                if self.current_rep_invalid:
                    # Bad form or a rushed rep with a bent back/standing leg mid-air

                    self.feedback = "❌ Rep NOT counted! Keep back and standing leg straight."
                    self.stage = 'START'
                    self.current_rep_invalid = False
                else:
                    self.counter += 1
                    self.stage = 'START'
                    
                    left = self.target_goal - self.counter
                    if left <= 0:
                        self.reps_left = "0"
                        self.goal_finished = True
                        self.feedback = "Workout Goal Achieved! Phenomenal job!"
                    else:
                        self.reps_left = str(left)
                        self.feedback = f"Perfect rep! {left} remaining."
                
                # Reset the frame counters for the next rep
                self.leg_error_frames = 0
                self.back_error_frames = 0
                self.front_facing_frames = 0

        return working_knee_angle, self.counter



