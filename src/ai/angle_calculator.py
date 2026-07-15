import numpy as np

class AngleCalculator:
    @staticmethod
    def calculate_angle(a, b, c):
        """
        Calculates the angle at point b (e.g. elbow/knee), using points a and c.
        """
        a = np.array(a)  # First point (e.g., shoulder)
        b = np.array(b)  # Joint point (e.g., elbow)
        c = np.array(c)  # Third point (e.g., wrist)
        
        # Calculate the angle using arctan2
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        # We always want the smaller internal angle
        if angle > 180.0:
            angle = 360 - angle
            
        return angle