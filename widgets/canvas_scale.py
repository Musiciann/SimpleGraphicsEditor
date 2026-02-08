class CanvasScale:
    @staticmethod
    def canvas_to_screen_x(canvas_widget, canvas_x):
        screen_x = int((canvas_x - canvas_widget.editor.view_center_x) * canvas_widget.editor.scale_factor +
                       canvas_widget.editor.view_center_x + canvas_widget.editor.view_offset_x)
        return max(0, min(screen_x, canvas_widget.editor.canvas_width))

    @staticmethod
    def canvas_to_screen_y(canvas_widget, canvas_y):
        screen_y = int((canvas_y - canvas_widget.editor.view_center_y) * canvas_widget.editor.scale_factor +
                       canvas_widget.editor.view_center_y + canvas_widget.editor.view_offset_y)
        return max(0, min(screen_y, canvas_widget.editor.canvas_height))

    @staticmethod
    def screen_to_canvas_x(canvas_widget, screen_x):
        canvas_x = int((screen_x - canvas_widget.editor.view_center_x - canvas_widget.editor.view_offset_x) /
                       canvas_widget.editor.scale_factor + canvas_widget.editor.view_center_x)
        return max(0, min(canvas_x, canvas_widget.editor.original_width - 1))

    @staticmethod
    def screen_to_canvas_y(canvas_widget, screen_y):
        canvas_y = int((screen_y - canvas_widget.editor.view_center_y - canvas_widget.editor.view_offset_y) /
                       canvas_widget.editor.scale_factor + canvas_widget.editor.view_center_y)
        return max(0, min(canvas_y, canvas_widget.editor.original_height - 1))

    @staticmethod
    def zoom_in(canvas_widget, event=None):
        if not canvas_widget.editor.canvas_created:
            return

        old_scale = canvas_widget.editor.scale_factor
        new_scale = min(10.0, canvas_widget.editor.scale_factor * 1.2)

        if old_scale == new_scale:
            return

        if event:
            mouse_canvas_x = CanvasScale.screen_to_canvas_x(canvas_widget, event.x)
            mouse_canvas_y = CanvasScale.screen_to_canvas_y(canvas_widget, event.y)

            canvas_widget.editor.scale_factor = new_scale

            new_mouse_screen_x = CanvasScale.canvas_to_screen_x(canvas_widget, mouse_canvas_x)
            new_mouse_screen_y = CanvasScale.canvas_to_screen_y(canvas_widget, mouse_canvas_y)

            dx = new_mouse_screen_x - event.x
            dy = new_mouse_screen_y - event.y

            canvas_widget.editor.view_offset_x -= dx
            canvas_widget.editor.view_offset_y -= dy
        else:
            canvas_widget.editor.scale_factor = new_scale

        canvas_widget.redraw_canvas()

    @staticmethod
    def zoom_out(canvas_widget, event=None):
        if not canvas_widget.editor.canvas_created:
            return

        old_scale = canvas_widget.editor.scale_factor
        new_scale = max(0.1, canvas_widget.editor.scale_factor / 1.2)

        if old_scale == new_scale:
            return

        if event:
            mouse_canvas_x = CanvasScale.screen_to_canvas_x(canvas_widget, event.x)
            mouse_canvas_y = CanvasScale.screen_to_canvas_y(canvas_widget, event.y)

            canvas_widget.editor.scale_factor = new_scale

            new_mouse_screen_x = CanvasScale.canvas_to_screen_x(canvas_widget, mouse_canvas_x)
            new_mouse_screen_y = CanvasScale.canvas_to_screen_y(canvas_widget, mouse_canvas_y)

            dx = new_mouse_screen_x - event.x
            dy = new_mouse_screen_y - event.y

            canvas_widget.editor.view_offset_x -= dx
            canvas_widget.editor.view_offset_y -= dy
        else:
            canvas_widget.editor.scale_factor = new_scale

        canvas_widget.redraw_canvas()

    @staticmethod
    def reset_zoom(canvas_widget):
        if not canvas_widget.editor.canvas_created:
            return

        canvas_widget.editor.scale_factor = 1.0
        canvas_widget.editor.view_offset_x = 0
        canvas_widget.editor.view_offset_y = 0
        canvas_widget.editor.view_center_x = canvas_widget.editor.canvas_width // 2
        canvas_widget.editor.view_center_y = canvas_widget.editor.canvas_height // 2
        canvas_widget.redraw_canvas()

    @staticmethod
    def on_mouse_wheel(canvas_widget, event):
        if event.delta > 0:
            CanvasScale.zoom_in(canvas_widget, event)
        else:
            CanvasScale.zoom_out(canvas_widget, event)
        return "break"

    @staticmethod
    def redraw_canvas(canvas_widget):
        if not canvas_widget.editor.canvas_created:
            return

        canvas_widget.canvas.delete("all")

        zoom_percent = int(canvas_widget.editor.scale_factor * 100)
        canvas_widget.scale_label.configure(text=f"Масштаб: {zoom_percent}%")

        canvas_widget.editor.status_bar.update_status(
            f"Холст: {canvas_widget.editor.original_width}x{canvas_widget.editor.original_height} пикселей | Масштаб: {zoom_percent}%")

        if canvas_widget.editor.grid_visible:
            canvas_widget.draw_pixel_grid()

        for line_info in canvas_widget.editor.lines:
            for pixel in line_info['pixels']:
                if len(pixel) == 3:
                    x, y, intensity = pixel
                    color = canvas_widget.get_color_from_intensity(intensity)
                else:
                    x, y = pixel
                    color = "black"

                screen_x = CanvasScale.canvas_to_screen_x(canvas_widget, x)
                screen_y = CanvasScale.canvas_to_screen_y(canvas_widget, y)

                if not (
                        0 <= screen_x <= canvas_widget.editor.canvas_width and 0 <= screen_y <= canvas_widget.editor.canvas_height):
                    continue

                pixel_size = max(1, int(canvas_widget.editor.scale_factor))

                x1 = screen_x - pixel_size // 2
                y1 = screen_y - pixel_size // 2
                x2 = screen_x + pixel_size // 2
                y2 = screen_y + pixel_size // 2

                x1 = max(0, min(x1, canvas_widget.editor.canvas_width))
                y1 = max(0, min(y1, canvas_widget.editor.canvas_height))
                x2 = max(0, min(x2, canvas_widget.editor.canvas_width))
                y2 = max(0, min(y2, canvas_widget.editor.canvas_height))

                canvas_widget.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color, outline=color, tags="line_pixel"
                )

        for point_info in canvas_widget.editor.points:
            x, y = point_info['x'], point_info['y']
            color = point_info['color']
            tag = point_info['tag']

            screen_x = CanvasScale.canvas_to_screen_x(canvas_widget, x)
            screen_y = CanvasScale.canvas_to_screen_y(canvas_widget, y)

            if not (
                    0 <= screen_x <= canvas_widget.editor.canvas_width and 0 <= screen_y <= canvas_widget.editor.canvas_height):
                continue

            pixel_size = max(1, int(canvas_widget.editor.scale_factor))

            x1 = screen_x - pixel_size // 2
            y1 = screen_y - pixel_size // 2
            x2 = screen_x + pixel_size // 2
            y2 = screen_y + pixel_size // 2

            x1 = max(0, min(x1, canvas_widget.editor.canvas_width))
            y1 = max(0, min(y1, canvas_widget.editor.canvas_height))
            x2 = max(0, min(x2, canvas_widget.editor.canvas_width))
            y2 = max(0, min(y2, canvas_widget.editor.canvas_height))

            canvas_widget.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color, outline=color, tags=tag
            )

        if canvas_widget.editor.debug_mode and canvas_widget.editor.total_steps > 0:
            canvas_widget.draw_debug_step()