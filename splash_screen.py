import customtkinter as ctk
from PIL import Image
import os

class SplashScreen:

    def __init__(self, parent):
        self.parent = parent
        self.window = ctk.CTkToplevel(parent)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)

        self.window.configure(fg_color=("#f0f0f0", "#2b2b2b"))

        width, height = 500, 300
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")

        main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        image_path = self.find_image("assets/temp_logo.png")
        if image_path and os.path.exists(image_path):
            pil_image = Image.open(image_path)
            pil_image = pil_image.resize((150, 150), Image.Resampling.LANCZOS)
            self.logo_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(150, 150))
            image_label = ctk.CTkLabel(main_frame, image=self.logo_image, text="")
            image_label.pack(pady=(0, 10))
        else:
            placeholder = ctk.CTkLabel(main_frame, text="🎨", font=ctk.CTkFont(size=80))
            placeholder.pack(pady=(0, 10))

        welcome_label = ctk.CTkLabel(
            main_frame,
            text="Добро пожаловать в\nГрафический редактор",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#1f6aa5", "#3b8ed0")
        )
        welcome_label.pack(pady=(0, 10))

        version_label = ctk.CTkLabel(
            main_frame,
            text="Версия 0.2.3",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        )
        version_label.pack(pady=(0, 5))

        info_label = ctk.CTkLabel(
            main_frame,
            text="Загрузка...",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color=("gray50", "gray70")
        )
        info_label.pack()

        self.window.after(2000, self.fade_out)

        main_frame.bind("<Button-1>", lambda e: self.close())
        for child in main_frame.winfo_children():
            child.bind("<Button-1>", lambda e: self.close())

    def find_image(self, filename):
        search_paths = [
            os.path.join(os.path.dirname(__file__), "assets", filename),
            os.path.join(os.path.dirname(__file__), filename),
            os.path.join(os.getcwd(), "assets", filename),
            os.path.join(os.getcwd(), filename),
        ]
        for path in search_paths:
            if os.path.exists(path):
                return path
        return None

    def fade_out(self, step=0):
        opacity = 1.0 - step * 0.1
        if opacity > 0:
            self.window.attributes("-alpha", opacity)
            self.window.after(50, self.fade_out, step + 1)
        else:
            self.close()

    def close(self):
        self.window.destroy()