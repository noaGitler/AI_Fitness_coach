from src.ai.exercises.base_exercise import BaseExercise
from src.ai.angle_calculator import AngleCalculator
import numpy as np

class StandingKneeExtension(BaseExercise):
    def __init__(self):
        super().__init__()
        self.feedback = "Stand in profile to the camera." 
        self.has_welcomed = False 
        
        self.target_goal = 0      
        self.reps_left = "0"      
        self.goal_finished = False 
        
        self.stage = 'START' 
        
        # מונים לסינון רעשים ויזואליים על המסך (Smoothing Filters)
        self.leg_error_frames = 0
        self.back_error_frames = 0
        self.front_facing_frames = 0
        
        # פילטר הצבעה לייצוב זיהוי הפרופיל במצב סטטי
        self.profile_voting = 0
        self.detected_profile = None 
        
        # ניהול חוקיות החזרה
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
        
        # איפוס מונים בהתחלה חדשה
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
            
            # =====================================================================
            # 🔒 מנגנון הצבעה דינמי ומיוצב לפרופיל (Profile Voting Filter)
            # =====================================================================
            if self.stage == 'START':
                # בדיקה חלקה בזמן עמידת מוצא למניעת נעילת שווא בגלל פריים בודד רועש
                if left_shoulder_z < right_shoulder_z:
                    self.profile_voting = min(15, self.profile_voting + 1)
                else:
                    self.profile_voting = max(-15, self.profile_voting - 1)
                
                # קביעת הפרופיל על בסיס מגמה יציבה
                if self.profile_voting >= 5:
                    self.detected_profile = 'LEFT'
                elif self.profile_voting <= -5:
                    self.detected_profile = 'RIGHT'
                else:
                    if self.detected_profile is None:
                        self.detected_profile = 'LEFT' if left_shoulder_z < right_shoulder_z else 'RIGHT'
            
            # שליפת נקודות ציון ביו-מכניות על פי הפרופיל הנבחר
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
            
            # חישוב זוויות התנועה המדויקות
            hip_angle = AngleCalculator.calculate_angle(shoulder_w, hip_w, knee_w)
            working_knee_angle = AngleCalculator.calculate_angle(hip_w, knee_w, ankle_w)
            standing_knee_angle = AngleCalculator.calculate_angle(hip_s, knee_s, ankle_s)
            
            # מדדי כיול יציבה (טווח מאוזן שמונע הדלקת שלד אדום שגוי במוצא)
            back_straight = abs(shoulder_w[0] - hip_w[0]) < 0.18  
            facing_camera = abs(landmarks[11].x - landmarks[12].x) > 0.22 
            
        except Exception as e:
            self.feedback = "Ensure your full body is visible."
            self.is_posture_bad = True
            return 0, self.counter

        # =====================================================================
        # 🚨 מערכת אבחון חכמה: הגנה מבוססת 4 פריימים לפסילה ו-8 פריימים למסך
        # =====================================================================
        posture_warning = ""
        is_bad_now = False

        # 1. בקרת פנים לחזית / פרופיל
        if facing_camera:
            self.front_facing_frames += 1
            if self.front_facing_frames >= 4 and self.stage in ['PASSE', 'EXTENDED']:
                self.current_rep_invalid = True
            if self.front_facing_frames >= 8:
                posture_warning = "⚠️ Turn to the side! Profile only."
                is_bad_now = True
        else:
            self.front_facing_frames = max(0, self.front_facing_frames - 1)

        # 2. בקרת שמירה על גב ישר
        if not back_straight:
            self.back_error_frames += 1
            if self.back_error_frames >= 4 and self.stage in ['PASSE', 'EXTENDED']:
                self.current_rep_invalid = True
            if self.back_error_frames >= 8:
                posture_warning = "⚠️ Keep your back straight!"
                is_bad_now = True
        else:
            self.back_error_frames = max(0, self.back_error_frames - 1)

        # 3. בקרת נעילת רגל עמידה (מנוטרלת לחלוטין במצב מוצא סטטי)
        if self.stage != 'START' and standing_knee_angle < 145:
            self.leg_error_frames += 1
            if self.leg_error_frames >= 4 and self.stage in ['PASSE', 'EXTENDED']:
                self.current_rep_invalid = True
            if self.leg_error_frames >= 8:
                posture_warning = "⚠️ Straighten your standing leg!"
                is_bad_now = True
        else:
            self.leg_error_frames = max(0, self.leg_error_frames - 1)

        # עדכון משתנה צבע השלד הגרפי (מנורמל וחסין הבהובים)
        self.is_posture_bad = is_bad_now

        # =====================================================================
        # 🔄 מכונת המצבים הראשית (Finite State Machine)
        # =====================================================================
        
        # מנגנון ביטול חזרה באמצע: אם המשתמש הוריד רגל לגמרי באמצע, מאפסים בצורה חלקה
        if self.stage in ['PASSE', 'EXTENDED'] and hip_angle > 145 and working_knee_angle > 145:
            self.stage = 'START'
            self.current_rep_invalid = False
            self.leg_error_frames = 0
            self.back_error_frames = 0
            self.front_facing_frames = 0
            self.feedback = "Rep reset. Stand straight."
            return working_knee_angle, self.counter

        # מצב 0: START - המתנה לעמידת מוצא תקינה ותחילת הרמה
        if self.stage == 'START':
            if is_bad_now:
                self.feedback = posture_warning
            else:
                self.feedback = "Good posture. Lift to Passé!"
            
            # כניסה לפסה (Passé) - דורש קיפול ברך והרמת ירך
            if hip_angle < 130 and working_knee_angle < 115:
                self.stage = 'PASSE'
                self.current_rep_invalid = False 

        # מצב 1: PASSE - הרגל מקופלת באוויר, מחכים ליישור
        elif self.stage == 'PASSE':
            if is_bad_now:
                self.feedback = posture_warning
            else:
                self.feedback = "Kick forward until straight!"
            
            if working_knee_angle >= 135 and hip_angle <= 135:
                self.stage = 'EXTENDED'
                self.feedback = "Brilliant extension! Hold it..."

        # מצב 2: EXTENDED - הרגל ישרה קדימה, מחכים לקיפול חזרה
        elif self.stage == 'EXTENDED':
            if is_bad_now:
                self.feedback = posture_warning
            else:
                self.feedback = "Now bend the knee back."
            
            if working_knee_angle < 120 and hip_angle <= 135:
                self.stage = 'RETRACTED'
                self.feedback = "Nice control! Now lower smoothly."

        # מצב 3: RETRACTED - שלב הורדת הרגל חזרה לרצפה (שלב סלחני לרעידות מאמץ)
        elif self.stage == 'RETRACTED':
            if is_bad_now:
                self.feedback = posture_warning
            else:
                self.feedback = "Lower your leg completely to finish."
            
            # זיהוי סיום תנועה מוחלט (הרגל נחתכה וישרה על הקרקע)
            if hip_angle > 145 and working_knee_angle > 145:
                if self.current_rep_invalid:
                    # המערכת תפסה ביצוע שגוי או מהיר מדי עם גב/רגל עקומה באוויר
                    self.feedback = "❌ Rep NOT counted! Keep back and standing leg straight."
                    self.stage = 'START'
                    self.current_rep_invalid = False
                else:
                    # ביצוע מושלם! ספירת חזרה ועדכון מדדים
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
                
                # איפוס מונים בסיום החזרה לקראת החזרה הבאה
                self.leg_error_frames = 0
                self.back_error_frames = 0
                self.front_facing_frames = 0

        return working_knee_angle, self.counter







# from src.ai.exercises.base_exercise import BaseExercise
# from src.ai.angle_calculator import AngleCalculator
# import numpy as np

# class StandingKneeExtension(BaseExercise):
#     def __init__(self):
#         super().__init__()
#         self.feedback = "Stand in profile to the camera." 
#         self.has_welcomed = False 
        
#         self.target_goal = 0      
#         self.reps_left = "0"      
#         self.goal_finished = False 
        
#         self.stage = 'START' 
        
#         # מוני פריימים לסינון רעשים (Smoothing)
#         self.leg_error_frames = 0
#         self.back_error_frames = 0
#         self.front_facing_frames = 0
        
#         # 🔥 משתנה המשדר החוצה אם השלד צריך להיות צבוע באדום
#         self.is_posture_bad = False

#     def set_target_goal(self, goal):
#         self.target_goal = goal
#         self.reps_left = str(goal)
#         self.counter = 0
#         self.goal_finished = False
#         self.feedback = f"Goal: {goal} reps. Stand in profile and lift to Passé!"
#         self.stage = 'START'
#         self.has_welcomed = False
#         self.is_posture_bad = False

#     def check(self, landmarks):
#         if self.target_goal == 0:
#             self.feedback = ""
#             return 0, self.counter
            
#         try:
#             # ==========================================
#             # 1. זיהוי דינמי של הצד (פרופיל ימין או שמאל)
#             # ==========================================
#             left_shoulder_z = landmarks[11].z
#             right_shoulder_z = landmarks[12].z
            
#             if left_shoulder_z < right_shoulder_z:
#                 # פרופיל שמאלי
#                 shoulder_w = [landmarks[11].x, landmarks[11].y]
#                 hip_w = [landmarks[23].x, landmarks[23].y]
#                 knee_w = [landmarks[25].x, landmarks[25].y]
#                 ankle_w = [landmarks[27].x, landmarks[27].y]
                
#                 hip_s = [landmarks[24].x, landmarks[24].y]
#                 knee_s = [landmarks[26].x, landmarks[26].y]
#                 ankle_s = [landmarks[28].x, landmarks[28].y]
#             else:
#                 # פרופיל ימני
#                 shoulder_w = [landmarks[12].x, landmarks[12].y]
#                 hip_w = [landmarks[24].x, landmarks[24].y]
#                 knee_w = [landmarks[26].x, landmarks[26].y]
#                 ankle_w = [landmarks[28].x, landmarks[28].y]
                
#                 hip_s = [landmarks[23].x, landmarks[23].y]
#                 knee_s = [landmarks[25].x, landmarks[25].y]
#                 ankle_s = [landmarks[27].x, landmarks[27].y]
            
#             # חישובי זוויות ביו-מכניות
#             hip_angle = AngleCalculator.calculate_angle(shoulder_w, hip_w, knee_w)
#             working_knee_angle = AngleCalculator.calculate_angle(hip_w, knee_w, ankle_w)
#             standing_knee_angle = AngleCalculator.calculate_angle(hip_s, knee_s, ankle_s)
            
#             # כיול רגישות מדדים (הפיכת הרף ליותר סלחני ומתאים לתנאי תאורה ביתיים)
#             back_straight = abs(shoulder_w[0] - hip_w[0]) < 0.16  # הורחב מ-0.12 ל-0.16
#             facing_camera = abs(landmarks[11].x - landmarks[12].x) > 0.24 # הורחב מ-0.18 ל-0.24
            
#         except Exception as e:
#             self.feedback = "Ensure your full body is visible."
#             self.is_posture_bad = True
#             return 0, self.counter

#         # =====================================================================
#         # 🚨 מערכת אבחון יציבה חכמה וסלחנית (מבוססת סינון רעשי מצלמה)
#         # =====================================================================
#         posture_warning = ""
#         is_bad_now = False

#         # 1. בדיקת חזית/פרופיל
#         if facing_camera:
#             self.front_facing_frames += 1
#             if self.front_facing_frames > 8: # דורש חצי שנייה של טעות לפני שצועק
#                 posture_warning = "⚠️ Turn to the side! Profile only."
#                 is_bad_now = True
#         else:
#             self.front_facing_frames = max(0, self.front_facing_frames - 1)

#         # 2. בדיקת גב עקום
#         if not back_straight and not is_bad_now:
#             self.back_error_frames += 1
#             if self.back_error_frames > 8: 
#                 posture_warning = "⚠️ Keep your back straight!"
#                 is_bad_now = True
#         else:
#             self.back_error_frames = max(0, self.back_error_frames - 1)

#         # 3. בדיקת רגל עמידה (נבדקת רק כשהרגל העובדת עדיין קרובה לרצפה למניעת בלבול)
#         if self.stage == 'START' and not is_bad_now:
#             if standing_knee_angle < 145: # הועבר ל-145 מעלות לעמידה טבעית ואנושית יותר
#                 self.leg_error_frames += 1
#                 if self.leg_error_frames > 8:
#                     posture_warning = "⚠️ Straighten your standing leg!"
#                     is_bad_now = True
#             else:
#                 self.leg_error_frames = max(0, self.leg_error_frames - 1)

#         # עדכון צבע השלד במסך בזמן אמת
#         self.is_posture_bad = is_bad_now

#         # =====================================================================
#         # 🔄 מכונת המצבים הראשית - זורמת וחסינת חסימות!
#         # =====================================================================
        
#         # חוק הזהב החדש: אם יש שגיאת יציבה אקטיבית, אנחנו מקפיאים את המצב ומציגים אזהרה,
#         # אבל לא הורסים את החזרה או חוסמים את היכולת לתקן!
#         if is_bad_now:
#             self.feedback = posture_warning
#             return working_knee_angle, self.counter

#         # מצב 0: START
#         if self.stage == 'START':
#             if hip_angle > 150 and working_knee_angle > 150:
#                 self.feedback = posture_warning if posture_warning else "Good posture. Lift to Passé!"
            
#             # כניסה לפסה - דורש הרמה אמיתית (אגן < 120) וקיפול חזק (ברך < 100)
#             elif hip_angle < 120 and working_knee_angle < 100:
#                 self.stage = 'PASSE'
#                 self.feedback = "Excellent Passé! Now extend forward!"
#                 self.current_rep_invalid = False

#         # מצב 1: PASSE
#         elif self.stage == 'PASSE':
#             # יישור קדימה - סף ביו-מכני ריאלי לראיית מכונה (135 מעלות בברך)
#             if working_knee_angle >= 135 and hip_angle <= 135:
#                 self.stage = 'EXTENDED'
#                 self.feedback = "Brilliant extension! Hold it..."
#             # הגנה מפני נפילת הרגל לרצפה באמצע התרגיל
#             elif hip_angle > 150: 
#                 self.feedback = "Don't drop the leg. Restart."
#                 self.stage = 'START'
#             else:
#                 self.feedback = "Kick forward until straight!"

#         # מצב 2: EXTENDED
#         elif self.stage == 'EXTENDED':
#             # קיפול חזרה למצב משולש (מתחת ל-120 מעלות)
#             if working_knee_angle < 120 and hip_angle <= 135:
#                 self.stage = 'RETRACTED'
#                 self.feedback = "Nice control! Now lower smoothly."
#             elif hip_angle > 150: 
#                 self.feedback = "Bend before lowering! Restart."
#                 self.stage = 'START'
#             else:
#                 self.feedback = "Now bend the knee back."

#         # מצב 3: RETRACTED
#         elif self.stage == 'RETRACTED':
#             # סיום חזרה מושלמת - הרגל חזרה למטה (מעל 145 מעלות באגן ובברך)
#             if hip_angle > 145 and working_knee_angle > 145:
#                 self.counter += 1
#                 self.stage = 'START'
                
#                 left = self.target_goal - self.counter
#                 if left <= 0:
#                     self.reps_left = "0"
#                     self.goal_finished = True
#                     self.feedback = "Workout Goal Achieved! Phenomenal job!"
#                 else:
#                     self.reps_left = str(left)
#                     self.feedback = f"Perfect rep! {left} remaining."
#             else:
#                 self.feedback = "Lower your leg completely."

#         return working_knee_angle, self.counter









# from src.ai.exercises.base_exercise import BaseExercise
# from src.ai.angle_calculator import AngleCalculator
# import numpy as np

# class StandingKneeExtension(BaseExercise):
#     def __init__(self):
#         super().__init__()
#         self.feedback = "Stand in profile to the camera." 
#         self.has_welcomed = False 
        
#         self.target_goal = 0      
#         self.reps_left = "0"      
#         self.goal_finished = False 
        
#         self.stage = 'START' 
        
#         self.leg_error_frames = 0
#         self.back_error_frames = 0
#         self.front_facing_frames = 0
        
#         self.current_rep_invalid = False
        
#         # 🔥 משתנה חדש שמשדר החוצה אם השלד צריך להיות צבוע באדום!
#         self.is_posture_bad = False

#     def set_target_goal(self, goal):
#         self.target_goal = goal
#         self.reps_left = str(goal)
#         self.counter = 0
#         self.goal_finished = False
#         self.feedback = f"Goal: {goal} reps. Stand in profile and lift to Passé!"
#         self.stage = 'START'
#         self.has_welcomed = False
#         self.current_rep_invalid = False
#         self.is_posture_bad = False

#     def check(self, landmarks):
#         if self.target_goal == 0:
#             self.feedback = ""
#             return 0, self.counter
            
#         try:
#             # ==========================================
#             # 1. זיהוי דינמי של הצד (פרופיל ימין או שמאל)
#             # ==========================================
#             # נבדוק איזו כתף קרובה יותר למצלמה (לפי ציר Z)
#             left_shoulder_z = landmarks[11].z
#             right_shoulder_z = landmarks[12].z
            
#             if left_shoulder_z < right_shoulder_z:
#                 # פרופיל שמאלי: רגל שמאל עובדת, ימין עומדת
#                 shoulder_w = [landmarks[11].x, landmarks[11].y]
#                 hip_w = [landmarks[23].x, landmarks[23].y]
#                 knee_w = [landmarks[25].x, landmarks[25].y]
#                 ankle_w = [landmarks[27].x, landmarks[27].y]
                
#                 hip_s = [landmarks[24].x, landmarks[24].y]
#                 knee_s = [landmarks[26].x, landmarks[26].y]
#                 ankle_s = [landmarks[28].x, landmarks[28].y]
#             else:
#                 # פרופיל ימני: רגל ימין עובדת, שמאל עומדת
#                 shoulder_w = [landmarks[12].x, landmarks[12].y]
#                 hip_w = [landmarks[24].x, landmarks[24].y]
#                 knee_w = [landmarks[26].x, landmarks[26].y]
#                 ankle_w = [landmarks[28].x, landmarks[28].y]
                
#                 hip_s = [landmarks[23].x, landmarks[23].y]
#                 knee_s = [landmarks[25].x, landmarks[25].y]
#                 ankle_s = [landmarks[27].x, landmarks[27].y]
            
#             # חישובי זוויות
#             hip_angle = AngleCalculator.calculate_angle(shoulder_w, hip_w, knee_w)
#             working_knee_angle = AngleCalculator.calculate_angle(hip_w, knee_w, ankle_w)
#             standing_knee_angle = AngleCalculator.calculate_angle(hip_s, knee_s, ankle_s)
            
#             # בדיקת גב ישר (מחמיר ומדויק יותר: סטייה קטנה מ-0.12)
#             back_straight = abs(shoulder_w[0] - hip_w[0]) < 0.12
            
#             # בדיקה האם המתאמן עם הפנים למצלמה במקום בפרופיל
#             # מרחק גדול בין הכתפיים בציר X מעיד על חזית
#             facing_camera = abs(landmarks[11].x - landmarks[12].x) > 0.18
            
#         except Exception as e:
#             self.feedback = "Ensure your full body is visible."
#             self.is_posture_bad = True
#             return 0, self.counter

#         # =====================================================================
#         # 🚨 מערכת אבחון יציבה קשוחה (מונעת רמאות מהירה) - כולל שלד אדום!
#         # =====================================================================
#         posture_warning = ""
#         is_bad_now = False

#         # 1. בדיקת חזית/פרופיל
#         if facing_camera:
#             self.front_facing_frames += 1
#             if self.front_facing_frames > 5:
#                 posture_warning = "⚠️ Turn to the side! Profile only."
#                 self.current_rep_invalid = True
#                 is_bad_now = True
#         else:
#             self.front_facing_frames = 0

#         # 2. בדיקת גב עקום
#         if not back_straight and not is_bad_now:
#             self.back_error_frames += 1
#             if self.back_error_frames > 5: # פוסל מהר מאוד! גם תנועה מהירה לא תעזור
#                 posture_warning = "⚠️ Keep your back straight!"
#                 self.current_rep_invalid = True
#                 is_bad_now = True
#         else:
#             self.back_error_frames = max(0, self.back_error_frames - 1)

#         # 3. בדיקת רגל עמידה
#         # ההחלטה המקצועית: בודקים את רגל העמידה אך ורק בעמדת המוצא. 
#         # בזמן פסה/דבלופה המצלמה מתבלבלת מההסתרה, לכן מקצועית (CV) עדיף להתעלם ממנה באוויר.
#         if self.stage == 'START' and not is_bad_now:
#             if standing_knee_angle < 155: # החמרנו! 155 זה רגל עמידה ישרה ואמיתית
#                 self.leg_error_frames += 1
#                 if self.leg_error_frames > 5:
#                     posture_warning = "⚠️ Straighten your standing leg!"
#                     self.current_rep_invalid = True
#                     is_bad_now = True
#             else:
#                 self.leg_error_frames = max(0, self.leg_error_frames - 1)

#         # מעדכן את המשתנה שאחראי על צבע השלד במסך!
#         self.is_posture_bad = is_bad_now

#         # =====================================================================
#         # 🔄 מכונת המצבים הראשית - חלקה ומדויקת!
#         # =====================================================================
        
#         # מצב 0: START
#         if self.stage == 'START':
#             if hip_angle > 150 and working_knee_angle > 150:
#                 self.feedback = posture_warning if posture_warning else "Good posture. Lift to Passé!"
            
#             # כניסה לפסה - דורש הרמה אמיתית (אגן < 120) וקיפול חזק (ברך < 100)
#             elif hip_angle < 120 and working_knee_angle < 100:
#                 self.stage = 'PASSE'
#                 self.feedback = "Excellent Passé! Now extend forward!"

#         # מצב 1: PASSE
#         elif self.stage == 'PASSE':
#             # יישור מלא: הברך צריכה להיות גדולה מ-145 מעלות כדי להיחשב ישרה!
#             if working_knee_angle >= 145 and hip_angle <= 130:
#                 self.stage = 'EXTENDED'
#                 self.feedback = "Brilliant extension! Hold it..."
#             # אם הוא הפיל את הרגל לרצפה בטעות
#             elif hip_angle > 160: 
#                 self.feedback = "You dropped the leg! Restart."
#                 self.stage = 'START'
#             else:
#                 self.feedback = posture_warning if posture_warning else "Kick forward until straight!"

#         # מצב 2: EXTENDED
#         elif self.stage == 'EXTENDED':
#             # חייב לקפל בחזרה מתחת ל-110 כדי לחזור למצב רטרקט
#             if working_knee_angle < 110 and hip_angle <= 130:
#                 self.stage = 'RETRACTED'
#                 self.feedback = "Nice control! Now lower smoothly."
#             elif hip_angle > 160: 
#                 self.feedback = "Bend before lowering! Restart."
#                 self.stage = 'START'
#             else:
#                 self.feedback = posture_warning if posture_warning else "Now bend the knee back."

#         # מצב 3: RETRACTED
#         elif self.stage == 'RETRACTED':
#             # סיום חזרה - הרגל חזרה למטה לגמרי (ישרה לחלוטין - 160 מעלות)
#             if hip_angle > 160 and working_knee_angle > 160:
                
#                 if self.current_rep_invalid:
#                     # ❌ המתאמן זייף במהלך התנועה!
#                     self.feedback = "❌ Rep NOT counted! Bad posture/speed."
#                     self.stage = 'START'
#                     self.current_rep_invalid = False 
#                 else:
#                     # ✅ החזרה הייתה מושלמת
#                     self.counter += 1
#                     self.stage = 'START'
                    
#                     left = self.target_goal - self.counter
#                     if left <= 0:
#                         self.reps_left = "0"
#                         self.goal_finished = True
#                         self.feedback = "Workout Goal Achieved! Phenomenal job!"
#                     else:
#                         self.reps_left = str(left)
#                         self.feedback = f"Perfect rep! {left} remaining."
#             else:
#                 self.feedback = posture_warning if posture_warning else "Lower your leg completely."

#         return working_knee_angle, self.counter

















# from src.ai.exercises.base_exercise import BaseExercise
# from src.ai.angle_calculator import AngleCalculator
# import numpy as np

# class StandingKneeExtension(BaseExercise):
#     def __init__(self):
#         super().__init__()
#         self.feedback = "Stand straight to begin." 
#         self.has_welcomed = False 
        
#         self.target_goal = 0      
#         self.reps_left = "0"      
#         self.goal_finished = False 
        
#         # מכונת המצבים המקורית והמעולה שלך נשמרה במלואה!
#         # 'START' -> 'PASSE' -> 'EXTENDED' -> 'RETRACTED'
#         self.stage = 'START' 
        
#         # מונה פנימי למניעת קפיצות ורעשים בפידבקים (Smoothing Counter)
#         self.posture_error_counter = 0

#     def set_target_goal(self, goal):
#         self.target_goal = goal
#         self.reps_left = str(goal)
#         self.counter = 0
#         self.goal_finished = False
#         self.feedback = f"Goal: {goal} reps. Lift your knee to Passé, then extend!"
#         self.stage = 'START'
#         self.has_welcomed = False
#         self.posture_error_counter = 0

#     def check(self, landmarks):
#         # הגנה: אם המשתמש עוד לא בחר מספר חזרות או שהיעד מאופס
#         if self.target_goal == 0:
#             self.feedback = ""
#             return 0, self.counter
            
#         try:
#             # שליפת קורדינאטות (x, y) לחישובי זוויות
#             shoulder_l = [landmarks[11].x, landmarks[11].y]
#             hip_l = [landmarks[23].x, landmarks[23].y]
#             knee_l = [landmarks[25].x, landmarks[25].y]
#             ankle_l = [landmarks[27].x, landmarks[27].y]
            
#             hip_r = [landmarks[24].x, landmarks[24].y]
#             knee_r = [landmarks[26].x, landmarks[26].y]
#             ankle_r = [landmarks[28].x, landmarks[28].y]
            
#             # 1. חישוב זוויות הליבה של הרגל העובדת
#             hip_angle = AngleCalculator.calculate_angle(shoulder_l, hip_l, knee_l)
#             working_knee_angle = AngleCalculator.calculate_angle(hip_l, knee_l, ankle_l)
            
#             # 2. חישוב זוויות לבדיקת יציבה ודגשים (גב ורגל תומכת)
#             standing_knee_angle = AngleCalculator.calculate_angle(hip_r, knee_r, ankle_r)
            
#             # הפכנו את הגב לטיפה יותר גמיש (0.15 במקום 0.12) כדי שלא יצעק על כל תזוזה קטנה
#             back_straight = abs(landmarks[11].x - landmarks[23].x) < 0.15
            
#         except Exception as e:
#             self.feedback = "Ensure your full body is visible."
#             return 0, self.counter

#         # ==========================================
#         # 🚨 מערכת דגשים ויציבה בזמן אמת (Posture Checks) - נשמרה!
#         # ==========================================
#         # הפכנו את רף הרגל התומכת ל-145 מעלות (במקום 155) - סלחני יותר לכיפוף קל וטבעי
#         if standing_knee_angle < 145:
#             self.posture_error_counter += 1
#             if self.posture_error_counter > 8: # העלינו ל-8 פריימים כדי לתת לך מרחב תנועה
#                 self.feedback = "FIX: Straighten your standing leg!"
#                 return working_knee_angle, self.counter
#         elif not back_straight:
#             self.posture_error_counter += 1
#             if self.posture_error_counter > 8:
#                 self.feedback = "FIX: Keep your spine erect and back straight!"
#                 return working_knee_angle, self.counter
#         else:
#             self.posture_error_counter = max(0, self.posture_error_counter - 1)

#         # ==========================================
#         # 🔄 מכונת המצבים של התנועה (Développé Logic - הגרסה הזורמת)
#         # ==========================================
        
#         # מצב 0: המתנה לתחילת תנועה (רגל למטה)
#         if self.stage == 'START':
#             # פתחנו את הטווח ל-135 מעלות (במקום 150) - קל יותר לאפס את החזרה
#             if hip_angle > 135 and working_knee_angle > 135:
#                 self.feedback = "Good posture. Lift your knee to Passé!"
            
#             # כניסה לפסא: פתחנו את זווית האגן ל-130 (במקום 125) והברך ל-115 (במקום 100)
#             elif hip_angle <= 130 and working_knee_angle < 115:
#                 self.stage = 'PASSE'
#                 self.feedback = "Excellent Passé! Now kick and extend forward!"

#         # מצב 1: החזקת רגל מקופלת באוויר (Passé position)
#         elif self.stage == 'PASSE':
#             # יישור הרגל קדימה: הורדנו את הדרישה ל-120 מעלות בברך (במקום 140 המלחיץ והנוקשה!)
#             # וזווית האגן הורחבה ל-130 (במקום 125) כדי לזרום עם גובה הרגל שלך במצלמה
#             if working_knee_angle >= 120 and hip_angle <= 130:
#                 self.stage = 'EXTENDED'
#                 self.feedback = "Brilliant extension! Hold and bend it back."
#             # נפילה מוקדמת של הרגל (הורחב ל-145 מעלות)
#             elif hip_angle > 145: 
#                 self.feedback = "Don't drop your thigh! Lift from the hip."
#                 self.stage = 'START'

#         # מצב 2: הרגל מיושרת באוויר (Extension)
#         elif self.stage == 'EXTENDED':
#             # קיפול חזרה: הברך צריכה להתקפל מתחת ל-125 מעלות (במקום 110 הנוקשה)
#             if working_knee_angle < 125 and hip_angle <= 130:
#                 self.stage = 'RETRACTED'
#                 self.feedback = "Nice control! Now lower your leg down smoothly."
#             elif hip_angle > 140: # ירידה ישירה בלי קיפול
#                 self.feedback = "Remember to bend your knee before lowering!"
#                 self.stage = 'START'

#         # מצב 3: הרגל קופלה מחדש באוויר, מחכים להורדה מלאה לרצפה
#         elif self.stage == 'RETRACTED':
#             # סיום חזרה מושלמת: רגל יורדת למטה (מעל 135 מעלות באגן ובברך במקום 150)
#             if hip_angle > 135 and working_knee_angle > 135:
#                 self.counter += 1
#                 self.stage = 'START'
                
#                 # עדכון מוני חזרות ויעדים
#                 left = self.target_goal - self.counter
#                 if left <= 0:
#                     self.reps_left = "0"
#                     self.goal_finished = True
#                     self.feedback = "Workout Goal Achieved! Phenomenal job!"
#                 else:
#                     self.reps_left = str(left)
#                     self.feedback = f"Perfect rep! {left} remaining."

#         return working_knee_angle, self.counter














# from src.ai.exercises.base_exercise import BaseExercise
# from src.ai.angle_calculator import AngleCalculator
# import numpy as np

# class StandingKneeExtension(BaseExercise):
#     def __init__(self):
#         super().__init__()
#         self.feedback = "Stand straight to begin." 
#         self.has_welcomed = False 
        
#         self.target_goal = 0      
#         self.reps_left = "0"      
#         self.goal_finished = False 
        
#         # מכונת המצבים המעודכנת לתרגיל ה-Développé
#         # 'START' -> 'PASSE' -> 'EXTENDED' -> 'RETRACTED'
#         self.stage = 'START' 
        
#         # מונה פנימי למניעת קפיצות ורעשים בפידבקים (Smoothing Counter)
#         self.posture_error_counter = 0

#     def set_target_goal(self, goal):
#         self.target_goal = goal
#         self.reps_left = str(goal)
#         self.counter = 0
#         self.goal_finished = False
#         self.feedback = f"Goal: {goal} reps. Lift your knee to Passé, then extend!"
#         self.stage = 'START'
#         self.has_welcomed = False
#         self.posture_error_counter = 0

#     def check(self, landmarks):
#         # הגנה: אם המשתמש עוד לא בחר מספר חזרות או שהיעד מאופס
#         if self.target_goal == 0:
#             self.feedback = ""
#             return 0, self.counter
            
#         # גובה ורוחב מנורמלים לבדיקות יחסיות (MediaPipe landmarks מגיעים בין 0 ל-1)
#         # נשתמש ברגל שמאל כרגל העובדת (ניתן להרחיב דינמית בהמשך)
#         # נקודות מפתח: 11=כתף שמאל, 23=אגן שמאל, 25=ברך שמאל, 27=קרסול שמאל
#         # נקודות רגל ימין (עמידה): 24=אגן ימין, 26=ברך ימין, 28=קרסול ימין
        
#         try:
#             # שליפת קורדינאטות (x, y) לחישובי זוויות
#             shoulder_l = [landmarks[11].x, landmarks[11].y]
#             hip_l = [landmarks[23].x, landmarks[23].y]
#             knee_l = [landmarks[25].x, landmarks[25].y]
#             ankle_l = [landmarks[27].x, landmarks[27].y]
            
#             hip_r = [landmarks[24].x, landmarks[24].y]
#             knee_r = [landmarks[26].x, landmarks[26].y]
#             ankle_r = [landmarks[28].x, landmarks[28].y]
            
#             # 1. חישוב זוויות הליבה של הרגל העובדת
#             # זווית אגן: קו ישר מהכתף לאגן, ומשם לברך
#             hip_angle = AngleCalculator.calculate_angle(shoulder_l, hip_l, knee_l)
#             # זווית ברך: קו מהאגן לברך, ומשם לקרסול
#             working_knee_angle = AngleCalculator.calculate_angle(hip_l, knee_l, ankle_l)
            
#             # 2. חישוב זוויות לבדיקת יציבה ודגשים (גב ורגל תומכת)
#             # רגל עמידה ישרה (זווית קרובה ל-180 מעלות)
#             standing_knee_angle = AngleCalculator.calculate_angle(hip_r, knee_r, ankle_r)
#             # גב ישר: זווית נטיית הכתף יחסית לאגן אנכית
#             back_straight = abs(landmarks[11].x - landmarks[23].x) < 0.12
            
#         except Exception as e:
#             # הגנה למקרה שחלק מהנקודות הוסתרו מהמצלמה
#             self.feedback = "Ensure your full body is visible."
#             return 0, self.counter

#         # ==========================================
#         # 🚨 מערכת דגשים ויציבה בזמן אמת (Posture Checks)
#         # ==========================================
#         if standing_knee_angle < 155:
#             self.posture_error_counter += 1
#             if self.posture_error_counter > 5: # סינון רעשים
#                 self.feedback = "FIX: Straighten your standing leg!"
#                 return working_knee_angle, self.counter
#         elif not back_straight:
#             self.posture_error_counter += 1
#             if self.posture_error_counter > 5:
#                 self.feedback = "FIX: Keep your spine erect and back straight!"
#                 return working_knee_angle, self.counter
#         else:
#             self.posture_error_counter = max(0, self.posture_error_counter - 1)

#         # ==========================================
#         # 🔄 מכונת המצבים של התנועה (Développé Logic)
#         # ==========================================
        
#         # מצב 0: המתנה לתחילת תנועה (רגל למטה)
#         if self.stage == 'START':
#             if hip_angle > 150 and working_knee_angle > 150:
#                 self.feedback = "Good posture. Lift your knee to Passé!"
            
#             # זיהוי מעבר לפסא: האגן מתקפל (מתחת ל-125 מעלות, כלומר הרגל עולה לפחות ל-55° ומעלה)
#             # והברך מקופלת חזק (זווית קטנה מ-100 מעלות, יוצרת משולש)
#             elif hip_angle <= 125 and working_knee_angle < 100:
#                 self.stage = 'PASSE'
#                 self.feedback = "Excellent Passé! Now kick and extend forward!"

#         # מצב 1: החזקת רגל מקופלת באוויר (Passé position)
#         elif self.stage == 'PASSE':
#             # המשתמש מיישר את הרגל קדימה: זווית הברך נפתחת (גדולה מ-140 מעלות)
#             # האגן נשאר מקופל/גבוה (גמישות מורחבת: מקבלים כל גובה בין 60° ל-125°)
#             if working_knee_angle >= 140 and hip_angle <= 125:
#                 self.stage = 'EXTENDED'
#                 self.feedback = "Brilliant extension! Hold and bend it back."
#             elif hip_angle > 140: # נפילה של הרגל מוקדם מדי
#                 self.feedback = "Don't drop your thigh! Lift from the hip."
#                 self.stage = 'START'

#         # מצב 2: הרגל מיושרת באוויר (Extension)
#         elif self.stage == 'EXTENDED':
#             # המשתמש חייב לקפל את הברך בחזרה למצב משולש לפני ההורדה
#             if working_knee_angle < 110 and hip_angle <= 125:
#                 self.stage = 'RETRACTED'
#                 self.feedback = "Nice control! Now lower your leg down smoothly."
#             elif hip_angle > 135: # המשתמש הוריד את הרגל ישר בלי לקפל
#                 self.feedback = "Remember to bend your knee before lowering!"
#                 self.stage = 'START'

#         # מצב 3: הרגל קופלה מחדש באוויר, מחכים להורדה מלאה לרצפה
#         elif self.stage == 'RETRACTED':
#             # החזרה מושלמת רק כשהרגל נוגעת חזרה ברצפה בצורה ישרה
#             if hip_angle > 150 and working_knee_angle > 150:
#                 self.counter += 1
#                 self.stage = 'START'
                
#                 # עדכון מוני חזרות ויעדים
#                 left = self.target_goal - self.counter
#                 if left <= 0:
#                     self.reps_left = "0"
#                     self.goal_finished = True
#                     self.feedback = "Workout Goal Achieved! Phenomenal job!"
#                 else:
#                     self.reps_left = str(left)
#                     self.feedback = f"Perfect rep! {left} remaining."

#         return working_knee_angle, self.counter


















# from src.ai.exercises.base_exercise import BaseExercise
# from src.ai.angle_calculator import AngleCalculator

# class StandingKneeExtension(BaseExercise):
#     def __init__(self):
#         super().__init__()
#         self.feedback = "" 
#         self.has_welcomed = False 
        
#         self.target_goal = 0      
#         self.reps_left = "0"      
#         self.goal_finished = False 
        
#         # מכונת המצבים המדויקת לתרגיל שלך:
#         # 'marching' = הרמת הברך | 'extending' = יישור הרגל קדימה | 'completed_rep' = חזרה מושלמת
#         self.stage = 'marching' 

#     def set_target_goal(self, goal):
#         self.target_goal = goal
#         self.reps_left = str(goal)
#         self.counter = 0
#         self.goal_finished = False
#         self.feedback = f"Goal: {goal} reps. Stand in profile, lift your knee and extend!"
#         self.stage = 'marching'
#         self.has_welcomed = False

#     def check(self, landmarks):
#         # 1. הגנה: אם המשתמש עוד לא בחר מספר חזרות, לא עושים כלום
#         if self.target_goal == 0:
#             self.feedback = ""
#             return 0, self.counter
            
#         # 2. שליפת נקודות פרופיל (צד ימין מופנה למצלמה)
#         shoulder = [landmarks[12].x, landmarks[12].y]      # כתף ימין
#         hip = [landmarks[24].x, landmarks[24].y]           # אגן ימין
#         knee_working = [landmarks[26].x, landmarks[26].y]  # ברך ימין (הרגל שעובדת)
#         ankle_working = [landmarks[28].x, landmarks[28].y] # קרסול ימין (הרגל שעובדת)
        
#         # נקודות של הרגל השנייה (הרגל שעומדים עליה - צד שמאל)
#         hip_standing = [landmarks[23].x, landmarks[23].y]
#         knee_standing = [landmarks[25].x, landmarks[25].y]
#         ankle_standing = [landmarks[27].x, landmarks[27].y]

#         # 3. חישובי זוויות
#         # זווית אגן (כתף -> אגן -> ברך) - בודק אם הירך עלתה לגובה המותן
#         hip_angle = AngleCalculator.calculate_angle(shoulder, hip, knee_working)
        
#         # זווית ברך עובדת (אגן -> ברך -> קרסול) - בודק אם הרגל מקופלת או ישרה
#         working_knee_angle = AngleCalculator.calculate_angle(hip, knee_working, ankle_working)
        
#         # זווית ברך עמידה (אגן -> ברך -> קרסול) - לוודא שרגל שמאל ישרה על הרצפה
#         standing_knee_angle = AngleCalculator.calculate_angle(hip_standing, knee_standing, ankle_standing)

#         # 4. בדיקת בטיחות א': האם רגל העמידה ישרה?
#         if standing_knee_angle < 155:
#             self.feedback = "ERROR: Keep your standing leg straight!"
#             return working_knee_angle, self.counter

#         # 5. בדיקת בטיחות ב': האם הגב ישר? (הפרש בציר ה-X בין כתף לאגן)
#         x_difference = abs(shoulder[0] - hip[0])
#         if x_difference > 0.12:
#             self.feedback = "ERROR: Keep your back straight!"
#             return working_knee_angle, self.counter

#         # 6. לוגיקת שלבי התנועה (הלב של התרגיל)

#         # שלב א': הרגל למטה ברצפה או חוזרת לרצפה
#         if hip_angle > 140:
#             if self.stage == 'completed_rep':
#                 self.stage = 'marching' # מוכן לחזרה הבאה
#             if not self.goal_finished:
#                 self.feedback = "Lift your knee up to hip height (90°)."

#         # שלב ב': המשתמש מרים את הברך לגובה המותן אבל היא עדיין מקופלת
#         elif hip_angle <= 105 and self.stage == 'marching':
#             # בודקים שהברך באמת מקופלת (זווית ברך קטנה מ-110)
#             if working_knee_angle < 110:
#                 self.feedback = "Great! Now KICK and straighten your leg forward!"
#                 self.stage = 'extending' # עוברים לשלב היישור
#             else:
#                 self.feedback = "Keep your knee high and bend your leg!"

#         # שלב ג': המשתמש מנסה ליישר את הרגל קדימה (טווח גמישות: בין 140 ל-180 מעלות בברך)
#         elif self.stage == 'extending':
#             # אם הוא עדיין לא יישר מספיק (הזווית קטנה מ-140 מעלות)
#             if working_knee_angle < 140:
#                 self.feedback = "Straighten your leg more! Kick forward!"
            
#             # אם הוא הצליח ליישר את הרגל קדימה (הברך נפתחה) והאגן עדיין גבוה
#             elif working_knee_angle >= 140 and hip_angle <= 110:
#                 self.stage = 'completed_rep' # החזרה הושלמה בהצלחה!
#                 self.counter += 1
                
#                 # עדכון חזרות
#                 left = self.target_goal - self.counter
#                 if left <= 0:
#                     self.reps_left = "0"
#                     self.goal_finished = True
#                     self.feedback = "Workout Complete! Outstanding performance!"
#                 else:
#                     self.reps_left = str(left)
#                     self.feedback = f"Perfect kick! Lower down safely. {left} left."

#         return working_knee_angle, self.counter