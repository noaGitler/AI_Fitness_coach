import numpy as np

class AngleCalculator:
    @staticmethod
    def calculate_angle(a, b, c):
        """
        מחשב זווית בנקודה b (המרפק/ברך) לפי הנקודות a ו-c.
        """
        a = np.array(a)  # נקודה ראשונה (למשל כתף)
        b = np.array(b)  # נקודת המפרק (למשל מרפק)
        c = np.array(c)  # נקודה שלישית (למשל פרק כף יד)
        
        # חישוב הזווית באמצעות ארק-טנגנס (arctan2)
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        # אנחנו תמיד רוצים את הזווית הפנימית הקטנה
        if angle > 180.0:
            angle = 360 - angle
            
        return angle