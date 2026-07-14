class BaseExercise:
    def __init__(self):
        self.counter = 0
        self.stage = None  # יכול להיות 'up' או 'down'
        
    def check(self, landmarks):
        """
        כל תרגיל יממש כאן את הלוגיקה הספציפית שלו.
        """
        raise NotImplementedError("Every exercise must implement the 'check' function!")
