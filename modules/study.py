import time
import threading
from plyer import notification
from PyPDF2 import PdfReader as pdf
from core.brain import Brain
from tkinter import filedialog, Tk

class StudyModule:
    def __init__(self):
        self.timer_thread = None
        self.brain = Brain()

    def pomodoro(self, minutes=25):
        def countdown():
            time.sleep(minutes * 60)
            notification.notify(
                title="N.O.V.A. Study Alert",
                message="Pomodoro done! Take a break, you've earned it.",
                timeout=10
            )

        self.timer_thread = threading.Thread(target=countdown)
        self.timer_thread.start()
        return f"Pomodoro started for {minutes} minutes. Go focus, I'll notify you when it's over."
    
    def summarize_pdf(self):
        try:
            root = Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            file_path = filedialog.askopenfilename(
                title="Select a PDF for N.O.V.A",
                filetypes=[("PDF files", "*.pdf")]
            )
            root.destroy()

            if not file_path:
                return "No file was selected."

            reader = pdf(file_path)
            full_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

            if not full_text.strip():
                return "The PDF seems to be empty or unreadable."

            words = full_text.split()
            if len(words) > 8000:
                print(f"PDF too long ({len(words)} words). Truncating to 8000 words.")
                full_text = " ".join(words[:8000])

            prompt = f"Please summarize the following text in exactly 5 sentences: {full_text}"
            summary = self.brain.ask(prompt)
            
            return summary

        except Exception as e:
            if "rate_limit_exceeded" in str(e):
                return "The PDF is too large for my current memory limits. Try a shorter document."
            return f"I had trouble reading that PDF. Error: {str(e)}"
        
    def flashcard(self, topic):
        try:
            prompt = f"Give me 3 flashcard questions and answers about {topic}. Format: Q: ... A: ..."
            response = self.brain.ask(prompt)
            return response
        except Exception as e:
            return f"I couldn't generate flashcards right now. Error: {str(e)}"
    
