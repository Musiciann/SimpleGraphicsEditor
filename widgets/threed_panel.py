import customtkinter as ctk
from tkinter import filedialog, messagebox
from .constants import PRIMARY_BLUE, PRIMARY_BLUE_DARK, PRIMARY_BLUE_HOVER, PRIMARY_BLUE_HOVER_DARK

class ThreeDPanel:
    def __init__(self, editor):
        self.editor = editor
        self.frame = ctk.CTkFrame(
            editor.root, width=300,
            corner_radius=15,
            border_width=2,
            border_color=("#4a4a4a", "#2b2b2b"),
            fg_color=("#2b2b2b", "#1e1e1e")
        )
        self.create_widgets()

    def create_widgets(self):
        inner = ctk.CTkFrame(self.frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(inner, text="3D Редактор",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=("#3a7eb6", "#4a8ec6")).pack(pady=(15, 10))

        self.new_btn = ctk.CTkButton(
            inner,
            text="➕ Создать новый объект",
            command=self.new_object_dialog,
            height=60,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=(PRIMARY_BLUE, PRIMARY_BLUE_DARK),
            hover_color=(PRIMARY_BLUE_HOVER, PRIMARY_BLUE_HOVER_DARK)
        )
        self.new_btn.pack(pady=10, fill="x")

        instruction = """
Управление с клавиатуры:

Перемещение:
  ← → ↑ ↓          - по X, Y (↑ вверх по экрану)
  Shift+↑ / Shift+↓ - по Z

Масштаб:
  Ctrl+← → ↑ ↓     - по X, Y
  Ctrl+Shift+↑ / ↓ - по Z

Поворот:
  r / R - вокруг X (±10°)
  t / T - вокруг Y (±10°)
  y / Y - вокруг Z (±10°)

Отражение:
  f - XY, g - XZ, h - YZ

Перспектива:
  p / P - d=20 / d=10
  o     - сброс к исходному объекту (куб)

Мышь: перетаскивание - панорама,
       колесико - масштаб
        """
        instr_label = ctk.CTkLabel(
            inner,
            text=instruction,
            justify="left",
            font=ctk.CTkFont(size=12),
            text_color=("gray70", "gray90")
        )
        instr_label.pack(pady=10, fill="x")

        btn_frame = ctk.CTkFrame(inner)
        btn_frame.pack(fill="x", pady=10)

        self.load_btn = ctk.CTkButton(
            btn_frame,
            text="Загрузить",
            command=self.load_from_file,
            height=40,
            fg_color=(PRIMARY_BLUE, PRIMARY_BLUE_DARK),
            hover_color=(PRIMARY_BLUE_HOVER, PRIMARY_BLUE_HOVER_DARK)
        )
        self.load_btn.pack(side="left", padx=5, expand=True, fill="x")

        self.save_btn = ctk.CTkButton(
            btn_frame,
            text="Сохранить",
            command=self.save_to_file,
            height=40,
            fg_color=(PRIMARY_BLUE, PRIMARY_BLUE_DARK),
            hover_color=(PRIMARY_BLUE_HOVER, PRIMARY_BLUE_HOVER_DARK)
        )
        self.save_btn.pack(side="left", padx=5, expand=True, fill="x")

        self.reset_btn = ctk.CTkButton(
            inner,
            text="Сброс вида",
            command=self.editor.threed_canvas.reset_view,
            height=40,
            fg_color="gray30",
            hover_color="gray20"
        )
        self.reset_btn.pack(pady=10, fill="x")

    def pack_widget(self):
        self.frame.pack(side="right", fill="y", padx=5, pady=5)

    def hide(self):
        self.frame.pack_forget()

    def show(self):
        self.frame.pack(side="right", fill="y", padx=5, pady=5)

    def new_object_dialog(self):
        dialog = ctk.CTkToplevel(self.editor.root)
        dialog.title("Создание 3D объекта")
        dialog.geometry("600x500")
        dialog.transient(self.editor.root)
        dialog.grab_set()
        dialog.configure(fg_color=("#2b2b2b", "#1e1e1e"))

        ctk.CTkLabel(dialog, text="Вершины (x y z), каждая на новой строке:",
                     font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(10,0))
        verts_text = ctk.CTkTextbox(dialog, height=200)
        verts_text.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(dialog, text="Ребра (индексы i j), каждая на новой строке:",
                     font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(10,0))
        edges_text = ctk.CTkTextbox(dialog, height=150)
        edges_text.pack(fill="x", padx=10, pady=5)

        def create():
            try:
                verts_data = verts_text.get("0.0", "end").strip().split('\n')
                verts = []
                for line in verts_data:
                    if line.strip():
                        parts = line.strip().split()
                        verts.append([float(parts[0]), float(parts[1]), float(parts[2])])
                edges_data = edges_text.get("0.0", "end").strip().split('\n')
                edges = []
                for line in edges_data:
                    if line.strip():
                        parts = line.strip().split()
                        edges.append((int(parts[0]), int(parts[1])))
                if not verts:
                    messagebox.showerror("Ошибка", "Нет вершин")
                    return
                self.editor.threed_canvas.set_object(verts, edges)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Неверный формат данных:\n{str(e)}")

        btn_frame = ctk.CTkFrame(dialog)
        btn_frame.pack(pady=20)
        ctk.CTkButton(btn_frame, text="Создать", command=create,
                     fg_color=(PRIMARY_BLUE, PRIMARY_BLUE_DARK),
                     hover_color=(PRIMARY_BLUE_HOVER, PRIMARY_BLUE_HOVER_DARK)).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Отмена", command=dialog.destroy).pack(side="left", padx=10)

    def load_from_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not filename:
            return
        self.editor.threed_canvas.load_from_file(filename)

    def save_to_file(self):
        if not self.editor.threed_canvas.vertices:
            messagebox.showwarning("Внимание", "Нет данных для сохранения")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not filename:
            return
        self.editor.threed_canvas.save_to_file(filename)