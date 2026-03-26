import math
from algorithms.algorithms import bresenham_algorithm_pixels

class FillTool:
    def __init__(self, canvas_widget):
        self.canvas_widget = canvas_widget
        self.editor = canvas_widget.editor
        self.fill_color = "lightgray"
        self.fill_steps = []
        self.current_step = 0
        self.total_steps = 0
        self.show_all = False

    def set_fill_color(self, color):
        self.fill_color = color

    def clear_fill(self):
        if self.canvas_widget.canvas:
            self.canvas_widget.canvas.delete("fill_pixel")
        self.fill_steps = []
        self.current_step = 0
        self.total_steps = 0
        self.show_all = False

    def update_fill_display(self):
        if not self.editor.canvas_created:
            return
        self.canvas_widget.canvas.delete("fill_pixel")
        if not self.fill_steps:
            return
        if self.show_all:
            steps_to_show = range(len(self.fill_steps))
        else:
            steps_to_show = range(self.current_step + 1)
        for step_idx in steps_to_show:
            if step_idx < len(self.fill_steps):
                for x, y in self.fill_steps[step_idx]:
                    screen_x = self.canvas_widget.canvas_to_screen_x(x)
                    screen_y = self.canvas_widget.canvas_to_screen_y(y)
                    pixel_size = max(1, self.editor.scale_factor)
                    self.canvas_widget.canvas.create_rectangle(
                        screen_x, screen_y,
                        screen_x + pixel_size, screen_y + pixel_size,
                        fill=self.fill_color, outline=self.fill_color, tags="fill_pixel"
                    )

    def fill_polygon(self, algorithm, polygon=None):
        if polygon is None:
            if not self.editor.polygons:
                self.editor.status_bar.update_status("Нет полигонов для заполнения")
                return False
            polygon = self.editor.polygons[-1]
        vertices = polygon['vertices']
        if len(vertices) < 3:
            self.editor.status_bar.update_status("Полигон должен иметь хотя бы 3 вершины")
            return False

        self.clear_fill()
        boundary = self._compute_boundary(vertices)

        if algorithm == "scanline":
            steps = self._fill_scanline(vertices, boundary)
        elif algorithm == "scanline_active":
            steps = self._fill_scanline_active(vertices, boundary)
        elif algorithm == "seed_simple":
            cx = sum(v[0] for v in vertices) / len(vertices)
            cy = sum(v[1] for v in vertices) / len(vertices)
            seed = (int(cx), int(cy))
            if not self._point_in_polygon(seed, vertices):
                found = False
                for dy in range(-5, 6):
                    for dx in range(-5, 6):
                        sx = int(cx) + dx
                        sy = int(cy) + dy
                        if self._point_in_polygon((sx, sy), vertices):
                            seed = (sx, sy)
                            found = True
                            break
                    if found:
                        break
                if not found:
                    self.editor.status_bar.update_status("Не удалось найти внутреннюю точку для затравки")
                    return False
            steps = self._fill_seed_simple(vertices, boundary, seed)
        elif algorithm == "seed_scanline":
            cx = sum(v[0] for v in vertices) / len(vertices)
            cy = sum(v[1] for v in vertices) / len(vertices)
            seed = (int(cx), int(cy))
            if not self._point_in_polygon(seed, vertices):
                found = False
                for dy in range(-5, 6):
                    for dx in range(-5, 6):
                        sx = int(cx) + dx
                        sy = int(cy) + dy
                        if self._point_in_polygon((sx, sy), vertices):
                            seed = (sx, sy)
                            found = True
                            break
                    if found:
                        break
                if not found:
                    self.editor.status_bar.update_status("Не удалось найти внутреннюю точку для затравки")
                    return False
            steps = self._fill_seed_scanline(vertices, boundary, seed)
        else:
            return False

        self.fill_steps = steps
        self.total_steps = len(steps)
        self.current_step = 0

        debug_mode = getattr(self.editor.tool_panel, 'fill_debug_var', None)
        if debug_mode and debug_mode.get():
            self.show_all = False
            self.update_fill_display()
            self.editor.status_bar.update_status(f"Режим отладки. Всего шагов: {self.total_steps}")
            return True
        else:
            all_pixels = []
            for step in steps:
                all_pixels.extend(step)
            polygon['fill_pixels'] = all_pixels
            polygon['fill_color'] = self.fill_color
            polygon['fill_algorithm'] = algorithm
            self.editor.status_bar.update_status(f"Заполнение завершено. Закрашено {len(all_pixels)} пикселей")
            self.canvas_widget.redraw_canvas()
            return True

    def _compute_boundary(self, vertices):
        boundary = set()
        n = len(vertices)
        for i in range(n):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i+1) % n]
            pixels = bresenham_algorithm_pixels(x1, y1, x2, y2)
            for px, py in pixels:
                boundary.add((px, py))
        return boundary

    def _fill_scanline(self, vertices, boundary):
        min_y = min(v[1] for v in vertices)
        max_y = max(v[1] for v in vertices)
        steps = []
        for y in range(min_y, max_y + 1):
            intersections = []
            n = len(vertices)
            for i in range(n):
                x1, y1 = vertices[i]
                x2, y2 = vertices[(i+1) % n]
                if (y1 <= y and y2 > y) or (y2 <= y and y1 > y):
                    x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                    intersections.append(x)
            intersections.sort()
            row_pixels = []
            for i in range(0, len(intersections), 2):
                if i+1 < len(intersections):
                    x_start = int(math.ceil(intersections[i]))
                    x_end = int(math.floor(intersections[i+1]))
                    for x in range(x_start, x_end + 1):
                        if (x, y) not in boundary:
                            row_pixels.append((x, y))
            if row_pixels:
                steps.append(row_pixels)
        return steps

    def _fill_scanline_active(self, vertices, boundary):
        edges = []
        n = len(vertices)
        for i in range(n):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i+1) % n]
            if y1 == y2:
                continue
            if y1 > y2:
                x1, x2 = x2, x1
                y1, y2 = y2, y1
            dx = (x2 - x1) / (y2 - y1)
            edges.append({
                'y_max': y2,
                'x': x1,
                'dx': dx,
                'y_min': y1
            })
        edges.sort(key=lambda e: e['y_min'])
        min_y = min(v[1] for v in vertices)
        max_y = max(v[1] for v in vertices)
        aet = []
        steps = []
        for y in range(min_y, max_y + 1):
            while edges and edges[0]['y_min'] == y:
                e = edges.pop(0)
                aet.append(e)
            aet = [e for e in aet if e['y_max'] > y]
            aet.sort(key=lambda e: e['x'])
            row_pixels = []
            for i in range(0, len(aet), 2):
                if i+1 < len(aet):
                    x1 = int(math.ceil(aet[i]['x']))
                    x2 = int(math.floor(aet[i+1]['x']))
                    for x in range(x1, x2 + 1):
                        if (x, y) not in boundary:
                            row_pixels.append((x, y))
            if row_pixels:
                steps.append(row_pixels)
            for e in aet:
                e['x'] += e['dx']
        return steps

    def _fill_seed_simple(self, vertices, boundary, seed):
        stack = [seed]
        visited = set()
        steps = []
        while stack:
            px, py = stack.pop()
            if (px, py) in visited:
                continue
            if (px, py) in boundary:
                continue
            visited.add((px, py))
            steps.append([(px, py)])
            for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                nx, ny = px + dx, py + dy
                if 0 <= nx < self.editor.original_width and 0 <= ny < self.editor.original_height:
                    if (nx, ny) not in visited and (nx, ny) not in boundary:
                        stack.append((nx, ny))
        return steps

    def _fill_seed_scanline(self, vertices, boundary, seed):
        stack = [seed]
        visited = set()
        steps = []
        while stack:
            px, py = stack.pop()
            if (px, py) in visited:
                continue
            if (px, py) in boundary:
                continue
            x_left = px
            x_right = px
            while x_left - 1 >= 0 and (x_left - 1, py) not in boundary and (x_left - 1, py) not in visited:
                x_left -= 1
            while x_right + 1 < self.editor.original_width and (x_right + 1, py) not in boundary and (x_right + 1, py) not in visited:
                x_right += 1
            row_pixels = []
            for x in range(x_left, x_right + 1):
                if (x, py) not in boundary and (x, py) not in visited:
                    row_pixels.append((x, py))
                    visited.add((x, py))
            if row_pixels:
                steps.append(row_pixels)
            for x in range(x_left, x_right + 1):
                for dy in [-1, 1]:
                    ny = py + dy
                    if 0 <= ny < self.editor.original_height:
                        if (x, ny) not in visited and (x, ny) not in boundary:
                            stack.append((x, ny))
        return steps

    def _point_in_polygon(self, point, vertices):
        x, y = point
        inside = False
        n = len(vertices)
        for i in range(n):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i+1) % n]
            if self._point_on_segment(point, (x1, y1), (x2, y2)):
                return True
            if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
                inside = not inside
        return inside

    def _point_on_segment(self, p, a, b):
        x, y = p
        x1, y1 = a
        x2, y2 = b
        cross = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)
        if abs(cross) > 1e-9:
            return False
        if min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2):
            return True
        return False

    def first_step(self):
        if self.total_steps > 0:
            self.current_step = 0
            self.show_all = False
            self.update_fill_display()

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.show_all = False
            self.update_fill_display()

    def next_step(self):
        if self.current_step < self.total_steps - 1:
            self.current_step += 1
            self.show_all = False
            self.update_fill_display()

    def last_step(self):
        if self.total_steps > 0:
            self.current_step = self.total_steps - 1
            self.show_all = False
            self.update_fill_display()

    def toggle_show_all(self):
        self.show_all = not self.show_all
        self.update_fill_display()