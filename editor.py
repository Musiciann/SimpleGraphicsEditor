import customtkinter as ctk
from tkinter import Menu, messagebox
from widgets.tool_panel import ToolPanel
from widgets.status_bar import StatusBar
from widgets.canvas import CanvasWidget

class GraphicsEditor:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Графический редактор")
        self.root.geometry("1200x800")

        self.selected_algorithm = "DDA"
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

        self.canvas_widget = CanvasWidget(self)
        self.create_menu()

        self.tool_panel = ToolPanel(self)
        self.status_bar = StatusBar(self)

        self.tool_panel.pack_widget()
        self.status_bar.pack_widget()
        self.canvas_widget.pack_widget()

    def create_menu(self):
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новый холст", command=self.create_new_canvas_dialog)
        file_menu.add_command(label="Открыть", command= self.canvas_widget.load_canvas)
        file_menu.add_command(label="Сохранить", command=self.canvas_widget.save_canvas)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        help_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)

    def create_new_canvas_dialog(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Создать новый холст")
        dialog.geometry("350x250")
        dialog.transient(self.root)
        dialog.grab_set()

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

        ctk.CTkButton(btn_frame, text="Создать", command=create).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Отмена", command=dialog.destroy).pack(side="left", padx=10)

    def show_about(self):
        messagebox.showinfo(
            "О программе",
            "Графический редактор\n\n"
            "Реализованы алгоритмы построения отрезков:\n"
            "1. Алгоритм ЦДА (Digital Differential Analyzer)\n"
            "2. Алгоритм Брезенхема (целочисленный)\n"
            "3. Алгоритм Ву (с антиалиасингом)\n\n"
            "Версия: 0.2.2"
        )

    def run(self):
        self.root.mainloop()