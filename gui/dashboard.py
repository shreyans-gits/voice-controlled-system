import customtkinter as ctk
import random
import pystray
from PIL import Image

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
ctk.FontManager.load_font("cufel.otf")

class Dashboard(ctk.CTk):
    def __init__(self, message_queue, input_queue):
        super().__init__()

        self.isListening = False

        self.title("N.O.V.A.")
        self.geometry("500x500")
        self.configure(fg_color = "#0a0a0f")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.my_label = ctk.CTkLabel(self, text="N.O.V.A.", font=("CUFEL", 64), text_color=("#00d4ff"))
        self.my_label.pack(pady=5)

        self.textbox = ctk.CTkTextbox(self, width=440, height=200, fg_color="#0f0f1a")
        self.textbox.pack(pady=5,padx=30)
        self.textbox.configure(state="disabled")

        self.statusLabel = ctk.CTkLabel(self, text="● IDLE", font=("Consolas", 13), text_color=("#888888"))

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
        self.statusLabel.pack(pady=1)
        # self.set_status("LISTENING")

        self.input_frame = ctk.CTkFrame(self, fg_color="#0a0a0f")
        self.input_frame.pack(side="bottom", fill="x", pady=20, padx=30)
        self.input_field = ctk.CTkTextbox(
            self.input_frame, 
            width=340, 
            height=35,
            fg_color="#0f0f1a",
            border_color="#00d4ff",
            border_width=2,
            activate_scrollbars=False
        )
        self.input_field.pack(side="left", padx=(0, 10), pady=10)

        self.send_button = ctk.CTkButton(
            self.input_frame,
            text="➤",
            width=50,
            command=self.handle_input,
            fg_color="#00d4ff",
            hover_color="#0c7b92",
            text_color="#0a0a0f"
        )
        self.send_button.pack(side="left")
        self.input_field.bind("<Shift-Return>", self.handle_newline)
        self.input_field.bind("<Return>", self.handle_enter)

        self.textbox.tag_config("nova", foreground="#00d4ff")
        self.textbox.tag_config("you", foreground="#ffffff")
        self.message_queue = message_queue
        self.input_queue = input_queue

        self.my_label.bind("<Double-Button-1>", self.toggle_mini_mode)
        self.statusLabel.bind("<Double-Button-1>", self.toggle_mini_mode)
        self.bind("<Button-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.on_move)
        self.setup_tray()

    def hide_window(self):
        self.withdraw()
        self.tray_icon.visible = True

    def show_window(self):
        self.deiconify()

    def setup_tray(self):
        icon_image = Image.open("Images/NOVA_High.png")
        menu = pystray.Menu(
            pystray.MenuItem("Open NOVA", self.show_window),
        )
        self.tray_icon = pystray.Icon("NOVA", icon_image, "NOVA Assistant", menu)
        self.tray_icon.run_detached()
    
    def add_message(self, sender, text):
        self.textbox.configure(state="normal")
        if sender == "NOVA":
            self.textbox.insert("end", sender + ": " + text + "\n", "nova")
        else:
            self.textbox.insert("end", sender + ": " + text + "\n", "you")
        self.textbox.configure(state="disabled")
        self.textbox.see("end")

    def check_queue(self, message_queue):
        while not message_queue.empty():
            msg = message_queue.get()
            if msg["type"] == "message":
                self.add_message(msg["sender"], msg["text"])
            elif msg["type"] == "status":
                self.set_status(msg["value"])
        self.after(100, lambda: self.check_queue(message_queue))

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
            bar_height = random.randint(10, 60) 
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

    def handle_input(self):
        text = self.input_field.get("1.0", "end-1c").strip()
        if text:
            self.input_field.delete("1.0", "end")
            self.input_field.configure(height=35)
            self.input_queue.put({"text": text})
            self.set_status("THINKING")

    def handle_enter(self, event):
        self.handle_input()
        return "break" 

    def handle_newline(self, event):
        self.after(10, self.auto_expand) 

    def auto_expand(self, event=None):
        content = self.input_field.get("1.0", "end-1c")
        line_count = content.count('\n') + 1
        display_lines = min(line_count, 5)
        new_height = 35 + (display_lines - 1) * 20
        self.input_field.configure(height=new_height)

    def toggle_mini_mode(self, event=None):
        if not hasattr(self, "is_mini"): self.is_mini = False
        
        if not self.is_mini:
            self.is_mini = True
            
            self.my_label.pack_forget()
            self.textbox.pack_forget()
            self.input_frame.pack_forget()
            
            self.geometry("460x140") 
            self.attributes("-topmost", True)
            
            self.my_canvas.pack(expand=True, pady=10)
            self.statusLabel.pack(expand=True, pady=(0, 10))
            
        else:
            self.is_mini = False
            
            self.attributes("-topmost", False)
            self.geometry("500x500")
            
            self.statusLabel.pack_forget()
            self.my_canvas.pack_forget()
            
            self.my_label.pack(pady=5)
            self.textbox.pack(pady=5, padx=30)
            self.my_canvas.pack(pady=5)
            self.statusLabel.pack(pady=1)
            self.input_frame.pack(side="bottom", fill="x", pady=20, padx=30)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    app = Dashboard()
    app.mainloop()