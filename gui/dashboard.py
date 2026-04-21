import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
ctk.FontManager.load_font("cufel.otf")

class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("N.O.V.A.")
        self.geometry("500x500")
        self.configure(fg_color = "#0a0a0f")
        self.resizable(False, False)

        self.my_label = ctk.CTkLabel(self, text="N.O.V.A.", font=("CUFEL", 64), text_color=("#00d4ff"))
        self.my_label.pack(pady=10)

        self.textbox = ctk.CTkTextbox(self, width=440, height=300, fg_color="#0f0f1a")
        self.textbox.pack(pady=10,padx=30)
        self.textbox.configure(state="disabled")

        self.statusLabel = ctk.CTkLabel(self, text="● IDLE", font=("Consolas", 13), text_color=("#888888"))
        self.statusLabel.pack(pady=1)

        self.set_status("LISTENING")
    
    def add_message(self,sender,text):
        self.textbox.configure(state="normal")
        self.textbox.insert("insert",sender+": "+text+"\n")
        self.textbox.configure(state="disabled")

    def set_status(self,status):
        if status == "LISTENING":
            self.statusLabel.configure(text="● LISTENING", text_color="#00ff88")
        elif status == "THINKING":
            self.statusLabel.configure(text="● THINKING", text_color="#ffd700")
        elif status == "SPEAKING":
            self.statusLabel.configure(text="● SPEAKING", text_color="#0c7b92")
        else:
            self.statusLabel.configure(text="● IDLE", text_color="#888888")

if __name__ == "__main__":
    app = Dashboard()
    app.mainloop()