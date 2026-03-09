from algorithms.matrix_utils import hermite_coeffs, bezier_coeffs, bspline_coeffs, eval_poly

class ParametricCurvesTool:
    MODE_HERMITE = "hermite"
    MODE_BEZIER = "bezier"
    MODE_BSPLINE = "bspline"

    def __init__(self, canvas_widget):
        self.canvas_widget = canvas_widget
        self.editor = canvas_widget.editor

        self.mode = self.MODE_BEZIER
        self.temp_points = []
        self.expected_points = 0
        self.closed = False

        self.editing_enabled = False
        self.selected_curve_idx = -1
        self.selected_point_idx = -1
        self.dragging = False
        self.drag_start = None

        self.current_bspline_curve = None

    def reset_state(self):
        self.temp_points = []
        self.expected_points = 0
        self.selected_curve_idx = -1
        self.selected_point_idx = -1
        self.dragging = False
        self.current_bspline_curve = None

    def set_mode(self, mode):
        self.mode = mode
        self.temp_points = []
        self.expected_points = 0
        self.current_bspline_curve = None
        self._clear_control_point_markers()
        self._delete_spline_input()

    def set_closed(self, closed):
        if self.closed != closed:
            self.closed = closed
            if self.current_bspline_curve is not None:
                self.current_bspline_curve['closed'] = closed
                self._rebuild_curve(self.current_bspline_curve)
                self._update_control_points()

    def toggle_edit_mode(self, enabled):
        self.editing_enabled = enabled
        if enabled:
            self._draw_all_control_points()
        else:
            self._clear_control_point_markers()
            self.selected_curve_idx = -1
            self.selected_point_idx = -1
            self.dragging = False

    def _canvas_exists(self):
        return (self.canvas_widget.canvas and
                self.canvas_widget.canvas.winfo_exists())

    def _draw_all_control_points(self):
        if not self.editing_enabled or not self._canvas_exists():
            return
        self._clear_control_point_markers()
        for line in self.editor.lines:
            if line.get('type') == 'parametric':
                pts = line.get('points', [])
                for idx, (x, y) in enumerate(pts):
                    screen_x = self.canvas_widget.canvas_to_screen_x(x)
                    screen_y = self.canvas_widget.canvas_to_screen_y(y)
                    size = max(4, self.editor.scale_factor * 2)
                    self.canvas_widget.canvas.create_rectangle(
                        screen_x - size//2, screen_y - size//2,
                        screen_x + size//2, screen_y + size//2,
                        fill="green", outline="black", width=1,
                        tags=("spline_control_point",)
                    )

    def _clear_control_point_markers(self):
        if self._canvas_exists():
            self.canvas_widget.canvas.delete("spline_control_point")

    def _delete_spline_input(self):
        if self._canvas_exists():
            self.canvas_widget.canvas.delete("spline_input")

    def _update_control_points(self):
        self._draw_all_control_points()

    def canvas_click(self, event):
        if not self.editor.canvas_created or self.editor.current_tool != "spline":
            return
        x = self.canvas_widget.screen_to_canvas_x(event.x)
        y = self.canvas_widget.screen_to_canvas_y(event.y)
        if x < 0 or x >= self.editor.original_width or y < 0 or y >= self.editor.original_height:
            return
        if self.editing_enabled:
            self._select_point(event.x, event.y)
        else:
            self._build_mode_click(x, y)

    def canvas_drag(self, event):
        if not self.editing_enabled or not self.dragging or self.selected_curve_idx < 0:
            return
        x = self.canvas_widget.screen_to_canvas_x(event.x)
        y = self.canvas_widget.screen_to_canvas_y(event.y)
        line = self.editor.lines[self.selected_curve_idx]
        if line.get('type') == 'parametric':
            line['points'][self.selected_point_idx] = (x, y)
            self._rebuild_curve(line)
            self._update_control_points()

    def canvas_release(self, event):
        self.dragging = False
        self.selected_curve_idx = -1
        self.selected_point_idx = -1

    def _select_point(self, screen_x, screen_y):
        screen_tolerance = 10
        best_dist_sq = screen_tolerance * screen_tolerance
        best_curve_idx = -1
        best_point_idx = -1
        for ci, line in enumerate(self.editor.lines):
            if line.get('type') != 'parametric':
                continue
            pts = line.get('points', [])
            for pi, (px, py) in enumerate(pts):
                spx = self.canvas_widget.canvas_to_screen_x(px)
                spy = self.canvas_widget.canvas_to_screen_y(py)
                dx = spx - screen_x
                dy = spy - screen_y
                dist_sq = dx*dx + dy*dy
                if dist_sq < best_dist_sq:
                    best_dist_sq = dist_sq
                    best_curve_idx = ci
                    best_point_idx = pi
        if best_curve_idx >= 0:
            self.selected_curve_idx = best_curve_idx
            self.selected_point_idx = best_point_idx
            self.dragging = True
            self.drag_start = (screen_x, screen_y)

    def _build_mode_click(self, x, y):
        if self.mode == self.MODE_HERMITE:
            self._hermite_click(x, y)
        elif self.mode == self.MODE_BEZIER:
            self._bezier_click(x, y)
        elif self.mode == self.MODE_BSPLINE:
            self._bspline_click(x, y)

    def _hermite_click(self, x, y):
        if len(self.temp_points) == 0:
            self.temp_points.append((x, y))
            self.canvas_widget.draw_pixel_point(x, y, "blue", "spline_input")
        elif len(self.temp_points) == 1:
            self.temp_points.append((x, y))
            self.canvas_widget.draw_pixel_point(x, y, "red", "spline_input")
        elif len(self.temp_points) == 2:
            self.temp_points.append((x, y))
            self.canvas_widget.draw_pixel_point(x, y, "green", "spline_input")
        elif len(self.temp_points) == 3:
            self.temp_points.append((x, y))
            self.canvas_widget.draw_pixel_point(x, y, "green", "spline_input")
            self._build_hermite_segment()
            self.temp_points = []
            self._delete_spline_input()
            self._after_curve_built()

    def _build_hermite_segment(self):
        P1, P4, T1_end, T4_end = self.temp_points
        R1 = (T1_end[0] - P1[0], T1_end[1] - P1[1])
        R4 = (T4_end[0] - P4[0], T4_end[1] - P4[1])
        coeffs_x, coeffs_y = hermite_coeffs(P1, P4, R1, R4)
        steps = max(abs(P4[0]-P1[0]), abs(P4[1]-P1[1])) * 2
        steps = max(steps, 50)
        pixels = []
        for i in range(steps + 1):
            t = i / steps
            x = int(round(eval_poly(coeffs_x, t)))
            y = int(round(eval_poly(coeffs_y, t)))
            if 0 <= x < self.editor.original_width and 0 <= y < self.editor.original_height:
                pixels.append((x, y))
        unique_pixels = []
        seen = set()
        for p in pixels:
            if p not in seen:
                seen.add(p)
                unique_pixels.append(p)
        curve_info = {
            'type': 'parametric',
            'subtype': 'hermite',
            'points': [P1, P4, T1_end, T4_end],
            'pixels': unique_pixels,
            'pixel_ids': []
        }
        self.editor.lines.append(curve_info)
        self._draw_curve_pixels(curve_info)

    def _bezier_click(self, x, y):
        if len(self.temp_points) < 4:
            self.temp_points.append((x, y))
            color = "blue" if len(self.temp_points) in (1, 4) else "green"
            self.canvas_widget.draw_pixel_point(x, y, color, "spline_input")
        if len(self.temp_points) == 4:
            self._build_bezier_segment()
            self.temp_points = []
            self._delete_spline_input()
            self._after_curve_built()

    def _build_bezier_segment(self):
        P1, P2, P3, P4 = self.temp_points
        coeffs_x, coeffs_y = bezier_coeffs(P1, P2, P3, P4)
        pixels = self._generate_pixels_from_coeffs(coeffs_x, coeffs_y, P1, P4)
        curve_info = {
            'type': 'parametric',
            'subtype': 'bezier',
            'points': [P1, P2, P3, P4],
            'pixels': pixels,
            'pixel_ids': []
        }
        self.editor.lines.append(curve_info)
        self._draw_curve_pixels(curve_info)

    def _bspline_click(self, x, y):
        self.temp_points.append((x, y))
        self.canvas_widget.draw_pixel_point(x, y, "blue", "spline_input")
        if len(self.temp_points) >= 4:
            if self.current_bspline_curve is None:
                self._create_new_bspline_curve()
            else:
                self._update_bspline_curve()
        self._after_curve_built()

    def _create_new_bspline_curve(self):
        curve_info = {
            'type': 'parametric',
            'subtype': 'bspline',
            'points': self.temp_points.copy(),
            'closed': self.closed,
            'pixels': [],
            'pixel_ids': []
        }
        self.editor.lines.append(curve_info)
        self.current_bspline_curve = curve_info
        self._rebuild_curve(curve_info)

    def _update_bspline_curve(self):
        if self.current_bspline_curve is None:
            return
        self.current_bspline_curve['points'] = self.temp_points.copy()
        self.current_bspline_curve['closed'] = self.closed
        self._rebuild_curve(self.current_bspline_curve)

    def _add_bspline_segment_pixels(self, P0, P1, P2, P3, pixels_list):
        coeffs_x, coeffs_y = bspline_coeffs(P0, P1, P2, P3)
        steps = max(abs(P2[0]-P1[0]), abs(P2[1]-P1[1])) * 2
        steps = max(steps, 30)
        for j in range(steps + 1):
            t = j / steps
            x = int(round(eval_poly(coeffs_x, t)))
            y = int(round(eval_poly(coeffs_y, t)))
            if 0 <= x < self.editor.original_width and 0 <= y < self.editor.original_height:
                pixels_list.append((x, y))

    def _generate_pixels_from_coeffs(self, coeffs_x, coeffs_y, start, end):
        steps = max(abs(end[0]-start[0]), abs(end[1]-start[1])) * 2
        steps = max(steps, 50)
        pixels = []
        for i in range(steps + 1):
            t = i / steps
            x = int(round(eval_poly(coeffs_x, t)))
            y = int(round(eval_poly(coeffs_y, t)))
            if 0 <= x < self.editor.original_width and 0 <= y < self.editor.original_height:
                pixels.append((x, y))
        unique = []
        seen = set()
        for p in pixels:
            if p not in seen:
                seen.add(p)
                unique.append(p)
        return unique

    def _draw_curve_pixels(self, curve_info):
        if not self._canvas_exists():
            return
        color = "black"
        for (x, y) in curve_info['pixels']:
            screen_x = self.canvas_widget.canvas_to_screen_x(x)
            screen_y = self.canvas_widget.canvas_to_screen_y(y)
            pixel_size = max(1, self.editor.scale_factor)
            pid = self.canvas_widget.canvas.create_rectangle(
                screen_x, screen_y,
                screen_x + pixel_size, screen_y + pixel_size,
                fill=color, outline=color, tags="parametric_pixel"
            )
            curve_info['pixel_ids'].append(pid)

    def _after_curve_built(self):
        if self.editing_enabled and self._canvas_exists():
            self._draw_all_control_points()

    def _rebuild_curve(self, line):
        if not self._canvas_exists():
            return
        for pid in line.get('pixel_ids', []):
            self.canvas_widget.canvas.delete(pid)
        line['pixel_ids'] = []
        subtype = line.get('subtype')
        pts = line.get('points', [])
        closed = line.get('closed', False)
        if not pts:
            return
        if subtype == 'hermite' and len(pts) == 4:
            P1, P4, T1, T4 = pts
            R1 = (T1[0]-P1[0], T1[1]-P1[1])
            R4 = (T4[0]-P4[0], T4[1]-P4[1])
            cx, cy = hermite_coeffs(P1, P4, R1, R4)
            line['pixels'] = self._generate_pixels_from_coeffs(cx, cy, P1, P4)
        elif subtype == 'bezier' and len(pts) == 4:
            cx, cy = bezier_coeffs(*pts)
            line['pixels'] = self._generate_pixels_from_coeffs(cx, cy, pts[0], pts[3])
        elif subtype == 'bspline' and len(pts) >= 4:
            all_pixels = []
            n = len(pts)
            if closed:
                extended = (pts[-3:] + pts + pts[:3])
                for i in range(n):
                    P0 = extended[i+3]
                    P1 = extended[i+4]
                    P2 = extended[i+5]
                    P3 = extended[i+6]
                    self._add_bspline_segment_pixels(P0, P1, P2, P3, all_pixels)
            else:
                for i in range(n - 3):
                    P0, P1, P2, P3 = pts[i:i+4]
                    self._add_bspline_segment_pixels(P0, P1, P2, P3, all_pixels)
            seen = set()
            unique = []
            for p in all_pixels:
                if p not in seen:
                    seen.add(p)
                    unique.append(p)
            line['pixels'] = unique
        else:
            return
        self._draw_curve_pixels(line)

    def redraw_curves(self):
        if not self._canvas_exists():
            return
        for line in self.editor.lines:
            if line.get('type') == 'parametric':
                for pid in line.get('pixel_ids', []):
                    self.canvas_widget.canvas.delete(pid)
                line['pixel_ids'] = []
                self._draw_curve_pixels(line)
        if self.editing_enabled:
            self._draw_all_control_points()