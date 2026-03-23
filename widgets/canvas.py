import customtkinter as ctk
from tkinter import messagebox
import math
from .canvas_scale import CanvasScale
from tools.line_tool import LineTool
from tools.curves_tool import CurvesTool
from tools.parametric_curves_tool import ParametricCurvesTool
from file_options.file_options_2d import FileOptions
from tools.polygon_tool import PolygonTool

class CanvasWidget:
    def __init__(self, editor):
        self.editor = editor
        self.line_tool = LineTool(self)
        self.curves_tool = CurvesTool(self)
        self.spline_tool = ParametricCurvesTool(self)
        self.polygon_tool = PolygonTool(self)
        self.file_options = FileOptions(self)

        self.main_frame = None
        self.canvas_frame = None
        self.canvas = None
        self.scroll_frame = None
        self.scale_label = None

        self.waiting_for_point = False

    def canvas_to_screen_x(self, canvas_x):
        return CanvasScale.canvas_to_screen_x(self, canvas_x)

    def canvas_to_screen_y(self, canvas_y):
        return CanvasScale.canvas_to_screen_y(self, canvas_y)

    def screen_to_canvas_x(self, screen_x):
        return CanvasScale.screen_to_canvas_x(self, screen_x)

    def screen_to_canvas_y(self, screen_y):
        return CanvasScale.screen_to_canvas_y(self, screen_y)

    def zoom_in(self, event=None):
        CanvasScale.zoom_in(self, event)

    def zoom_out(self, event=None):
        CanvasScale.zoom_out(self, event)

    def reset_zoom(self):
        CanvasScale.reset_zoom(self)

    def on_mouse_wheel(self, event):
        return CanvasScale.on_mouse_wheel(self, event)

    def redraw_canvas(self):
        CanvasScale.redraw_canvas(self)

    def pack_widget(self):
        self.main_frame = ctk.CTkFrame(self.editor.root)
        self.main_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    def hide(self):
        if self.main_frame:
            self.main_frame.pack_forget()

    def show(self):
        if self.main_frame:
            self.main_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        else:
            self.pack_widget()

    def create_canvas_area(self):
        if self.main_frame:
            self.main_frame.destroy()
            self.editor.lines = []
            self.editor.points = []
            self.editor.polygons = []
            self.editor.start_point = None
            self.editor.end_point = None
            self.editor.step_pixels = []
            self.editor.current_step = 0
            self.editor.total_steps = 0
            self.editor.show_all = False

        self.editor.original_width = self.editor.canvas_width
        self.editor.original_height = self.editor.canvas_height

        self.main_frame = ctk.CTkFrame(self.editor.root)
        self.main_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.canvas_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=15,
            border_width=2,
            border_color=("#4a4a4a", "#2b2b2b"),
            fg_color="transparent"
        )
        self.canvas_frame.pack(expand=True)
        info_frame = ctk.CTkFrame(self.canvas_frame)
        info_frame.pack(side="top", fill="x", pady=(0, 5))

        size_label = ctk.CTkLabel(
            info_frame,
            text=f"Размер холста: {self.editor.canvas_width} × {self.editor.canvas_height}",
            font=("Arial", 12)
        )
        size_label.pack(side="left", padx=10)

        self.scale_label = ctk.CTkLabel(
            info_frame,
            text=f"Масштаб: {int(self.editor.scale_factor * 100)}%",
            font=("Arial", 12)
        )
        self.scale_label.pack(side="right", padx=10)

        self.canvas = ctk.CTkCanvas(
            self.canvas_frame,
            width=self.editor.canvas_width,
            height=self.editor.canvas_height,
            bg="white",
            highlightthickness=1,
            highlightbackground="gray"
        )
        self.canvas.pack(padx=10, pady=10)

        self.editor.view_offset_x = 0
        self.editor.view_offset_y = 0
        self.editor.view_center_x = self.editor.canvas_width // 2
        self.editor.view_center_y = self.editor.canvas_height // 2

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.show_coordinates)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)

        self.canvas.bind("<ButtonPress-2>", self.start_drag)
        self.canvas.bind("<ButtonPress-3>", self.start_drag)
        self.canvas.bind("<B2-Motion>", self.drag_canvas)
        self.canvas.bind("<B3-Motion>", self.drag_canvas)
        self.canvas.bind("<ButtonRelease-2>", self.stop_drag)
        self.canvas.bind("<ButtonRelease-3>", self.stop_drag)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

        self.editor.canvas_created = True

        self.editor.status_bar.update_status(
            f"Холст: {self.editor.original_width}x{self.editor.original_height} пикселей")

        if self.editor.grid_visible:
            self.draw_pixel_grid()

        self.update_step_label()
        self.disable_step_buttons()

    def on_canvas_click(self, event):
        if self.waiting_for_point:
            self.test_point_inside_polygon(event)
            return
        if self.editor.current_tool == "line":
            self.line_tool.canvas_click(event)
        elif self.editor.current_tool == "curves":
            self.curves_tool.canvas_click(event)
        elif self.editor.current_tool == "spline":
            self.spline_tool.canvas_click(event)
        elif self.editor.current_tool == "polygon":
            self.polygon_tool.canvas_click(event)

    def on_canvas_drag(self, event):
        if self.editor.current_tool == "spline":
            self.spline_tool.canvas_drag(event)

    def on_canvas_release(self, event):
        if self.editor.current_tool == "spline":
            self.spline_tool.canvas_release(event)

    def draw_pixel_grid(self):
        if not self.editor.canvas_created:
            return

        self.canvas.delete("grid")

        if not self.editor.grid_visible:
            return

        for x in range(0, self.editor.original_width + 1):
            screen_x = self.canvas_to_screen_x(x)
            if -10 <= screen_x <= self.editor.canvas_width + 10:
                self.canvas.create_line(
                    screen_x, 0,
                    screen_x, self.editor.canvas_height,
                    fill="#e0e0e0",
                    tags="grid",
                    width=1
                )

        for y in range(0, self.editor.original_height + 1):
            screen_y = self.canvas_to_screen_y(y)
            if -10 <= screen_y <= self.editor.canvas_height + 10:
                self.canvas.create_line(
                    0, screen_y,
                    self.editor.canvas_width, screen_y,
                    fill="#e0e0e0",
                    tags="grid",
                    width=1
                )

    def draw_pixel_point(self, x, y, color, tag):
        if not self.editor.canvas_created:
            return

        screen_x = self.canvas_to_screen_x(x)
        screen_y = self.canvas_to_screen_y(y)

        pixel_size = max(1, self.editor.scale_factor)

        x1 = screen_x
        y1 = screen_y
        x2 = screen_x + pixel_size
        y2 = screen_y + pixel_size

        point_id = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=color, outline=color, tags=tag
        )

        self.editor.points.append({
            'id': point_id,
            'x': x,
            'y': y,
            'color': color,
            'tag': tag
        })

    def draw_debug_pixel(self, x, y, color):
        screen_x = self.canvas_to_screen_x(x)
        screen_y = self.canvas_to_screen_y(y)

        pixel_size = max(1, self.editor.scale_factor)

        x1 = screen_x
        y1 = screen_y
        x2 = screen_x + pixel_size
        y2 = screen_y + pixel_size

        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=color, outline="#404040", width=1, tags="debug"
        )

    def canvas_to_screen_x_for_grid(self, canvas_x):
        screen_x = (canvas_x - self.editor.view_center_x) * self.editor.scale_factor + \
                   self.editor.view_center_x + self.editor.view_offset_x
        return int(round(screen_x))

    def canvas_to_screen_y_for_grid(self, canvas_y):
        screen_y = (canvas_y - self.editor.view_center_y) * self.editor.scale_factor + \
                   self.editor.view_center_y + self.editor.view_offset_y
        return int(round(screen_y))

    def draw_debug_step(self):
        if not self.editor.canvas_created or not self.editor.debug_mode:
            return

        self.canvas.delete("debug")

        if not self.editor.step_pixels or self.editor.total_steps == 0:
            return

        if self.editor.show_all:
            steps_to_show = range(self.editor.total_steps)
        else:
            steps_to_show = range(self.editor.current_step + 1)

        for i in steps_to_show:
            if i < len(self.editor.step_pixels):
                pixel = self.editor.step_pixels[i]

                if len(pixel) == 3:
                    x, y, intensity = pixel
                    color = self.line_tool.get_color_from_intensity(intensity)
                    self.draw_debug_pixel(x, y, color)
                else:
                    x, y = pixel
                    self.draw_debug_pixel(x, y, "#000000")

    def first_step(self):
        if self.editor.total_steps > 0:
            self.editor.current_step = 0
            self.editor.show_all = False
            self.draw_debug_step()
            self.update_step_label()
            self.update_step_buttons_state()

    def prev_step(self):
        if self.editor.current_step > 0:
            self.editor.current_step -= 1
            self.editor.show_all = False
            self.draw_debug_step()
            self.update_step_label()
            self.update_step_buttons_state()

    def next_step(self):
        if self.editor.current_step < self.editor.total_steps - 1:
            self.editor.current_step += 1
            self.editor.show_all = False
            self.draw_debug_step()
            self.update_step_label()
            self.update_step_buttons_state()

    def last_step(self):
        if self.editor.total_steps > 0:
            self.editor.current_step = self.editor.total_steps - 1
            self.editor.show_all = False
            self.draw_debug_step()
            self.update_step_label()
            self.update_step_buttons_state()

    def toggle_show_all(self):
        self.editor.show_all = not self.editor.show_all
        if self.editor.show_all:
            self.editor.tool_panel.show_all_btn.configure(text="Показать по шагам")
        else:
            self.editor.tool_panel.show_all_btn.configure(text="Показать все")
        self.draw_debug_step()
        self.update_step_buttons_state()

    def reset_step_mode(self):
        self.editor.step_pixels = []
        self.editor.current_step = 0
        self.editor.total_steps = 0
        self.editor.show_all = False
        self.update_step_label()
        self.disable_step_buttons()

        if hasattr(self, 'canvas') and self.canvas is not None:
            self.canvas.delete("debug")

    def enable_step_buttons(self):
        self.editor.tool_panel.first_btn.configure(state="normal")
        self.editor.tool_panel.prev_btn.configure(state="normal")
        self.editor.tool_panel.next_btn.configure(state="normal")
        self.editor.tool_panel.last_btn.configure(state="normal")
        self.editor.tool_panel.show_all_btn.configure(state="normal")
        self.update_step_buttons_state()

    def disable_step_buttons(self):
        self.editor.tool_panel.first_btn.configure(state="disabled")
        self.editor.tool_panel.prev_btn.configure(state="disabled")
        self.editor.tool_panel.next_btn.configure(state="disabled")
        self.editor.tool_panel.last_btn.configure(state="disabled")
        self.editor.tool_panel.show_all_btn.configure(state="disabled")
        self.editor.tool_panel.show_all_btn.configure(text="Показать все")

    def update_step_buttons_state(self):
        if self.editor.total_steps == 0:
            self.disable_step_buttons()
            return

        self.editor.tool_panel.first_btn.configure(state="normal" if self.editor.current_step > 0 else "disabled")
        self.editor.tool_panel.prev_btn.configure(state="normal" if self.editor.current_step > 0 else "disabled")
        self.editor.tool_panel.next_btn.configure(
            state="normal" if self.editor.current_step < self.editor.total_steps - 1 else "disabled")
        self.editor.tool_panel.last_btn.configure(
            state="normal" if self.editor.current_step < self.editor.total_steps - 1 else "disabled")

        if self.editor.show_all:
            self.editor.tool_panel.show_all_btn.configure(text="Показать по шагам")
        else:
            self.editor.tool_panel.show_all_btn.configure(text="Показать все")

    def update_step_label(self):
        if self.editor.total_steps > 0:
            self.editor.tool_panel.step_label.configure(
                text=f"{self.editor.current_step + 1}/{self.editor.total_steps}")
        else:
            self.editor.tool_panel.step_label.configure(text="0/0")

    def start_drag(self, event):
        if not self.editor.canvas_created:
            return

        self.editor.dragging = True
        self.editor.drag_start_x = event.x
        self.editor.drag_start_y = event.y
        self.editor.drag_start_offset_x = self.editor.view_offset_x
        self.editor.drag_start_offset_y = self.editor.view_offset_y
        self.canvas.configure(cursor="fleur")

    def drag_canvas(self, event):
        if not self.editor.canvas_created or not self.editor.dragging:
            return

        dx = event.x - self.editor.drag_start_x
        dy = event.y - self.editor.drag_start_y

        self.editor.view_offset_x = self.editor.drag_start_offset_x + dx
        self.editor.view_offset_y = self.editor.drag_start_offset_y + dy

        self.redraw_canvas()

    def stop_drag(self, event):
        self.editor.dragging = False
        self.canvas.configure(cursor="")

    def reset_view(self):
        if not self.editor.canvas_created:
            return

        self.editor.scale_factor = 1.0
        self.editor.view_offset_x = 0
        self.editor.view_offset_y = 0
        self.editor.view_center_x = self.editor.canvas_width // 2
        self.editor.view_center_y = self.editor.canvas_height // 2
        self.redraw_canvas()

    def show_coordinates(self, event):
        if not self.editor.canvas_created:
            return

        canvas_x = self.screen_to_canvas_x(event.x)
        canvas_y = self.screen_to_canvas_y(event.y)

        if 0 <= canvas_x < self.editor.original_width and 0 <= canvas_y < self.editor.original_height:
            self.editor.status_bar.update_coordinates(canvas_x, canvas_y)
        else:
            self.editor.status_bar.clear_coordinates()

    def clear_canvas(self):
        if not self.editor.canvas_created:
            return

        self.canvas.delete("all")
        self.editor.start_point = None
        self.editor.end_point = None
        self.reset_step_mode()

        self.editor.lines = []
        self.editor.points = []
        self.editor.polygons = []

        if self.editor.grid_visible:
            self.draw_pixel_grid()

    def toggle_debug_mode(self):
        if not self.editor.canvas_created:
            self.editor.tool_panel.debug_var.set(False)
            self.editor.debug_mode = False
            messagebox.showwarning("Внимание", "Сначала создайте холст")
            return

        old_debug_mode = self.editor.debug_mode
        self.editor.debug_mode = self.editor.tool_panel.debug_var.get()

        if old_debug_mode != self.editor.debug_mode:
            if not self.editor.debug_mode:
                self.reset_step_mode()

                self.remove_debug_points()

                if hasattr(self, 'canvas') and self.canvas is not None:
                    self.canvas.delete("debug")
                    self.canvas.delete("start")
                    self.canvas.delete("end")

                self.editor.start_point = None
                self.editor.end_point = None

                self.disable_step_buttons()
            else:
                self.editor.tool_panel.debug_checkbox.configure(state="normal")
                if hasattr(self, 'canvas') and self.canvas is not None:
                    self.canvas.delete("debug")
                self.reset_step_mode()
                self.remove_debug_points()

        if hasattr(self, 'canvas') and self.canvas is not None:
            self.redraw_canvas()

    def remove_debug_points(self):
        if not hasattr(self.editor, 'points'):
            return

        non_debug_points = []
        for point in self.editor.points:
            if point.get('tag') not in ['start', 'end']:
                non_debug_points.append(point)
            else:
                if point.get('id') and hasattr(self, 'canvas') and self.canvas is not None:
                    self.canvas.delete(point['id'])

        self.editor.points = non_debug_points

    def toggle_grid(self):
        if not self.editor.canvas_created:
            self.editor.tool_panel.grid_var.set(False)
            messagebox.showwarning("Внимание", "Сначала создайте холст")
            return

        self.editor.grid_visible = self.editor.tool_panel.grid_var.get()
        self.redraw_canvas()

    def save_canvas(self, filename=None):
        return self.file_options.save_canvas(filename)

    def load_canvas(self, filename=None):
        return self.file_options.load_canvas(filename)

    def finish_polygon(self):
        self.polygon_tool.finish_polygon()

    def clear_polygons(self):
        for poly in self.editor.polygons:
            for pid in poly.get('pixel_ids', []):
                self.canvas.delete(pid)
        self.editor.polygons = []
        self.polygon_tool.clear_polygon_points()
        self.editor.status_bar.update_status("Все полигоны удалены")
        self.redraw_canvas()

    def test_point_inside_polygon(self, event):
        self.waiting_for_point = False
        x = self.screen_to_canvas_x(event.x)
        y = self.screen_to_canvas_y(event.y)
        point = (x, y)
        if not self.editor.polygons:
            self.editor.status_bar.update_status("Нет полигонов для проверки")
            return
        poly = self.editor.polygons[-1]
        inside = self.polygon_tool.point_in_polygon(point, poly['vertices'])
        msg = f"Точка ({x}, {y}) {'внутри' if inside else 'снаружи'} полигона"
        self.editor.status_bar.update_status(msg)
        self.draw_intersection_point(x, y, "green" if inside else "red")

    def draw_intersection_point(self, x, y, color):
        screen_x = self.canvas_to_screen_x(x)
        screen_y = self.canvas_to_screen_y(y)
        r = 3
        self.canvas.create_oval(
            screen_x - r, screen_y - r,
            screen_x + r, screen_y + r,
            fill=color, outline=color, tags="intersection"
        )

    def build_convex_hull_graham(self):
        self.build_convex_hull('graham')

    def build_convex_hull_jarvis(self):
        self.build_convex_hull('jarvis')

    def build_convex_hull(self, algorithm='graham'):
        if not self.editor.polygons:
            self.editor.status_bar.update_status("Сначала создайте полигон")
            return
        poly = self.editor.polygons[-1]
        points = poly['vertices']
        if algorithm == 'graham':
            hull = self.polygon_tool.graham_scan(points)
        else:
            hull = self.polygon_tool.jarvis_march(points)
        if len(hull) < 3:
            self.editor.status_bar.update_status("Не удалось построить выпуклую оболочку")
            return
        hull_info = {
            'type': 'polygon',
            'vertices': hull,
            'convex': True,
            'normals': [],
            'pixel_ids': []
        }
        self.editor.polygons.append(hull_info)
        self.polygon_tool.draw_polygon(hull_info)
        self.editor.status_bar.update_status(f"Выпуклая оболочка построена ({algorithm})")
        self.redraw_canvas()

    def check_polygon_convexity(self):
        if not self.editor.polygons:
            self.editor.status_bar.update_status("Нет полигонов")
            return
        poly = self.editor.polygons[-1]
        convex = self.polygon_tool.compute_convexity(poly)
        self.editor.status_bar.update_status(f"Полигон {'выпуклый' if convex else 'вогнутый'}")

    def show_internal_normals(self):
        if not self.editor.polygons:
            return
        poly = self.editor.polygons[-1]
        if not self.polygon_tool.compute_convexity(poly):
            self.editor.status_bar.update_status("Внутренние нормали можно вычислить только для выпуклого полигона")
            return
        normals = self.polygon_tool.compute_internal_normals(poly)
        vertices = poly['vertices']
        for i, (nx, ny) in enumerate(normals):
            p1 = vertices[i]
            p2 = vertices[(i+1) % len(vertices)]
            mx = (p1[0] + p2[0]) / 2
            my = (p1[1] + p2[1]) / 2
            screen_mx = self.canvas_to_screen_x(mx)
            screen_my = self.canvas_to_screen_y(my)
            scale = 15 / self.editor.scale_factor
            end_x = screen_mx + nx * scale
            end_y = screen_my + ny * scale
            self.canvas.create_line(screen_mx, screen_my, end_x, end_y, fill="red", width=2, tags="normal")
            angle = math.atan2(ny, nx)
            head_len = 5
            head_angle = math.pi/6
            x1 = end_x - head_len * math.cos(angle + head_angle)
            y1 = end_y - head_len * math.sin(angle + head_angle)
            x2 = end_x - head_len * math.cos(angle - head_angle)
            y2 = end_y - head_len * math.sin(angle - head_angle)
            self.canvas.create_line(end_x, end_y, x1, y1, fill="red", tags="normal")
            self.canvas.create_line(end_x, end_y, x2, y2, fill="red", tags="normal")
        self.editor.status_bar.update_status("Внутренние нормали отображены (красные стрелки)")

    def check_last_line_intersection(self):
        line_info = None
        for l in reversed(self.editor.lines):
            if l.get('type') == 'line':
                line_info = l
                break
        if not line_info:
            self.editor.status_bar.update_status("Нет нарисованных отрезков")
            return
        if not self.editor.polygons:
            self.editor.status_bar.update_status("Нет полигонов")
            return
        seg = (line_info['start'], line_info['end'])
        poly = self.editor.polygons[-1]
        intersections = self.polygon_tool.segment_intersect_polygon(seg, poly['vertices'])
        if intersections:
            msg = "Точки пересечения: " + ", ".join(f"({int(x)},{int(y)})" for x,y in intersections)
            self.editor.status_bar.update_status(msg)
            for x,y in intersections:
                self.draw_intersection_point(x, y, "orange")
        else:
            self.editor.status_bar.update_status("Пересечений нет")

    def draw_current_polygon(self):
        if self.editor.current_tool == "polygon" and self.polygon_tool.points:
            self.polygon_tool.draw_current_polygon()