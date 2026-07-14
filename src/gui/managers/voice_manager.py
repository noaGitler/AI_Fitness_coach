import threading
import pyttsx3
from PyQt6.QtCore import QObject

class VoiceManager(QObject):
    """
    מנהל הפידבק הקולי הרשמי של האפליקציה (SOLID - Single Responsibility Principle).
    מבודד לחלוטין את מנוע ה-Text-to-Speech (pyttsx3) ומריץ אותו בטרד נפרד למניעת תקיעת ה-GUI.
    """
    def __init__(self):
        super().__init__()
        self.last_spoken_text = ""
        self.is_speaking = False

    def speak_safe(self, text, priority=False):
        """
        מקבל טקסט, מנקה אותו, ומקריא אותו ברמקול בצורה מאובטחת ללא חסימת ממשק המשתמש.
        (בול כמו הפונקציה המקורית מהמיין שלך, רק מופרדת לחלוטין בארכיטקטורה)
        """
        # הגנות מפני כפל דיבור או דיבור מקביל ששובר את המנוע
        if not text or text == self.last_spoken_text or self.is_speaking:
            return
        
        if not priority and (text == self.last_spoken_text or self.is_speaking):
            return
        
        if priority:
            self.is_speaking = False
            
        self.last_spoken_text = text
        self.is_speaking = True

        # def run():
        #     try:
        #         # ניקוי המחרוזות הייחודי ללוגיקת ה-AI שלכן
        #         clean = text.replace("ERROR: ", "").replace("rep!", "rep.")
                
        #         # אתחול וכיול המנוע בתוך הטרד
        #         engine = pyttsx3.init()
        #         engine.setProperty('rate', 175) # מהירות קצב דיבור אופטימלית
        #         engine.say(clean)
        #         engine.runAndWait()
                
        #         # שחרור המנוע מהזיכרון למניעת זליגות זיכרון (Memory Leaks)
        #         del engine

        def run():
            try:
                # ניקוי המחרוזות הייחודי ללוגיקת ה-AI שלכן
                clean = text.replace("ERROR: ", "").replace("rep!", "rep.")
                
                # 🔥 תוספת חדשה: ניקוי אמוג'ים וסימני אזהרה ויזואליים כדי שלא ישבשו את הדיבור
                clean = clean.replace("⚠️ ", "").replace("❌ ", "")
                
                # אתחול וכיול המנוע בתוך הטרד
                engine = pyttsx3.init()
                engine.setProperty('rate', 175) # מהירות קצב דיבור אופטימלית
                engine.say(clean)
                engine.runAndWait()
                
                # שחרור המנוע מהזיכרון למניעת זליגות זיכרון (Memory Leaks)
                del engine
            except Exception as e:
                print(f"[VOICE ERROR] Failed to output speech: {e}")
            finally:
                self.is_speaking = False

        # הרצה בטרד נפרד (daemon) כדי שה-GUI לא יקפא בזמן שהיא מדברת
        threading.Thread(target=run, daemon=True).start()

    def reset(self):
        """מאפס את זיכרון הדיבור (שימושי במעבר בין מסכים או איפוס אימון)"""
        self.last_spoken_text = ""
        self.is_speaking = False
        print("[VOICE] Voice manager cache cleared.")