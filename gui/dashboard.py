import customtkinter as ctk
import random

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
ctk.FontManager.load_font("cufel.otf")

class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.isListening = False

        self.title("N.O.V.A.")
        self.geometry("500x500")
        self.configure(fg_color = "#0a0a0f")
        self.resizable(False, False)

        self.my_label = ctk.CTkLabel(self, text="N.O.V.A.", font=("CUFEL", 64), text_color=("#00d4ff"))
        self.my_label.pack(pady=5)

        self.textbox = ctk.CTkTextbox(self, width=440, height=200, fg_color="#0f0f1a")
        self.textbox.pack(pady=5,padx=30)
        self.textbox.configure(state="disabled")

        self.statusLabel = ctk.CTkLabel(self, text="● IDLE", font=("Consolas", 13), text_color=("#888888"))
        self.statusLabel.pack(pady=1)

        self.my_canvas = ctk.CTkCanvas(self, width=440, height=60, bg="#0a0a0f", highlightthickness=0)
        self.my_canvas.pack(pady=5)
        self.bars = []
        number_of_bars = 20
        bar_width = 4
        canvas_width = 440
        spacing = canvas_width / number_of_bars
        for i in range(number_of_bars):
            x_pos = (i * spacing) + (spacing / 2)
            bar = self.my_canvas.create_rectangle(x_pos - (bar_width / 2), 20, x_pos + (bar_width / 2), 30, fill="#00d4ff", outline="")
            self.bars.append(bar)

        self.set_status("LISTENING")
    
    def add_message(self,sender,text):
        self.textbox.configure(state="normal")
        self.textbox.insert("end",sender+": "+text+"\n")
        self.textbox.configure(state="disabled")

    def set_status(self,status):
        if status == "LISTENING":
            self.statusLabel.configure(text="● LISTENING", text_color="#00ff88")
            if not self.isListening:
                self.isListening = True
                self.animate_waveform()
        elif status == "THINKING":
            self.statusLabel.configure(text="● THINKING", text_color="#ffd700")
            self.isListening = False
        elif status == "SPEAKING":
            self.statusLabel.configure(text="● SPEAKING", text_color="#0c7b92")
            self.isListening = False
        else:
            self.statusLabel.configure(text="● IDLE", text_color="#888888")
            self.isListening = False

    def animate_waveform(self):
        if not self.isListening:
            self.my_canvas.delete("all")
            return
        self.my_canvas.delete("all")
        number_of_bars = 20
        spacing = 440 / number_of_bars
        center_y = 30

        for i in range(number_of_bars):
            bar_height = random.randint(10, 100) 
            x_pos = (i * spacing) + (spacing / 2)
            
            y1 = center_y - (bar_height / 2)
            y2 = center_y + (bar_height / 2)

            self.my_canvas.create_rectangle(
                x_pos - 2, y1, 
                x_pos + 2, y2, 
                fill="#00d4ff", 
                outline=""
            )
        self.after(100, self.animate_waveform)

if __name__ == "__main__":
    app = Dashboard()
    app.mainloop()