import customtkinter as ctk
from tkinter import messagebox
from algorithms.algorithms import dda_algorithm_pixels, bresenham_algorithm_pixels, wu_algorithm_pixels


class CanvasWidget:
    def __init__(self, editor):
        self.editor = editor

        self.main_frame = None
        self.canvas_frame = None
        self.canvas = None

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
            self.reset_step_mode()

        self.editor.original_width = self.editor.canvas_width
        self.editor.original_height = self.editor.canvas_height

        view_width = int(self.editor.original_width * self.editor.scale_factor)
        view_height = int(self.editor.original_height * self.editor.scale_factor)

        self.main_frame = ctk.CTkFrame(self.editor.root)
        self.main_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.canvas_frame = ctk.CTkFrame(self.main_frame)
        self.canvas_frame.pack(fill="both", expand=True)

        self.canvas = ctk.CTkCanvas(
            self.canvas_frame,
            width=view_width,
            height=view_height,
            bg="white",
            highlightthickness=1,
            highlightbackground="gray"
        )
        self.canvas.pack(fill="both", expand=True)

        self.canvas.config(scrollregion=(0, 0, view_width, view_height))

        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<Motion>", self.show_coordinates)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", self.on_mouse_wheel_up)
        self.canvas.bind("<Button-5>", self.on_mouse_wheel_down)

        self.canvas.bind("<ButtonPress-2>", self.start_drag)
        self.canvas.bind("<ButtonPress-3>", self.start_drag)
        self.canvas.bind("<B2-Motion>", self.drag_canvas)
        self.canvas.bind("<B3-Motion>", self.drag_canvas)
        self.canvas.bind("<ButtonRelease-2>", self.stop_drag)
        self.canvas.bind("<ButtonRelease-3>", self.stop_drag)

        self.editor.canvas_created = True
        self.editor.view_offset_x = 0
        self.editor.view_offset_y = 0

        self.editor.status_bar.update_status(
            f"Холст: {self.editor.original_width}x{self.editor.original_height} пикселей")

        if self.editor.grid_visible:
            self.draw_pixel_grid()

    def draw_pixel_grid(self):
        if not self.editor.canvas_created:
            return

        self.canvas.delete("grid")

        if not self.editor.grid_visible:
            return

        view_width = int(self.editor.original_width * self.editor.scale_factor)
        view_height = int(self.editor.original_height * self.editor.scale_factor)

        for x in range(0, self.editor.original_width + 1):
            screen_x = int(x * self.editor.scale_factor)
            self.canvas.create_line(
                screen_x, 0, screen_x, view_height,
                fill="#e0e0e0", tags="grid", width=1
            )

        for y in range(0, self.editor.original_height + 1):
            screen_y = int(y * self.editor.scale_factor)
            self.canvas.create_line(
                0, screen_y, view_width, screen_y,
                fill="#e0e0e0", tags="grid", width=1
            )

    def canvas_click(self, event):
        if not self.editor.canvas_created or self.editor.current_tool != "line":
            return

        x = int(event.x / self.editor.scale_factor)
        y = int(event.y / self.editor.scale_factor)

        if x < 0 or x >= self.editor.original_width or y < 0 or y >= self.editor.original_height:
            return

        if self.editor.start_point is None:
            if self.editor.debug_mode:
                self.canvas.delete("debug")
                self.canvas.delete("start")
                self.canvas.delete("end")
                self.reset_step_mode()

            self.editor.start_point = (x, y)
            self.draw_pixel_point(x, y, "blue", "start")
        else:
            self.editor.end_point = (x, y)
            self.draw_pixel_point(x, y, "red", "end")
            self.draw_line()
            self.editor.start_point = None
            self.editor.end_point = None

    def draw_pixel_point(self, x, y, color, tag):
        if not self.editor.canvas_created:
            return

        screen_x = int(x * self.editor.scale_factor)
        screen_y = int(y * self.editor.scale_factor)

        point_size = max(1, int(self.editor.scale_factor))

        point_id = self.canvas.create_rectangle(
            screen_x, screen_y,
            screen_x + point_size, screen_y + point_size,
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

                screen_x = int(x * self.editor.scale_factor)
                screen_y = int(y * self.editor.scale_factor)
                pixel_size = max(1, int(self.editor.scale_factor))

                pixel_id = self.canvas.create_rectangle(
                    screen_x, screen_y,
                    screen_x + pixel_size, screen_y + pixel_size,
                    fill=color, outline=color, tags="line_pixel"
                )
                line_info['pixel_ids'].append(pixel_id)

            self.editor.lines.append(line_info)

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

    def draw_debug_pixel(self, x, y, color):
        screen_x = int(x * self.editor.scale_factor)
        screen_y = int(y * self.editor.scale_factor)
        pixel_size = max(1, int(self.editor.scale_factor))

        self.canvas.create_rectangle(
            screen_x, screen_y,
            screen_x + pixel_size, screen_y + pixel_size,
            fill=color, outline="#404040", width=1, tags="debug"
        )

    def get_color_from_intensity(self, intensity):
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

    def zoom_in(self):
        if not self.editor.canvas_created:
            return

        old_scale = self.editor.scale_factor
        self.editor.scale_factor = min(10.0, self.editor.scale_factor * 1.2)

        if old_scale != self.editor.scale_factor:
            self.redraw_canvas()

    def zoom_out(self):
        if not self.editor.canvas_created:
            return

        old_scale = self.editor.scale_factor
        self.editor.scale_factor = max(0.1, self.editor.scale_factor / 1.2)

        if old_scale != self.editor.scale_factor:
            self.redraw_canvas()

    def reset_zoom(self):
        if not self.editor.canvas_created:
            return

        self.editor.scale_factor = 1.0
        self.editor.view_offset_x = 0
        self.editor.view_offset_y = 0
        self.redraw_canvas()

    def on_mouse_wheel(self, event):
        if event.state & 0x4:
            if event.delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            return "break"
        else:
            if event.state & 0x1:
                self.canvas.xview_scroll(-1 * (event.delta // 120), "units")
            else:
                self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def on_mouse_wheel_up(self, event):
        self.zoom_in()

    def on_mouse_wheel_down(self, event):
        self.zoom_out()

    def redraw_canvas(self):
        if not self.editor.canvas_created:
            return

        view_width = int(self.editor.original_width * self.editor.scale_factor)
        view_height = int(self.editor.original_height * self.editor.scale_factor)

        self.canvas.config(width=view_width, height=view_height)
        self.canvas.config(scrollregion=(0, 0, view_width, view_height))

        self.canvas.delete("all")

        zoom_percent = int(self.editor.scale_factor * 100)
        self.editor.tool_panel.zoom_label.configure(text=f"{zoom_percent}%")
        self.editor.status_bar.update_status(
            f"Холст: {self.editor.original_width}x{self.editor.original_height} пикселей | Масштаб: {zoom_percent}%")

        if self.editor.grid_visible:
            self.draw_pixel_grid()

        for line_info in self.editor.lines:
            for pixel in line_info['pixels']:
                if len(pixel) == 3:
                    x, y, intensity = pixel
                    color = self.get_color_from_intensity(intensity)
                else:
                    x, y = pixel
                    color = "black"

                screen_x = int(x * self.editor.scale_factor)
                screen_y = int(y * self.editor.scale_factor)
                pixel_size = max(1, int(self.editor.scale_factor))

                self.canvas.create_rectangle(
                    screen_x, screen_y,
                    screen_x + pixel_size, screen_y + pixel_size,
                    fill=color, outline=color, tags="line_pixel"
                )

        for point_info in self.editor.points:
            x, y = point_info['x'], point_info['y']
            color = point_info['color']
            tag = point_info['tag']

            screen_x = int(x * self.editor.scale_factor)
            screen_y = int(y * self.editor.scale_factor)
            point_size = max(1, int(self.editor.scale_factor))

            self.canvas.create_rectangle(
                screen_x, screen_y,
                screen_x + point_size, screen_y + point_size,
                fill=color, outline=color, tags=tag
            )

        if self.editor.debug_mode and self.editor.total_steps > 0:
            self.draw_debug_step()

    def start_drag(self, event):
        if not self.editor.canvas_created:
            return

        self.editor.dragging = True
        self.editor.last_x = event.x
        self.editor.last_y = event.y
        self.canvas.configure(cursor="fleur")

    def drag_canvas(self, event):
        if not self.editor.canvas_created or not self.editor.dragging:
            return

        dx = event.x - self.editor.last_x
        dy = event.y - self.editor.last_y

        self.canvas.xview_scroll(-dx, "units")
        self.canvas.yview_scroll(-dy, "units")

        self.editor.last_x = event.x
        self.editor.last_y = event.y
        self.editor.view_offset_x += dx
        self.editor.view_offset_y += dy

    def stop_drag(self, event):
        self.editor.dragging = False
        self.canvas.configure(cursor="")

    def reset_view(self):
        if not self.editor.canvas_created:
            return

        self.editor.scale_factor = 1.0
        self.editor.view_offset_x = 0
        self.editor.view_offset_y = 0
        self.redraw_canvas()

    def show_coordinates(self, event):
        if not self.editor.canvas_created:
            return

        canvas_x = int(event.x / self.editor.scale_factor)
        canvas_y = int(event.y / self.editor.scale_factor)

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

        self.editor.debug_mode = self.editor.tool_panel.debug_var.get()

        if self.editor.debug_mode:
            self.editor.tool_panel.debug_checkbox.configure(state="normal")
        else:
            self.disable_step_buttons()
            self.reset_step_mode()

        self.redraw_canvas()

    def toggle_grid(self):
        if not self.editor.canvas_created:
            self.editor.tool_panel.grid_var.set(False)
            messagebox.showwarning("Внимание", "Сначала создайте холст")
            return

        self.editor.grid_visible = self.editor.tool_panel.grid_var.get()
        self.draw_pixel_grid()
        self.redraw_canvas()