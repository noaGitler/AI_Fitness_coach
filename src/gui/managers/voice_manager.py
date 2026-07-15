import threading
import pyttsx3
from PyQt6.QtCore import QObject

class VoiceManager(QObject):
    """
    The application's official voice feedback manager (SOLID - Single Responsibility Principle).
    Completely isolates the Text-to-Speech engine (pyttsx3) and runs it in a separate thread to prevent blocking the GUI.
    """
    def __init__(self):
        super().__init__()
        self.last_spoken_text = ""
        self.is_speaking = False

    def speak_safe(self, text, priority=False):
        """
        Receives text, cleans it, and reads it out of the speaker securely without blocking the UI.
        """
        # guards against duplicate speech or concurrent speech that would break the engine
        if not text or text == self.last_spoken_text or self.is_speaking:
            return
        
        if not priority and (text == self.last_spoken_text or self.is_speaking):
            return
        
        if priority:
            self.is_speaking = False
            
        self.last_spoken_text = text
        self.is_speaking = True


        def run():
            try:
                clean = text.replace("ERROR: ", "").replace("rep!", "rep.")
                clean = clean.replace("⚠️ ", "").replace("❌ ", "")
                
                engine = pyttsx3.init()
                engine.setProperty('rate', 175)  # optimal speech rate
                engine.say(clean)
                engine.runAndWait()
                
                # Release the engine from memory to prevent memory leaks
                del engine
            except Exception as e:
                print(f"[VOICE ERROR] Failed to output speech: {e}")
            finally:
                self.is_speaking = False

        # Run in a separate (daemon) thread so the GUI doesn't freeze while it speaks
        threading.Thread(target=run, daemon=True).start()

    def reset(self):
        """Resets the speech memory"""
        self.last_spoken_text = ""
        self.is_speaking = False
        print("[VOICE] Voice manager cache cleared.")