import customtkinter as ctk
import algorithms.transform3d as t3d
from file_options.file_options_3d import *

class ThreeDCanvas:
    def __init__(self, editor):
        self.editor = editor
        self.main_frame = None
        self.canvas = None
        self.vertices = []
        self.edges = []
        self.default_vertices = []
        self.default_edges = []
        self.view_scale = 50.0
        self.view_offset_x = 0
        self.view_offset_y = 0
        self.drag_start = None
        self.init_default_object()

    def init_default_object(self):
        self.default_vertices = [
            [-1, -1, -1], [ 1, -1, -1], [ 1,  1, -1], [-1,  1, -1],
            [-1, -1,  1], [ 1, -1,  1], [ 1,  1,  1], [-1,  1,  1]
        ]
        self.default_edges = [
            (0,1),(1,2),(2,3),(3,0),
            (4,5),(5,6),(6,7),(7,4),
            (0,4),(1,5),(2,6),(3,7)
        ]
        self.vertices = [v[:] for v in self.default_vertices]
        self.edges = self.default_edges[:]
        self.center_object()

    def center_object(self):
        if not self.vertices:
            return
        xs = [v[0] for v in self.vertices]
        ys = [v[1] for v in self.vertices]
        zs = [v[2] for v in self.vertices]
        cx = (min(xs) + max(xs)) / 2
        cy = (min(ys) + max(ys)) / 2
        cz = (min(zs) + max(zs)) / 2
        self.vertices = [[v[0]-cx, v[1]-cy, v[2]-cz] for v in self.vertices]

    def pack_widget(self):
        self.main_frame = ctk.CTkFrame(self.editor.root)
        self.main_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.canvas = ctk.CTkCanvas(
            self.main_frame,
            bg="white",
            highlightthickness=1,
            highlightbackground="gray"
        )
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.bind_keys()

    def bind_keys(self):
        self.editor.root.bind_all("<Left>", lambda e: self.translate(-1,0,0) if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("<Right>", lambda e: self.translate(1,0,0) if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("<Up>", lambda e: self.translate(0,1,0) if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("<Down>", lambda e: self.translate(0,-1,0) if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("<Shift-Up>", lambda e: self.translate(0,0,1) if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("<Shift-Down>", lambda e: self.translate(0,0,-1) if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("<Control-Left>", lambda e: self.scale(0.9,1,1) if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("<Control-Right>", lambda e: self.scale(1.1,1,1) if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("<Control-Up>", lambda e: self.scale(1,0.9,1) if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("<Control-Down>", lambda e: self.scale(1,1.1,1) if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("<Control-Shift-Up>", lambda e: self.scale(1,1,1.1) if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("<Control-Shift-Down>", lambda e: self.scale(1,1,0.9) if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("r", lambda e: self.rotate('x', 10) if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("R", lambda e: self.rotate('x', -10) if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("t", lambda e: self.rotate('y', 10) if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("T", lambda e: self.rotate('y', -10) if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("y", lambda e: self.rotate('z', 10) if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("Y", lambda e: self.rotate('z', -10) if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("f", lambda e: self.reflect('xy') if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("g", lambda e: self.reflect('xz') if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("h", lambda e: self.reflect('yz') if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("p", lambda e: self.perspective(20) if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("P", lambda e: self.perspective(10) if self.editor.mode=="3d" else None)
        self.editor.root.bind_all("o", lambda e: self.reset_to_default() if self.editor.mode=="3d" else None)

    def hide(self):
        self.main_frame.pack_forget()

    def show(self):
        self.main_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.draw()

    def translate(self, dx, dy, dz):
        mat = t3d.translation(dx, dy, dz)
        self.apply_transform(mat)

    def scale(self, sx, sy, sz):
        mat = t3d.scaling(sx, sy, sz)
        self.apply_transform(mat)

    def rotate(self, axis, angle):
        if axis == 'x':
            mat = t3d.rotation_x(angle)
        elif axis == 'y':
            mat = t3d.rotation_y(angle)
        elif axis == 'z':
            mat = t3d.rotation_z(angle)
        else:
            return
        self.apply_transform(mat)

    def reflect(self, plane):
        mat = t3d.reflection(plane)
        self.apply_transform(mat)

    def perspective(self, d):
        if d == 0:
            return
        mat = t3d.perspective(d)
        self.apply_transform(mat)

    def reset_to_default(self):
        self.vertices = [v[:] for v in self.default_vertices]
        self.edges = self.default_edges[:]
        self.center_object()
        self.draw()

    def apply_transform(self, matrix):
        self.vertices = t3d.apply_transform(self.vertices, matrix)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        if not self.vertices:
            return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            w, h = 600, 600

        points_2d = []
        for v in self.vertices:
            x = v[0] * self.view_scale + w/2 + self.view_offset_x
            y = -v[1] * self.view_scale + h/2 + self.view_offset_y
            points_2d.append((x, y))

        for (i,j) in self.edges:
            if i < len(points_2d) and j < len(points_2d):
                x1,y1 = points_2d[i]
                x2,y2 = points_2d[j]
                self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)

        for x,y in points_2d:
            self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="red", outline="")

    def on_mouse_down(self, event):
        self.drag_start = (event.x, event.y)

    def on_mouse_drag(self, event):
        if self.drag_start:
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            self.view_offset_x += dx
            self.view_offset_y += dy
            self.drag_start = (event.x, event.y)
            self.draw()

    def on_mouse_up(self, event):
        self.drag_start = None

    def on_mouse_wheel(self, event):
        if event.delta > 0:
            self.view_scale *= 1.1
        else:
            self.view_scale /= 1.1
        self.draw()

    def reset_view(self):
        self.view_scale = 50.0
        self.view_offset_x = 0
        self.view_offset_y = 0
        self.draw()

    def load_from_file(self, filename):
        try:
            verts, edges = load_from_file(filename)
            self.default_vertices = [v[:] for v in verts]
            self.default_edges = edges[:]
            self.vertices = [v[:] for v in verts]
            self.edges = edges[:]
            self.center_object()
            self.draw()
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")

    def save_to_file(self, filename):
        try:
            save_to_file(filename, self.vertices, self.edges)
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{str(e)}")

    def set_object(self, vertices, edges):
        self.default_vertices = [v[:] for v in vertices]
        self.default_edges = edges[:]
        self.vertices = [v[:] for v in vertices]
        self.edges = edges[:]
        self.center_object()
        self.draw()