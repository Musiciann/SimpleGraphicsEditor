import math
from algorithms.algorithms import bresenham_algorithm_pixels

class PolygonTool:
    def __init__(self, canvas_widget):
        self.canvas_widget = canvas_widget
        self.editor = canvas_widget.editor
        self.points = []
        self.temp_point_ids = []
        self.temp_edge_ids = []

    def canvas_click(self, event):
        if self.editor.current_tool != "polygon":
            return
        x = self.canvas_widget.screen_to_canvas_x(event.x)
        y = self.canvas_widget.screen_to_canvas_y(event.y)
        self.points.append((x, y))

        screen_x = self.canvas_widget.canvas_to_screen_x(x)
        screen_y = self.canvas_widget.canvas_to_screen_y(y)
        pixel_size = max(1, self.editor.scale_factor)
        pid = self.canvas_widget.canvas.create_rectangle(
            screen_x, screen_y,
            screen_x + pixel_size, screen_y + pixel_size,
            fill="blue", outline="blue", tags="polygon_point"
        )
        self.temp_point_ids.append(pid)

        if len(self.points) >= 2:
            p1 = self.points[-2]
            p2 = self.points[-1]
            pixels = bresenham_algorithm_pixels(p1[0], p1[1], p2[0], p2[1])
            for px, py in pixels:
                screen_x = self.canvas_widget.canvas_to_screen_x(px)
                screen_y = self.canvas_widget.canvas_to_screen_y(py)
                pixel_size = max(1, self.editor.scale_factor)
                eid = self.canvas_widget.canvas.create_rectangle(
                    screen_x, screen_y,
                    screen_x + pixel_size, screen_y + pixel_size,
                    fill="#aaaaaa", outline="#aaaaaa", tags="polygon_edge_temp"
                )
                self.temp_edge_ids.append(eid)

        self.editor.status_bar.update_status(f"Полигон: точка {len(self.points)} добавлена")

    def finish_polygon(self):
        if len(self.points) < 3:
            self.editor.status_bar.update_status("Полигон должен иметь хотя бы 3 точки")
            self.clear_polygon_points()
            return
        polygon_info = {
            'type': 'polygon',
            'vertices': self.points.copy(),
            'convex': None,
            'normals': [],
            'pixel_ids': []
        }
        self.editor.polygons.append(polygon_info)
        self.draw_polygon(polygon_info)
        self.clear_polygon_points()
        self.editor.status_bar.update_status("Полигон создан")
        self.canvas_widget.redraw_canvas()

    def clear_polygon_points(self):
        if self.canvas_widget.canvas:
            self.canvas_widget.canvas.delete("polygon_point")
            self.canvas_widget.canvas.delete("polygon_edge_temp")
        self.points = []
        self.temp_point_ids = []
        self.temp_edge_ids = []

    def draw_polygon(self, polygon):
        vertices = polygon['vertices']
        if len(vertices) < 3:
            return
        for i in range(len(vertices)):
            p1 = vertices[i]
            p2 = vertices[(i+1) % len(vertices)]
            pixels = bresenham_algorithm_pixels(p1[0], p1[1], p2[0], p2[1])
            for px, py in pixels:
                screen_x = self.canvas_widget.canvas_to_screen_x(px)
                screen_y = self.canvas_widget.canvas_to_screen_y(py)
                pixel_size = max(1, self.editor.scale_factor)
                pid = self.canvas_widget.canvas.create_rectangle(
                    screen_x, screen_y,
                    screen_x + pixel_size, screen_y + pixel_size,
                    fill="black", outline="black", tags="polygon_edge"
                )
                polygon.setdefault('pixel_ids', []).append(pid)

    def draw_current_polygon(self):
        if not self.points:
            return
        for (x, y) in self.points:
            screen_x = self.canvas_widget.canvas_to_screen_x(x)
            screen_y = self.canvas_widget.canvas_to_screen_y(y)
            pixel_size = max(1, self.editor.scale_factor)
            self.canvas_widget.canvas.create_rectangle(
                screen_x, screen_y,
                screen_x + pixel_size, screen_y + pixel_size,
                fill="blue", outline="blue", tags="polygon_point"
            )
        for i in range(len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i+1]
            pixels = bresenham_algorithm_pixels(p1[0], p1[1], p2[0], p2[1])
            for px, py in pixels:
                screen_x = self.canvas_widget.canvas_to_screen_x(px)
                screen_y = self.canvas_widget.canvas_to_screen_y(py)
                pixel_size = max(1, self.editor.scale_factor)
                self.canvas_widget.canvas.create_rectangle(
                    screen_x, screen_y,
                    screen_x + pixel_size, screen_y + pixel_size,
                    fill="#aaaaaa", outline="#aaaaaa", tags="polygon_edge_temp"
                )

    def compute_convexity(self, polygon):
        vertices = polygon['vertices']
        n = len(vertices)
        if n < 3:
            polygon['convex'] = False
            return False
        signs = []
        for i in range(n):
            p1 = vertices[i]
            p2 = vertices[(i+1) % n]
            p3 = vertices[(i+2) % n]
            v1 = (p2[0] - p1[0], p2[1] - p1[1])
            v2 = (p3[0] - p2[0], p3[1] - p2[1])
            cross = v1[0]*v2[1] - v1[1]*v2[0]
            if cross != 0:
                signs.append(1 if cross > 0 else -1)
        if not signs:
            polygon['convex'] = False
            return False
        all_pos = all(s > 0 for s in signs)
        all_neg = all(s < 0 for s in signs)
        convex = all_pos or all_neg
        polygon['convex'] = convex
        return convex

    def compute_internal_normals(self, polygon):
        vertices = polygon['vertices']
        n = len(vertices)
        if n < 3:
            return []
        area = 0
        for i in range(n):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i+1) % n]
            area += x1*y2 - x2*y1
        ccw = area > 0
        normals = []
        for i in range(n):
            p1 = vertices[i]
            p2 = vertices[(i+1) % n]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            if ccw:
                nx, ny = -dy, dx
            else:
                nx, ny = dy, -dx
            length = math.hypot(nx, ny)
            if length > 0:
                nx /= length
                ny /= length
            normals.append((nx, ny))
        polygon['normals'] = normals
        return normals

    def graham_scan(self, points):
        if len(points) < 3:
            return points[:]
        p0 = min(points, key=lambda p: (p[1], p[0]))
        def angle(p):
            dx = p[0] - p0[0]
            dy = p[1] - p0[1]
            return math.atan2(dy, dx)
        sorted_pts = sorted(points, key=angle)
        unique = []
        last_angle = None
        for p in sorted_pts:
            ang = angle(p)
            if ang != last_angle:
                unique.append(p)
                last_angle = ang
            else:
                if unique and math.hypot(p[0]-p0[0], p[1]-p0[1]) > math.hypot(unique[-1][0]-p0[0], unique[-1][1]-p0[1]):
                    unique[-1] = p
        stack = []
        for p in unique:
            while len(stack) >= 2:
                p1 = stack[-2]
                p2 = stack[-1]
                cross = (p2[0]-p1[0])*(p[1]-p1[1]) - (p2[1]-p1[1])*(p[0]-p1[0])
                if cross <= 0:
                    stack.pop()
                else:
                    break
            stack.append(p)
        return stack

    def jarvis_march(self, points):
        if len(points) < 3:
            return points[:]
        start = min(points, key=lambda p: (p[1], p[0]))
        hull = [start]
        current = start
        while True:
            next_point = None
            for p in points:
                if p == current:
                    continue
                if next_point is None:
                    next_point = p
                else:
                    cross = (p[0]-current[0])*(next_point[1]-current[1]) - \
                            (p[1]-current[1])*(next_point[0]-current[0])
                    if cross < 0 or (cross == 0 and
                                     math.hypot(p[0]-current[0], p[1]-current[1]) >
                                     math.hypot(next_point[0]-current[0], next_point[1]-current[1])):
                        next_point = p
            if next_point == start:
                break
            hull.append(next_point)
            current = next_point
        return hull

    def point_in_polygon(self, point, vertices):
        x, y = point
        inside = False
        n = len(vertices)
        for i in range(n):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i+1) % n]
            if self.point_on_segment(point, (x1, y1), (x2, y2)):
                return True
            if ((y1 > y) != (y2 > y)) and (x < (x2-x1)*(y-y1)/(y2-y1) + x1):
                inside = not inside
        return inside

    def point_on_segment(self, p, a, b):
        x, y = p
        x1, y1 = a
        x2, y2 = b
        cross = (x2-x1)*(y-y1) - (y2-y1)*(x-x1)
        if abs(cross) > 1e-9:
            return False
        if min(x1,x2) <= x <= max(x1,x2) and min(y1,y2) <= y <= max(y1,y2):
            return True
        return False

    def segment_intersect_polygon(self, seg, vertices):
        intersections = []
        p1, p2 = seg
        n = len(vertices)
        for i in range(n):
            a = vertices[i]
            b = vertices[(i+1) % n]
            inter = self.segment_intersection(p1, p2, a, b)
            if inter:
                intersections.append(inter)
        unique = []
        for pt in intersections:
            if not any(math.hypot(pt[0]-u[0], pt[1]-u[1]) < 1e-6 for u in unique):
                unique.append(pt)
        return unique

    def segment_intersection(self, p1, p2, p3, p4):
        x1,y1 = p1
        x2,y2 = p2
        x3,y3 = p3
        x4,y4 = p4
        denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
        if denom == 0:
            return None
        t = ((x1-x3)*(y3-y4) - (y1-y3)*(x3-x4)) / denom
        u = -((x1-x2)*(y1-y3) - (y1-y2)*(x1-x3)) / denom
        if 0 <= t <= 1 and 0 <= u <= 1:
            x = x1 + t*(x2-x1)
            y = y1 + t*(y2-y1)
            return (x, y)
        return None