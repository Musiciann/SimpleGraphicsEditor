import customtkinter as ctk
from tkinter import Menu, messagebox
from widgets.tool_panel import ToolPanel
from widgets.status_bar import StatusBar
from widgets.canvas import CanvasWidget
from widgets.splash_screen import SplashScreen
from widgets.threed_panel import ThreeDPanel
from widgets.threed_canvas import ThreeDCanvas

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class GraphicsEditor:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Графический редактор")
        self.root.geometry("1200x800")

        # Настройка внешнего вида корневого окна
        self.root.configure(fg_color=("#2b2b2b", "#1e1e1e"))

        self.root.withdraw()
        self.splash = SplashScreen(self.root)
        self.splash.window.bind("<Destroy>", lambda e: self.after_splash())

        # Переменные состояния
        self.selected_algorithm = "DDA"
        self.selected_curve_type = "circle"
        self.debug_mode = False
        self.grid_visible = False
        self.start_point = None
        self.end_point = None
        self.scale_factor = 1.0
        self.current_tool = "line"
        self.canvas_created = False

        self.dragging = False
        self.last_x = 0
        self.last_y = 0
        self.view_offset_x = 0
        self.view_offset_y = 0

        self.step_pixels = []
        self.current_step = 0
        self.total_steps = 0
        self.show_all = False

        self.lines = []
        self.points = []
        self.original_width = 800
        self.original_height = 600
        self.canvas_width = 800
        self.canvas_height = 600

        self.mode = "2d"

        self.canvas_widget = CanvasWidget(self)
        self.threed_canvas = ThreeDCanvas(self)
        self.threed_panel = ThreeDPanel(self)

        self.create_menu()

        self.tool_panel = ToolPanel(self)
        self.status_bar = StatusBar(self)

        self.tool_panel.pack_widget()
        self.status_bar.pack_widget()
        self.canvas_widget.pack_widget()

        self.spline_tool = self.canvas_widget.spline_tool

        self.threed_canvas.pack_widget()
        self.threed_canvas.hide()
        self.threed_panel.pack_widget()
        self.threed_panel.hide()

    def after_splash(self):
        self.root.deiconify()

    def create_menu(self):
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новый холст", command=self.create_new_canvas_dialog)
        file_menu.add_command(label="Открыть", command=self.canvas_widget.load_canvas)
        file_menu.add_command(label="Сохранить", command=self.canvas_widget.save_canvas)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        mode_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Режим", menu=mode_menu)
        mode_menu.add_command(label="2D редактор", command=self.switch_to_2d)
        mode_menu.add_command(label="3D редактор", command=self.switch_to_3d)

        help_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)

    def switch_to_2d(self):
        if self.mode == "2d":
            return
        self.mode = "2d"
        self.threed_panel.hide()
        self.threed_canvas.hide()
        self.tool_panel.show()
        self.canvas_widget.show()

    def switch_to_3d(self):
        if self.mode == "3d":
            return
        self.mode = "3d"
        self.tool_panel.hide()
        self.canvas_widget.hide()
        self.threed_panel.show()
        self.threed_canvas.show()

    def create_new_canvas_dialog(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Создать новый холст")
        dialog.geometry("350x250")
        dialog.transient(self.root)
        dialog.grab_set()

        # Стиль диалога
        dialog.configure(fg_color=("#2b2b2b", "#1e1e1e"))

        ctk.CTkLabel(dialog, text="Размер холста",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        width_frame = ctk.CTkFrame(dialog)
        width_frame.pack(pady=5, padx=20)
        ctk.CTkLabel(width_frame, text="Ширина:", width=80).pack(side="left", padx=5)
        width_entry = ctk.CTkEntry(width_frame, width=100)
        width_entry.pack(side="left", padx=5)
        width_entry.insert(0, str(self.original_width))

        height_frame = ctk.CTkFrame(dialog)
        height_frame.pack(pady=5, padx=20)
        ctk.CTkLabel(height_frame, text="Высота:", width=80).pack(side="left", padx=5)
        height_entry = ctk.CTkEntry(height_frame, width=100)
        height_entry.pack(side="left", padx=5)
        height_entry.insert(0, str(self.original_height))

        def create():
            try:
                width = int(width_entry.get())
                height = int(height_entry.get())
                if width < 10 or height < 10:
                    messagebox.showerror("Ошибка", "Минимальный размер холста: 10x10 пикселей")
                    return
                if width > 5000 or height > 5000:
                    messagebox.showerror("Ошибка", "Максимальный размер холста: 5000x5000 пикселей")
                    return

                self.canvas_width = width
                self.canvas_height = height

                self.scale_factor = 1.0
                self.view_offset_x = 0
                self.view_offset_y = 0

                self.canvas_widget.create_canvas_area()

                self.tool_panel.debug_var.set(False)
                self.debug_mode = False

                dialog.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите целые числа для размеров холста")

        btn_frame = ctk.CTkFrame(dialog)
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="Создать", command=create,
                     fg_color=("#3a7eb6", "#1f5380"),
                     hover_color=("#4a8ec6", "#2a6390")).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Отмена", command=dialog.destroy).pack(side="left", padx=10)

    def show_about(self):
        messagebox.showinfo(
            "О программе",
            "Графический редактор\n\n"
            "Реализованы алгоритмы построения отрезков:\n"
            "1. Алгоритм ЦДА\n"
            "2. Алгоритм Брезенхема\n"
            "3. Алгоритм Ву (с антиалиасингом)\n\n"
            "Реализовано построение кривых:\n"
            "1. Окружность\n"
            "2. Эллипс\n"
            "3. Парабола\n"
            "4. Гипербола\n\n"
            "Реализовано построение параметрических кривых:\n"
            "1. Кривая Эрмита\n"
            "2. Кривая Безье\n"
            "3. B-сплайн\n\n"
            "3D редактор с матричными преобразованиями (управление с клавиатуры).\n"
            "Современный стиль на базе customtkinter.\n"
            "Версия: 0.6.1"
        )

    def run(self):
        self.root.mainloop()