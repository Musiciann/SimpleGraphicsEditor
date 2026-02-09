import json
import os
from tkinter import filedialog, messagebox


class FileOptions:
    def __init__(self, canvas_widget):
        self.canvas_widget = canvas_widget
        self.editor = canvas_widget.editor

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

            self.canvas_widget.create_canvas_area()

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

            self.canvas_widget.redraw_canvas()

            messagebox.showinfo("Успех", f"Холст загружен из файла:\n{filename}")
            return True

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
            return False