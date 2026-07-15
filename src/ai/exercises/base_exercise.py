class BaseExercise:
    """
    Base class for all exercises. Each specific exercise inherits from this
    and implements its own rep-counting logic in 'check'.
    """
    def __init__(self):
        self.counter = 0
        self.stage = None  
        
    def check(self, landmarks):
        """
        Every exercise implements its own specific logic here.
        """
        raise NotImplementedError("Every exercise must implement the 'check' function!")
