from algorithms.algorithms import dda_algorithm_pixels, bresenham_algorithm_pixels, wu_algorithm_pixels


class LineTool:
    def __init__(self, canvas_widget):
        self.canvas_widget = canvas_widget
        self.editor = canvas_widget.editor

    def canvas_click(self, event):
        if not self.editor.canvas_created or self.editor.current_tool != "line":
            return

        x = self.canvas_widget.screen_to_canvas_x(event.x)
        y = self.canvas_widget.screen_to_canvas_y(event.y)

        if x < 0 or x >= self.editor.original_width or y < 0 or y >= self.editor.original_height:
            return

        if self.editor.start_point is None:
            if self.editor.debug_mode:
                if hasattr(self.canvas_widget, 'canvas') and self.canvas_widget.canvas is not None:
                    self.canvas_widget.canvas.delete("debug")
                    self.canvas_widget.canvas.delete("start")
                    self.canvas_widget.canvas.delete("end")
                self.canvas_widget.reset_step_mode()
                self.canvas_widget.remove_debug_points()

            self.editor.start_point = (x, y)
            self.canvas_widget.draw_pixel_point(x, y, "blue", "start")
        else:
            self.editor.end_point = (x, y)
            self.canvas_widget.draw_pixel_point(x, y, "red", "end")

            self.draw_line()

            if not self.editor.debug_mode:
                if hasattr(self.canvas_widget, 'canvas') and self.canvas_widget.canvas is not None:
                    self.canvas_widget.canvas.delete("start")
                    self.canvas_widget.canvas.delete("end")
                self.canvas_widget.remove_debug_points()
                self.editor.start_point = None
                self.editor.end_point = None

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

            self.canvas_widget.draw_debug_step()

            self.canvas_widget.enable_step_buttons()
            self.canvas_widget.update_step_label()
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

                screen_x = self.canvas_widget.canvas_to_screen_x(x)
                screen_y = self.canvas_widget.canvas_to_screen_y(y)

                pixel_size = max(1, self.editor.scale_factor)

                x1_pixel = screen_x
                y1_pixel = screen_y
                x2_pixel = screen_x + pixel_size
                y2_pixel = screen_y + pixel_size

                pixel_id = self.canvas_widget.canvas.create_rectangle(
                    x1_pixel, y1_pixel,
                    x2_pixel, y2_pixel,
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

    @staticmethod
    def get_color_from_intensity(intensity):
        gray_value = int(255 * (1 - intensity))
        if gray_value < 0:
            gray_value = 0
        if gray_value > 255:
            gray_value = 255
        return f'#{gray_value:02x}{gray_value:02x}{gray_value:02x}'