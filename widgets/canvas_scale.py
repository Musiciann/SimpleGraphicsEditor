from tools import LineTool
from algorithms.algorithms import bresenham_algorithm_pixels

class CanvasScale:

    @staticmethod
    def canvas_to_screen_x(canvas_widget, canvas_x):
        screen_x = (canvas_x - canvas_widget.editor.view_center_x) * canvas_widget.editor.scale_factor + \
                   canvas_widget.editor.view_center_x + canvas_widget.editor.view_offset_x
        return screen_x

    @staticmethod
    def canvas_to_screen_y(canvas_widget, canvas_y):
        screen_y = (canvas_y - canvas_widget.editor.view_center_y) * canvas_widget.editor.scale_factor + \
                   canvas_widget.editor.view_center_y + canvas_widget.editor.view_offset_y
        return screen_y

    @staticmethod
    def screen_to_canvas_x(canvas_widget, screen_x):
        if canvas_widget.editor.scale_factor == 0:
            return 0
        canvas_x = (screen_x - canvas_widget.editor.view_center_x - canvas_widget.editor.view_offset_x) / \
                   canvas_widget.editor.scale_factor + canvas_widget.editor.view_center_x
        return int(canvas_x)

    @staticmethod
    def screen_to_canvas_y(canvas_widget, screen_y):
        if canvas_widget.editor.scale_factor == 0:
            return 0
        canvas_y = (screen_y - canvas_widget.editor.view_center_y - canvas_widget.editor.view_offset_y) / \
                   canvas_widget.editor.scale_factor + canvas_widget.editor.view_center_y
        return int(canvas_y)

    @staticmethod
    def zoom_in(self, event=None):
        if not self.editor.canvas_created:
            return

        old_scale = self.editor.scale_factor
        new_scale = min(10.0, self.editor.scale_factor * 1.2)

        if old_scale == new_scale:
            return

        if event:
            mouse_canvas_x = self.screen_to_canvas_x(event.x)
            mouse_canvas_y = self.screen_to_canvas_y(event.y)

            self.editor.scale_factor = new_scale

            new_mouse_screen_x = self.canvas_to_screen_x(mouse_canvas_x)
            new_mouse_screen_y = self.canvas_to_screen_y(mouse_canvas_y)

            dx = new_mouse_screen_x - event.x
            dy = new_mouse_screen_y - event.y

            self.editor.view_offset_x -= dx
            self.editor.view_offset_y -= dy
        else:
            self.editor.scale_factor = new_scale

        self.redraw_canvas()

    @staticmethod
    def zoom_out(self, event=None):
        if not self.editor.canvas_created:
            return

        old_scale = self.editor.scale_factor
        new_scale = max(0.1, self.editor.scale_factor / 1.2)

        if old_scale == new_scale:
            return

        if event:
            mouse_canvas_x = self.screen_to_canvas_x(event.x)
            mouse_canvas_y = self.screen_to_canvas_y(event.y)

            self.editor.scale_factor = new_scale

            new_mouse_screen_x = self.canvas_to_screen_x(mouse_canvas_x)
            new_mouse_screen_y = self.canvas_to_screen_y(mouse_canvas_y)

            dx = new_mouse_screen_x - event.x
            dy = new_mouse_screen_y - event.y

            self.editor.view_offset_x -= dx
            self.editor.view_offset_y -= dy
        else:
            self.editor.scale_factor = new_scale

        self.redraw_canvas()

    @staticmethod
    def reset_zoom(self):
        if not self.editor.canvas_created:
            return

        self.editor.scale_factor = 1.0
        self.editor.view_offset_x = 0
        self.editor.view_offset_y = 0
        self.editor.view_center_x = self.editor.canvas_width // 2
        self.editor.view_center_y = self.editor.canvas_height // 2
        self.redraw_canvas()

    @staticmethod
    def on_mouse_wheel(self, event):
        if event.delta > 0:
            self.zoom_in(event)
        else:
            self.zoom_out(event)
        return "break"

    @staticmethod
    def redraw_canvas(self):
        if not self.editor.canvas_created:
            return

        self.canvas.delete("all")

        zoom_percent = int(self.editor.scale_factor * 100)
        if hasattr(self, 'scale_label') and self.scale_label:
            self.scale_label.configure(text=f"Масштаб: {zoom_percent}%")

        self.editor.status_bar.update_status(
            f"Холст: {self.editor.original_width}x{self.editor.original_height} пикселей | Масштаб: {zoom_percent}%")

        if self.editor.grid_visible:
            self.draw_pixel_grid()

        if not self.editor.debug_mode:
            for line_info in self.editor.lines:
                for pixel in line_info['pixels']:
                    if len(pixel) == 3:
                        x, y, intensity = pixel
                        color = LineTool.get_color_from_intensity(intensity)
                    else:
                        x, y = pixel
                        color = "black"

                    screen_x = self.canvas_to_screen_x(x)
                    screen_y = self.canvas_to_screen_y(y)

                    pixel_size = max(1, self.editor.scale_factor)

                    x1 = screen_x
                    y1 = screen_y
                    x2 = screen_x + pixel_size
                    y2 = screen_y + pixel_size

                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=color, outline=color, tags="line_pixel"
                    )

            for point_info in self.editor.points:
                x, y = point_info['x'], point_info['y']
                color = point_info['color']
                tag = point_info['tag']

                screen_x = self.canvas_to_screen_x(x)
                screen_y = self.canvas_to_screen_y(y)

                pixel_size = max(1, self.editor.scale_factor)

                x1 = screen_x
                y1 = screen_y
                x2 = screen_x + pixel_size
                y2 = screen_y + pixel_size

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color, outline=color, tags=tag
                )
        else:
            for point_info in self.editor.points:
                if point_info.get('tag') in ['start', 'end']:
                    x, y = point_info['x'], point_info['y']
                    color = point_info['color']
                    tag = point_info['tag']

                    screen_x = self.canvas_to_screen_x(x)
                    screen_y = self.canvas_to_screen_y(y)

                    pixel_size = max(1, self.editor.scale_factor)

                    x1 = screen_x
                    y1 = screen_y
                    x2 = screen_x + pixel_size
                    y2 = screen_y + pixel_size

                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=color, outline=color, tags=tag
                    )

        self.canvas.delete("polygon_edge")
        self.canvas.delete("normal")
        for poly in self.editor.polygons:
            vertices = poly['vertices']
            if len(vertices) < 3:
                continue
            for i in range(len(vertices)):
                p1 = vertices[i]
                p2 = vertices[(i + 1) % len(vertices)]
                pixels = bresenham_algorithm_pixels(p1[0], p1[1], p2[0], p2[1])
                for px, py in pixels:
                    screen_x = self.canvas_to_screen_x(px)
                    screen_y = self.canvas_to_screen_y(py)
                    pixel_size = max(1, self.editor.scale_factor)
                    self.canvas.create_rectangle(
                        screen_x, screen_y,
                        screen_x + pixel_size, screen_y + pixel_size,
                        fill="black", outline="black", tags="polygon_edge"
                    )

        self.draw_current_polygon()

        self.canvas.delete("fill_pixel")
        for poly in self.editor.polygons:
            if 'fill_pixels' in poly and poly['fill_pixels']:
                for x, y in poly['fill_pixels']:
                    screen_x = self.canvas_to_screen_x(x)
                    screen_y = self.canvas_to_screen_y(y)
                    pixel_size = max(1, self.editor.scale_factor)
                    self.canvas.create_rectangle(
                        screen_x, screen_y,
                        screen_x + pixel_size, screen_y + pixel_size,
                        fill=poly['fill_color'], outline=poly['fill_color'], tags="fill_pixel"
                    )

        if self.editor.debug_mode and self.editor.total_steps > 0:
            self.draw_debug_step()