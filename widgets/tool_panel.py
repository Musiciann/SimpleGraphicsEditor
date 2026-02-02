import customtkinter as ctk

class ToolPanel:
    def __init__(self, editor):
        self.editor = editor

        self.tool_frame = ctk.CTkFrame(editor.root, width=250)

        self.debug_var = ctk.BooleanVar(value=False)
        self.grid_var = ctk.BooleanVar(value=False)
        self.algorithm_var = ctk.StringVar(value="DDA")

        self._create_widgets()

    def pack_widget(self):
        self.tool_frame.pack(side="right", fill="y", padx=5, pady=5)
        self.tool_frame.pack_propagate(False)

    def _create_widgets(self):
        ctk.CTkLabel(self.tool_frame, text="Инструменты",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        self.line_tool_btn = ctk.CTkButton(
            self.tool_frame,
            text="Отрезок",
            command=self.select_line_tool,
            height=40
        )
        self.line_tool_btn.pack(pady=5, padx=10)

        self.other_tool_btn = ctk.CTkButton(
            self.tool_frame,
            text="Другой инструмент",
            command=self.select_other_tool,
            height=40,
            fg_color=("gray75", "gray25")
        )
        self.other_tool_btn.pack(pady=5, padx=10)

        self.common_settings_frame = ctk.CTkFrame(self.tool_frame)
        self.common_settings_frame.pack(fill="x", padx=10, pady=15)

        ctk.CTkLabel(self.common_settings_frame,
                     text="Общие настройки",
                     font=ctk.CTkFont(weight="bold")).pack(pady=5)

        scale_frame = ctk.CTkFrame(self.common_settings_frame)
        scale_frame.pack(fill="x", padx=10, pady=5)

        self.zoom_out_btn = ctk.CTkButton(
            scale_frame,
            text="-",
            width=40,
            command=self.editor.canvas_widget.zoom_out
        )
        self.zoom_out_btn.pack(side="left", padx=5)

        self.zoom_label = ctk.CTkLabel(
            scale_frame,
            text="100%",
            width=60
        )
        self.zoom_label.pack(side="left", padx=5)

        self.zoom_in_btn = ctk.CTkButton(
            scale_frame,
            text="+",
            width=40,
            command=self.editor.canvas_widget.zoom_in
        )
        self.zoom_in_btn.pack(side="left", padx=5)

        self.reset_zoom_btn = ctk.CTkButton(
            scale_frame,
            text="Сброс",
            width=60,
            command=self.editor.canvas_widget.reset_zoom
        )
        self.reset_zoom_btn.pack(side="left", padx=5)

        self.grid_checkbox = ctk.CTkCheckBox(
            self.common_settings_frame,
            text="Показать сетку",
            variable=self.grid_var,
            command=self.editor.canvas_widget.toggle_grid,
            state="normal"
        )
        self.grid_checkbox.pack(pady=5, padx=10)

        control_frame = ctk.CTkFrame(self.common_settings_frame)
        control_frame.pack(fill="x", padx=10, pady=10)

        self.clear_btn = ctk.CTkButton(
            control_frame,
            text="Очистить холст",
            command=self.editor.canvas_widget.clear_canvas,
            state="normal"
        )
        self.clear_btn.pack(pady=5)

        self.reset_view_btn = ctk.CTkButton(
            control_frame,
            text="Сброс вида",
            command=self.editor.canvas_widget.reset_view,
            state="normal"
        )
        self.reset_view_btn.pack(pady=5)

        self.line_tool_frame = ctk.CTkFrame(self.tool_frame)
        self.line_tool_frame.pack_forget()

        self.setup_line_tool_functionality()

    def setup_line_tool_functionality(self):
        for widget in self.line_tool_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.line_tool_frame,
                     text="Алгоритмы построения",
                     font=ctk.CTkFont(weight="bold")).pack(pady=5)

        algorithms = [
            ("Алгоритм ЦДА", "DDA"),
            ("Алгоритм Брезенхема", "Bresenham"),
            ("Алгоритм Ву", "Wu")
        ]

        for text, value in algorithms:
            radio = ctk.CTkRadioButton(
                self.line_tool_frame,
                text=text,
                variable=self.algorithm_var,
                value=value,
                command=self.on_algorithm_change
            )
            radio.pack(anchor="w", padx=20, pady=2)

        ctk.CTkLabel(self.line_tool_frame,
                     text="Отладочный режим",
                     font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))

        debug_controls = ctk.CTkFrame(self.line_tool_frame)
        debug_controls.pack(fill="x", padx=10, pady=5)

        self.debug_checkbox = ctk.CTkCheckBox(
            debug_controls,
            text="Включить отладку",
            variable=self.debug_var,
            command=self.toggle_debug_mode
        )
        self.debug_checkbox.pack(side="left", padx=5)

        step_frame = ctk.CTkFrame(self.line_tool_frame)
        step_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(step_frame, text="Пошаговый режим:").pack(anchor="w", pady=2)

        step_controls = ctk.CTkFrame(step_frame)
        step_controls.pack(fill="x", pady=5)

        self.first_btn = ctk.CTkButton(
            step_controls,
            text="<<",
            width=35,
            command=self.editor.canvas_widget.first_step,
            state="disabled"
        )
        self.first_btn.pack(side="left", padx=2)

        self.prev_btn = ctk.CTkButton(
            step_controls,
            text="<",
            width=35,
            command=self.editor.canvas_widget.prev_step,
            state="disabled"
        )
        self.prev_btn.pack(side="left", padx=2)

        self.step_label = ctk.CTkLabel(step_controls, text="0/0", width=50)
        self.step_label.pack(side="left", padx=5)

        self.next_btn = ctk.CTkButton(
            step_controls,
            text=">",
            width=35,
            command=self.editor.canvas_widget.next_step,
            state="disabled"
        )
        self.next_btn.pack(side="left", padx=2)

        self.last_btn = ctk.CTkButton(
            step_controls,
            text=">>",
            width=35,
            command=self.editor.canvas_widget.last_step,
            state="disabled"
        )
        self.last_btn.pack(side="left", padx=2)

        self.show_all_btn = ctk.CTkButton(
            step_frame,
            text="Показать все",
            width=120,
            command=self.editor.canvas_widget.toggle_show_all,
            state="disabled"
        )
        self.show_all_btn.pack(pady=5)

    def select_line_tool(self):
        self.editor.current_tool = "line"
        self.line_tool_btn.configure(fg_color="#3B8ED0")
        self.other_tool_btn.configure(fg_color=("gray75", "gray25"))
        self.line_tool_frame.pack(fill="x", padx=10, pady=10)

    def select_other_tool(self):
        self.editor.current_tool = "other"
        self.line_tool_btn.configure(fg_color=("gray75", "gray25"))
        self.other_tool_btn.configure(fg_color="#3B8ED0")
        self.line_tool_frame.pack_forget()

    def on_algorithm_change(self):
        self.editor.selected_algorithm = self.algorithm_var.get()

    def toggle_debug_mode(self):
        self.editor.canvas_widget.toggle_debug_mode()