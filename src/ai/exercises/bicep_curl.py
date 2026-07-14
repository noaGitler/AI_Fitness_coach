from src.ai.exercises.base_exercise import BaseExercise
from src.ai.angle_calculator import AngleCalculator
import numpy as np

class BicepCurl(BaseExercise):
    def __init__(self):
        super().__init__()
        self.feedback = "" 
        self.has_welcomed = False 
        self.error_frame_counter = 0
        
        self.target_goal = 0      
        self.reps_left = "0"      
        self.bonus_counter = 0    
        self.goal_finished = False 

        self.prev_elbow_y = None

    def set_target_goal(self, goal):
        self.target_goal = goal
        self.reps_left = str(goal)
        self.counter = 0
        self.bonus_counter = 0
        self.goal_finished = False
        self.feedback = f"Goal: {goal} reps. Start!"
        self.prev_elbow_y = None
        self.has_welcomed = False

    def check(self, landmarks):
        # חסימת מסך פתיחה ושמירה על שקט מוחלט
        if self.target_goal == 0:
            self.feedback = ""
            return 0, self.counter
            
        shoulder_lm = landmarks[11] # כתף עובדת
        other_shoulder_lm = landmarks[12] # כתף שנייה לבדיקת קו הגוף
        elbow_lm = landmarks[13]
        wrist_lm = landmarks[15]
        
        # 1. בדיקת נראות בסיסית וסלחנית
        if shoulder_lm.visibility < 0.4 or elbow_lm.visibility < 0.4 or wrist_lm.visibility < 0.4 or other_shoulder_lm.visibility < 0.4:
            self.feedback = "ERROR: Step back!"
            self.has_welcomed = False 
            return 0, self.counter

        # חישוב הזווית הנוכחית במרפק (כתף -> מרפק -> כף יד) - לצורך ספירת החזרות
        shoulder = [shoulder_lm.x, shoulder_lm.y]
        elbow = [elbow_lm.x, elbow_lm.y]
        wrist = [wrist_lm.x, wrist_lm.y]
        angle = AngleCalculator.calculate_angle(shoulder, elbow, wrist)

        # חישוב זווית פריסת הכתף הצידה (כתף שנייה -> כתף עובדת -> מרפק)
        other_shoulder = [other_shoulder_lm.x, other_shoulder_lm.y]
        shoulder_abduction_angle = AngleCalculator.calculate_angle(other_shoulder, shoulder, elbow)

        # 2. הגנה א': חסימת נפנוף זרוע אנכי (חוק גובה המרפק בציר Y)
        is_elbow_too_high = elbow_lm.y < (shoulder_lm.y + 0.03)

        # 3. הגנה ב' (הידוק חגורה קשוח): חסימת הרחקת הכתף הצידה (Shoulder Abduction)
        is_side_wings_cheat = shoulder_abduction_angle > 115

        if is_elbow_too_high or is_side_wings_cheat:
            self.error_frame_counter += 1
            if self.error_frame_counter > 5: 
                if is_side_wings_cheat:
                    self.feedback = "ERROR: Arms forward!" 
                else:
                    self.feedback = "ERROR: Keep elbow down!"
                self.stage = None 
                return angle, self.counter
        else:
            self.error_frame_counter = 0

        # 4. לוגיקת ספירה מהודקת ומבוקרת עם מנגנון הבונוס השקט והמשודרג
        if not self.has_welcomed:
            if angle > 125: 
                self.feedback = "Perfect. Start working!"
                self.has_welcomed = True
                self.stage = 'down'
            else:
                self.feedback = "Straighten your arms to start"
        else:
            if angle > 130: 
                self.stage = 'down'
                if self.target_goal > 0 and not self.goal_finished:
                    self.feedback = f"Good. {self.reps_left} left"
                else:
                    # עדכון שקט: מציג את מספר הבונוס הנוכחי בירידה בלי לחפור קולית מחדש
                    self.feedback = f"Plus {self.bonus_counter}"
                
            elif angle < 52 and self.stage == 'down': 
                self.stage = 'up'
                self.counter += 1
                
                if self.target_goal > 0 and not self.goal_finished:
                    current_left = int(self.reps_left) - 1
                    self.reps_left = str(current_left)
                    
                    if current_left == 0:
                        self.goal_finished = True
                        # פעם אחת בלבד מפעיל את ההכרזה החגיגית על מעבר למצב בונוס!
                        self.feedback = "Bonus mode active!"
                        print("\n[LOG] Target goal reached! Switching to Bonus Mode.\n")
                    else:
                        self.feedback = "Good rep!"
                else:
                    # חזרות הבונוס הבאות: אומרת קצר וקולע רק את המספר, למשל "Plus 2", "Plus 3"
                    self.bonus_counter += 1
                    self.reps_left = f"+{self.bonus_counter}"
                    self.feedback = f"Plus {self.bonus_counter}"
                
                print(f"[LOG] Rep counted. Total: {self.counter}, Bonus: {self.bonus_counter}")
                
            elif angle > 52 and angle < 130:
                if self.stage == 'down':
                    self.feedback = "Lift up..."
                else:
                    self.feedback = "Lower down..."
                
        return angle, self.counter

