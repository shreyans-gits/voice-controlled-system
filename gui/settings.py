import customtkinter as ctk
from PIL import Image
import json
import os

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, memory, notes, config_module):
        super().__init__()
        self.title("N.O.V.A. System Settings")
        self.geometry("600x800")
        self.configure(fg_color="#0a0a0f")
        
        self.attributes("-topmost", True)
        self.focus_force()

        self.memory = memory
        self.notes_module = notes
        self.config = config_module

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.render_settings()

    def render_settings(self):
        header_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=10)
        
        try:
            logo_img = ctk.CTkImage(Image.open("Images/NOVA_High.png"), size=(50, 50))
            ctk.CTkLabel(header_frame, image=logo_img, text="").pack(side="left", padx=10)
        except: pass
        
        ctk.CTkLabel(header_frame, text="System Settings", 
                     font=("Orbitron", 22, "bold"), text_color="#00ffff").pack(side="left")

        self.create_section_label("Memory Core")
        self.memory_box = ctk.CTkTextbox(self.scroll_frame, height=100, fg_color="#121212", font=("Consolas", 12))
        self.memory_box.pack(fill="x", pady=5)
        self.memory_box.insert("0.0", self.memory.summary)
        self.memory_box.configure(state="disabled")

        ctk.CTkButton(self.scroll_frame, text="Wipe Memory", fg_color="#441111", 
                      command=self.clear_memory).pack(pady=5)

        self.create_section_label("Voice Notes")
        ctk.CTkButton(self.scroll_frame, text="Clear All Notes", fg_color="#1a1a1a", 
                      command=self.clear_notes).pack(pady=5)
        self.note_status = ctk.CTkLabel(self.scroll_frame, text="", font=("Consolas", 10))
        self.note_status.pack()

        self.create_section_label("Voice Speed")
        self.speed_label = ctk.CTkLabel(self.scroll_frame, text="Speed: 0%", text_color="#aaa")
        self.speed_label.pack()
        
        self.speed_slider = ctk.CTkSlider(self.scroll_frame, from_=-50, to=50, 
                                          command=self.update_speed)
        self.speed_slider.set(0)
        if os.path.exists("settings.json"):
            with open("settings.json") as f:
                data = json.load(f)
                saved = data.get("voice_speed", "+0%")
                try:
                    val = int(saved.replace("%", "").replace("+", ""))
                    self.speed_slider.set(val)
                    self.speed_label.configure(text=f"Speed: {saved}")
                except:
                    pass
        self.speed_slider.pack(fill="x", pady=10)

        self.create_section_label("Contact Directory")
        self.contacts_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#121212")
        self.contacts_frame.pack(fill="x", padx=5, pady=5)
        
        self.contact_rows = []
        for name, num in self.config.CONTACTS.items():
            self.add_contact_row(name, num)

        ctk.CTkButton(self.scroll_frame, text="+ Add New Contact", command=lambda: self.add_contact_row(),
                      fg_color="#1a1a1a").pack(pady=5)
        
        ctk.CTkButton(self.scroll_frame, text="Save Contacts", fg_color="#00ffff", text_color="#000",
                      command=self.save_contacts).pack(pady=20)

        ctk.CTkButton(self, text="CLOSE", command=self.destroy).pack(side="bottom", pady=10)

    def create_section_label(self, text):
        ctk.CTkLabel(self.scroll_frame, text=f"— {text} —", text_color="#00ffff", 
                     font=("Consolas", 14, "bold")).pack(pady=(20, 5))

    def clear_memory(self):
        self.memory.clear()
        self.memory_box.configure(state="normal")
        self.memory_box.delete("0.0", "end")
        self.memory_box.insert("0.0", "Memory Cleared.")
        self.memory_box.configure(state="disabled")

    def clear_notes(self):
        msg = self.notes_module.clear_notes()
        self.note_status.configure(text=msg, text_color="green")

    def update_speed(self, value):
        speed = int(value)
        sign = "+" if speed >= 0 else ""
        speed_str = f"{sign}{speed}%"
        self.speed_label.configure(text=f"Speed: {speed_str}")
        
        with open("settings.json", "w") as f:
            json.dump({"voice_speed": speed_str}, f)

    def add_contact_row(self, name="", num=""):
        row = ctk.CTkFrame(self.contacts_frame, fg_color="transparent")
        row.pack(fill="x", pady=2)
        n_ent = ctk.CTkEntry(row, width=120); n_ent.insert(0, name); n_ent.pack(side="left", padx=2)
        p_ent = ctk.CTkEntry(row); p_ent.insert(0, num); p_ent.pack(side="left", fill="x", expand=True, padx=2)
        ctk.CTkButton(row, text="X", width=30, fg_color="#441111", 
                      command=lambda r=row: self.remove_row(r)).pack(side="right")
        self.contact_rows.append((row, n_ent, p_ent))

    def remove_row(self, row):
        self.contact_rows = [r for r in self.contact_rows if r[0] != row]
        row.destroy()

    def save_contacts(self):
        new_contacts = {n.get(): p.get() for _, n, p in self.contact_rows if n.get()}
        print(f"New Contacts Saved: {new_contacts}")
        self.config.CONTACTS = new_contacts
        env_path = ".env"
        with open(env_path, 'r') as f:
            lines = f.readlines()

        with open(env_path, 'w') as f:
            for line in lines:
                if line.startswith("contacts"):
                    f.write(f"contacts = {json.dumps(new_contacts)}\n")
                else:
                    f.write(line)