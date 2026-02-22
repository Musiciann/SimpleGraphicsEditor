import math
from algorithms.algorithms import (
    bresenham_circle_pixels,
    bresenham_ellipse_pixels,
    bresenham_parabola_pixels,
    bresenham_hyperbola_pixels,
    rotate_pixels,
    interpolate_pixels
)

class CurvesTool:
    def __init__(self, canvas_widget):
        self.canvas_widget = canvas_widget
        self.editor = canvas_widget.editor
        self.clicks = 0
        self.points = []
        self.params = {}

    def canvas_click(self, event):
        if not self.editor.canvas_created or self.editor.current_tool != "curves":
            return

        x = self.canvas_widget.screen_to_canvas_x(event.x)
        y = self.canvas_widget.screen_to_canvas_y(event.y)

        curve_type = self.editor.selected_curve_type

        if self.clicks == 0:
            self.points = []
            if self.editor.debug_mode:
                self.canvas_widget.reset_step_mode()
                self.canvas_widget.remove_debug_points()
                if hasattr(self.canvas_widget, 'canvas') and self.canvas_widget.canvas is not None:
                    self.canvas_widget.canvas.delete("debug")
            self.canvas_widget.canvas.delete("input_point")

        self.points.append((x, y))
        self.canvas_widget.draw_pixel_point(x, y, "green", "input_point")

        if curve_type == "circle":
            if self.clicks == 0:
                self.editor.status_bar.update_status("Окружность: выберите точку радиуса")
                self.clicks = 1
            else:
                cx, cy = self.points[0]
                r = int(((x - cx) ** 2 + (y - cy) ** 2) ** 0.5)
                self.params = {'cx': cx, 'cy': cy, 'r': r}
                self.execute_draw()
                self.finish_tool()

        elif curve_type == "ellipse":
            if self.clicks == 0:
                self.editor.status_bar.update_status("Эллипс: выберите конец полуоси A (горизонтальной)")
                self.clicks = 1
            elif self.clicks == 1:
                self.editor.status_bar.update_status("Эллипс: выберите конец полуоси B (вертикальной)")
                self.clicks = 2
            else:
                cx, cy = self.points[0]
                a = abs(self.points[1][0] - cx)
                b = abs(self.points[2][1] - cy)
                self.params = {'cx': cx, 'cy': cy, 'a': a, 'b': b}
                self.execute_draw()
                self.finish_tool()

        elif curve_type == "parabola":
            if self.clicks == 0:
                self.editor.status_bar.update_status("Парабола: выберите направление (точка фокуса/вектор)")
                self.clicks = 1
            else:
                vx, vy = self.points[0]
                ux, uy = self.points[1]

                dist = math.sqrt((ux - vx) ** 2 + (uy - vy) ** 2)
                p = dist
                if p < 1: p = 1

                angle = math.atan2(uy - vy, ux - vx)

                self.params = {'cx': vx, 'cy': vy, 'p': int(p), 'angle': angle}
                self.execute_draw()
                self.finish_tool()

        elif curve_type == "hyperbola":
            if self.clicks == 0:
                self.editor.status_bar.update_status("Гипербола: выберите точку полуоси a (направление)")
                self.clicks = 1
            elif self.clicks == 1:
                self.editor.status_bar.update_status("Гипербола: выберите точку полуоси b")
                self.clicks = 2
            else:
                cx, cy = self.points[0]
                ax, ay = self.points[1]
                bx, by = self.points[2]

                a = math.sqrt((ax - cx) ** 2 + (ay - cy) ** 2)
                b = math.sqrt((bx - cx) ** 2 + (by - cy) ** 2)

                angle = math.atan2(ay - cy, ax - cx)

                self.params = {'cx': cx, 'cy': cy, 'a': int(a), 'b': int(b), 'angle': angle}
                self.execute_draw()
                self.finish_tool()

    def execute_draw(self):
        curve_type = self.editor.selected_curve_type
        pixels = []

        if curve_type == "circle":
            pixels = bresenham_circle_pixels(self.params['cx'], self.params['cy'], self.params['r'])

        elif curve_type == "ellipse":
            pixels = bresenham_ellipse_pixels(self.params['cx'], self.params['cy'], self.params['a'], self.params['b'])

        elif curve_type == "parabola":
            branches = bresenham_parabola_pixels(self.params['p'])
            all_pixels = []
            for branch in branches:
                rotated = rotate_pixels(branch, self.params['angle'], 0, 0)
                shifted = [(x + self.params['cx'], y + self.params['cy']) for x, y in rotated]
                interpolated = interpolate_pixels(shifted)
                all_pixels.extend(interpolated)
            pixels = all_pixels

        elif curve_type == "hyperbola":
            branches = bresenham_hyperbola_pixels(self.params['a'], self.params['b'])
            all_pixels = []
            for branch in branches:
                rotated = rotate_pixels(branch, self.params['angle'], 0, 0)
                shifted = [(x + self.params['cx'], y + self.params['cy']) for x, y in rotated]
                interpolated = interpolate_pixels(shifted)
                all_pixels.extend(interpolated)
            pixels = all_pixels

        filtered_pixels = []
        for px, py in pixels:
            if 0 <= px < self.editor.original_width and 0 <= py < self.editor.original_height:
                filtered_pixels.append((px, py))

        if self.editor.debug_mode:
            self.editor.step_pixels = filtered_pixels
            self.editor.total_steps = len(filtered_pixels)
            self.editor.current_step = 0
            self.editor.show_all = False

            self.canvas_widget.draw_debug_step()
            self.canvas_widget.enable_step_buttons()
            self.canvas_widget.update_step_label()
            self.canvas_widget.canvas.delete("input_point")
        else:
            self.draw_immediately(filtered_pixels)
            self.canvas_widget.canvas.delete("input_point")
            self.canvas_widget.remove_debug_points()

    def draw_immediately(self, pixels):
        curve_info = {
            'type': self.editor.selected_curve_type,
            'params': self.params,
            'pixels': pixels,
            'algorithm': 'Bresenham',
            'pixel_ids': []
        }

        color = "black"

        for px, py in pixels:
            screen_x = self.canvas_widget.canvas_to_screen_x(px)
            screen_y = self.canvas_widget.canvas_to_screen_y(py)
            pixel_size = max(1, self.editor.scale_factor)

            pid = self.canvas_widget.canvas.create_rectangle(
                screen_x, screen_y,
                screen_x + pixel_size, screen_y + pixel_size,
                fill=color, outline=color, tags="curve_pixel"
            )
            curve_info['pixel_ids'].append(pid)

        self.editor.lines.append(curve_info)

    def finish_tool(self):
        self.clicks = 0
        self.points = []
        self.params = {}