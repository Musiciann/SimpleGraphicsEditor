import customtkinter as ctk

class StatusBar:
    def __init__(self, editor):
        self.editor = editor

        self.status_frame = ctk.CTkFrame(editor.root, height=32,
            corner_radius=10,
            fg_color=("#f0f0f0", "#2b2b2b"),
            border_width=1,
            border_color=("gray70", "gray25"))
        self.status_label = None
        self.coord_label = None

        self._create_widgets()

    def pack_widget(self):
        self.status_frame.pack(side="bottom", fill="x", padx=5, pady=(0, 5))

    def _create_widgets(self):
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text=f"Холст: {self.editor.canvas_width}x{self.editor.canvas_height} пикселей",
            font = ctk.CTkFont(size=12),
            text_color = ("gray20", "gray80")
        )
        self.status_label.pack(side="left", padx=10)

        self.coord_label = ctk.CTkLabel(
            self.status_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#1f6aa5", "#3b8ed0")
        )
        self.coord_label.pack(side="right", padx=10)

    def update_status(self, message):
        self.status_label.configure(text=message)

    def update_coordinates(self, x, y):
        self.coord_label.configure(text=f"X: {x}, Y: {y}")

    def clear_coordinates(self):
        self.coord_label.configure(text="")