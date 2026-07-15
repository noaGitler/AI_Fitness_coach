from src.ai.exercises.base_exercise import BaseExercise
from src.ai.angle_calculator import AngleCalculator
import numpy as np

class Squat(BaseExercise):
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
        self.target_goal = goal
        self.reps_left = str(goal)
        self.counter = 0
        self.bonus_counter = 0
        self.goal_finished = False
        self.feedback = f"Goal: {goal} reps. Start!"
        self.has_welcomed = False

    def check(self, landmarks):
        # חסימת מסך פתיחה ושמירה על שקט מוחלט
        if self.target_goal == 0:
            self.feedback = ""
            return 0, self.counter

        # חילוץ נקודות מפתח (כתף, אגן, ברך, קרסול)
        shoulder_lm = landmarks[12] 
        hip_lm = landmarks[24]
        knee_lm = landmarks[26]
        ankle_lm = landmarks[28]

        # --- הוספת מנגנון אימות זווית צילום (צדדי) ---
        # השוואת עומק הכתף והירך כדי לוודא עמידה מהצד
        # אם הכתף והירך באותו מישור עומק (x דומה), זה אומר שהמתאמן עומד נכון
        is_side_view = abs(shoulder_lm.x - hip_lm.x) < 0.25

        if not is_side_view:
            self.feedback = "Please stand sideways!"
            return 0, self.counter # לא מחשיבים תנועה אם הזווית לא נכונה

        # 1. בדיקת נראות בסיסית וסלחנית
        if shoulder_lm.visibility < 0.4 or hip_lm.visibility < 0.4 or knee_lm.visibility < 0.4 or ankle_lm.visibility < 0.4:
            self.feedback = "ERROR: Step back!"
            self.has_welcomed = False 
            return 0, self.counter

        # המרת הקואורדינטות לצורך חישוב
        shoulder = [shoulder_lm.x, shoulder_lm.y]
        hip = [hip_lm.x, hip_lm.y]
        knee = [knee_lm.x, knee_lm.y]
        ankle = [ankle_lm.x, ankle_lm.y]

        # חישוב זווית הברך (לספירת הסקוואט)
        angle = AngleCalculator.calculate_angle(hip, knee, ankle)
        print(f"[DEBUG] Squat Angle: {angle}, Stage: {self.stage}") # תוסיפי את זה!
        
        # חישוב זווית הגב/האגן (כדי לוודא שהוא לא מתכופף מדי קדימה)
        back_angle = AngleCalculator.calculate_angle(shoulder, hip, knee)

        # 2. הגנת יציבה: חסימת כיפוף גב מסוכן
        is_back_too_bent = back_angle < 50

        if is_back_too_bent:
            self.error_frame_counter += 1
            if self.error_frame_counter > 5: 
                self.feedback = "ERROR: Keep back straight!"
                self.stage = None 
                return angle, self.counter
        else:
            self.error_frame_counter = 0

        # 3. לוגיקת ספירה מהודקת ומבוקרת עם מנגנון הבונוס
        if not self.has_welcomed:
            if angle > 160: # המתאמן עומד זקוף ומוכן
                self.feedback = "Perfect. Start working!"
                self.has_welcomed = True
                self.stage = 'up'
            else:
                self.feedback = "Stand up straight to start"
        else:
            if angle > 160: 
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
                    # חזרות בונוס
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
    