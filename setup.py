import customtkinter as ctk
from PIL import Image
import os
import sys

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SetupWizard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("N.O.V.A. Deployment Wizard")
        self.geometry("600x900")
        self.configure(fg_color="#0a0a0f")

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.contact_rows = []
        self.entries = {}
        self.render_ui()

    def render_ui(self):
        try:
            logo_img = ctk.CTkImage(Image.open("Images/NOVA_High.png"), size=(80, 80))
            logo_label = ctk.CTkLabel(self.scroll_frame, image=logo_img, text="")
            logo_label.pack(pady=(10, 0))
        except:
            pass 

        ctk.CTkLabel(self.scroll_frame, text="First Time Setup", 
                     font=("Orbitron", 24, "bold"), text_color="#00ffff").pack(pady=5)
        ctk.CTkLabel(self.scroll_frame, text="Neurally Optimized Voice Assistant", 
                     font=("Consolas", 12), text_color="#555").pack(pady=(0, 20))

        
        self.add_section("User Identity", [
            ("USER_NAME", "Your Name")
        ])

        self.add_section("API Keys", [
            ("GROQ_API_KEY", "GROQ API Key"),
            ("GEMINI_KEY", "Gemini API Key"),
            ("NEWS_API_KEY", "News API Key")
        ], is_secret=True)

        self.add_section("Voice Settings", [
            ("TTS_VOICE", "TTS Voice (en-US-AriaNeural)"),
            ("TTS_LANG", "TTS Language (en-US)")
        ])

        self.add_section("Environment", [
            ("CITY", "City")
        ])

        self.add_section("Spotify Integration", [
            ("SPOTIPY_CLIENT_ID", "Client ID"),
            ("SPOTIPY_CLIENT_SECRET", "Client Secret"),
            ("SPOTIPY_REDIRECT_URI", "Redirect URI")
        ])

        ctk.CTkLabel(self.scroll_frame, text="— Contacts —", text_color="#00ffff", 
                     font=("Consolas", 14, "bold")).pack(pady=(20, 10))
        
        self.contacts_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#121212")
        self.contacts_frame.pack(fill="x", padx=10, pady=5)
        
        self.add_contact_btn = ctk.CTkButton(self.scroll_frame, text="+ Add Contact", 
                                             command=self.add_contact_row, 
                                             fg_color="#1a1a1a", hover_color="#333")
        self.add_contact_btn.pack(pady=10)

        for _ in range(3): self.add_contact_row()

        self.save_btn = ctk.CTkButton(self, text="SAVE & DEPLOY NOVA", 
                                      command=self.save_and_exit, 
                                      height=50, font=("Consolas", 16, "bold"),
                                      fg_color="#00ffff", text_color="#000",
                                      hover_color="#00cccc")
        self.save_btn.pack(side="bottom", fill="x", padx=40, pady=20)

    def add_section(self, title, fields, is_secret=False):
        ctk.CTkLabel(self.scroll_frame, text=f"— {title} —", text_color="#00ffff", 
                     font=("Consolas", 14, "bold")).pack(pady=(15, 5))
        
        for key, label in fields:
            row = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=label, width=150, anchor="w").pack(side="left")
            
            entry = ctk.CTkEntry(row, placeholder_text=f"Enter {label}...", 
                                 show="*" if is_secret else "", fg_color="#121212")
            entry.pack(side="right", fill="x", expand=True)
            self.entries[key] = entry

    def add_contact_row(self):
        row_frame = ctk.CTkFrame(self.contacts_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=2, padx=5)
        
        name_ent = ctk.CTkEntry(row_frame, placeholder_text="Name", width=120)
        name_ent.pack(side="left", padx=2)
        
        num_ent = ctk.CTkEntry(row_frame, placeholder_text="Number (with +91)")
        num_ent.pack(side="left", fill="x", expand=True, padx=2)
        
        del_btn = ctk.CTkButton(row_frame, text="X", width=30, fg_color="#441111", 
                                command=lambda r=row_frame: self.remove_row(r))
        del_btn.pack(side="right", padx=2)
        
        self.contact_rows.append((row_frame, name_ent, num_ent))

    def remove_row(self, frame):
        self.contact_rows = [r for r in self.contact_rows if r[0] != frame]
        frame.destroy()

    def save_and_exit(self):
        try:
            contacts = {}
            for _, name_ent, num_ent in self.contact_rows:
                n, num = name_ent.get().strip(), num_ent.get().strip()
                if n and num: contacts[n] = num

            env_lines = ["# NOVA CONFIGURATION FILE\n"]
            for key, entry in self.entries.items():
                val = entry.get().strip()
                env_lines.append(f'{key} = "{val}"')
            
            env_lines.append(f'\n# Contacts Directory\nCONTACTS = {contacts}')

            with open(".env", "w") as f:
                f.write("\n".join(env_lines))

            print("Deployment successful. Self-destructing setup wizard...")
            script_path = os.path.abspath(sys.argv[0])
            self.destroy()
            os.remove(script_path) 
            sys.exit()

        except Exception as e:
            print(f"Deployment failed: {e}")

if __name__ == "__main__":
    app = SetupWizard()
    app.mainloop()