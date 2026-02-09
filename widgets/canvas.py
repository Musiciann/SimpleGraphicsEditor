import customtkinter as ctk
from tkinter import messagebox
from algorithms.algorithms import dda_algorithm_pixels, bresenham_algorithm_pixels, wu_algorithm_pixels
import json
import os
from tkinter import filedialog
from .canvas_scale import CanvasScale


class CanvasWidget:
    def __init__(self, editor):
        self.editor = editor

        self.main_frame = None
        self.canvas_frame = None
        self.canvas = None
        self.scroll_frame = None
        self.scale_label = None

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

    def create_canvas_area(self):
        if self.main_frame:
            self.main_frame.destroy()
            self.editor.lines = []
            self.editor.points = []
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

        self.canvas_frame = ctk.CTkFrame(self.main_frame)
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

        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<Motion>", self.show_coordinates)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Control-MouseWheel>", self.on_mouse_wheel)

        self.canvas.bind("<ButtonPress-2>", self.start_drag)
        self.canvas.bind("<ButtonPress-3>", self.start_drag)
        self.canvas.bind("<B2-Motion>", self.drag_canvas)
        self.canvas.bind("<B3-Motion>", self.drag_canvas)
        self.canvas.bind("<ButtonRelease-2>", self.stop_drag)
        self.canvas.bind("<ButtonRelease-3>", self.stop_drag)

        self.editor.canvas_created = True

        self.editor.status_bar.update_status(
            f"Холст: {self.editor.original_width}x{self.editor.original_height} пикселей")

        if self.editor.grid_visible:
            self.draw_pixel_grid()

        self.update_step_label()
        self.disable_step_buttons()


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

    def draw_line(self):
        if not self.editor.canvas_created or not self.editor.start_point or not self.editor.end_point:
            return

        x1, y1 = self.editor.start_point
        x2, y2 = self.editor.end_point

        if self.editor.debug_mode:
            self.editor.step_pixels = self.get_pixels_for_algorithm(x1, y1, x2, y2)
            self.editor.total_steps = len(self.editor.step_pixels)
            self.editor.current_step = 0
            self.editor.show_all = False

            self.draw_debug_step()

            self.enable_step_buttons()
            self.update_step_label()
        else:
            pixels = self.get_pixels_for_algorithm(x1, y1, x2, y2)

            line_info = {
                'type': 'line',
                'start': (x1, y1),
                'end': (x2, y2),
                'algorithm': self.editor.selected_algorithm,
                'pixels': pixels,
                'pixel_ids': []
            }

            for pixel in pixels:
                if len(pixel) == 3:
                    x, y, intensity = pixel
                    color = self.get_color_from_intensity(intensity)
                else:
                    x, y = pixel
                    color = "black"

                screen_x = self.canvas_to_screen_x(x)
                screen_y = self.canvas_to_screen_y(y)

                pixel_size = max(1, self.editor.scale_factor)

                x1_pixel = screen_x
                y1_pixel = screen_y
                x2_pixel = screen_x + pixel_size
                y2_pixel = screen_y + pixel_size

                pixel_id = self.canvas.create_rectangle(
                    x1_pixel, y1_pixel,
                    x2_pixel, y2_pixel,
                    fill=color, outline=color, tags="line_pixel"
                )
                line_info['pixel_ids'].append(pixel_id)

            self.editor.lines.append(line_info)

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

    def canvas_click(self, event):
        if not self.editor.canvas_created or self.editor.current_tool != "line":
            return

        x = self.screen_to_canvas_x(event.x)
        y = self.screen_to_canvas_y(event.y)

        if x < 0 or x >= self.editor.original_width or y < 0 or y >= self.editor.original_height:
            return

        if self.editor.start_point is None:
            if self.editor.debug_mode:
                if hasattr(self, 'canvas') and self.canvas is not None:
                    self.canvas.delete("debug")
                    self.canvas.delete("start")
                    self.canvas.delete("end")
                self.reset_step_mode()
                self.remove_debug_points()

            self.editor.start_point = (x, y)
            self.draw_pixel_point(x, y, "blue", "start")
        else:
            self.editor.end_point = (x, y)
            self.draw_pixel_point(x, y, "red", "end")

            self.draw_line()

            if not self.editor.debug_mode:
                if hasattr(self, 'canvas') and self.canvas is not None:
                    self.canvas.delete("start")
                    self.canvas.delete("end")
                self.remove_debug_points()
                self.editor.start_point = None
                self.editor.end_point = None

    def canvas_to_screen_x_for_grid(self, canvas_x):
        screen_x = (canvas_x - self.editor.view_center_x) * self.editor.scale_factor + \
                   self.editor.view_center_x + self.editor.view_offset_x
        return int(round(screen_x))

    def canvas_to_screen_y_for_grid(self, canvas_y):
        screen_y = (canvas_y - self.editor.view_center_y) * self.editor.scale_factor + \
                   self.editor.view_center_y + self.editor.view_offset_y
        return int(round(screen_y))

    def get_pixels_for_algorithm(self, x1, y1, x2, y2):
        if self.editor.selected_algorithm == "DDA":
            return dda_algorithm_pixels(x1, y1, x2, y2)
        elif self.editor.selected_algorithm == "Bresenham":
            return bresenham_algorithm_pixels(x1, y1, x2, y2)
        else:
            return wu_algorithm_pixels(x1, y1, x2, y2)

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
                    color = self.get_color_from_intensity(intensity)
                    self.draw_debug_pixel(x, y, color)
                else:
                    x, y = pixel
                    self.draw_debug_pixel(x, y, "#000000")

    @staticmethod
    def get_color_from_intensity(intensity):
        gray_value = int(255 * (1 - intensity))
        if gray_value < 0:
            gray_value = 0
        if gray_value > 255:
            gray_value = 255
        return f'#{gray_value:02x}{gray_value:02x}{gray_value:02x}'

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
        if not self.editor.canvas_created or not self.editor.lines:
            messagebox.showwarning("Внимание", "Нечего сохранять - холст пуст")
            return False

        if not filename:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[
                    ("JSON файлы", "*.json"),
                    ("Все файлы", "*.*")
                ],
                title="Сохранить холст"
            )

        if not filename:
            return False

        try:
            save_data = {
                'canvas_width': self.editor.original_width,
                'canvas_height': self.editor.original_height,
                'lines': [],
                'points': []
            }

            for line_info in self.editor.lines:
                line_data = {
                    'type': line_info['type'],
                    'start': line_info['start'],
                    'end': line_info['end'],
                    'algorithm': line_info['algorithm'],
                    'pixels': line_info['pixels']
                }
                save_data['lines'].append(line_data)

            for point_info in self.editor.points:
                point_data = {
                    'x': point_info['x'],
                    'y': point_info['y'],
                    'color': point_info['color'],
                    'tag': point_info['tag']
                }
                save_data['points'].append(point_data)

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("Успех", f"Холст сохранен в файл:\n{filename}")
            return True

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
            return False

    def load_canvas(self, filename=None):
        if not filename:
            filename = filedialog.askopenfilename(
                filetypes=[
                    ("JSON файлы", "*.json"),
                    ("Все файлы", "*.*")
                ],
                title="Открыть холст"
            )

        if not filename or not os.path.exists(filename):
            return False

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                load_data = json.load(f)

            self.editor.canvas_width = load_data['canvas_width']
            self.editor.canvas_height = load_data['canvas_height']
            self.editor.original_width = load_data['canvas_width']
            self.editor.original_height = load_data['canvas_height']

            self.editor.lines = []
            self.editor.points = []
            self.editor.start_point = None
            self.editor.end_point = None

            self.create_canvas_area()

            for line_data in load_data['lines']:
                line_info = {
                    'type': line_data['type'],
                    'start': tuple(line_data['start']),
                    'end': tuple(line_data['end']),
                    'algorithm': line_data['algorithm'],
                    'pixels': line_data['pixels'],
                    'pixel_ids': []
                }
                self.editor.lines.append(line_info)

            for point_data in load_data['points']:
                point_info = {
                    'x': point_data['x'],
                    'y': point_data['y'],
                    'color': point_data['color'],
                    'tag': point_data['tag'],
                    'id': None
                }
                self.editor.points.append(point_info)

            self.redraw_canvas()

            messagebox.showinfo("Успех", f"Холст загружен из файла:\n{filename}")
            return True

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
            return False