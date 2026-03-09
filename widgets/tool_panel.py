import customtkinter as ctk
from .scrollbar_tool_frame import ScrollableToolFrame
from .constants import PRIMARY_BLUE, PRIMARY_BLUE_DARK, PRIMARY_BLUE_HOVER, PRIMARY_BLUE_HOVER_DARK

class ToolPanel:
    def __init__(self, editor):
        self.editor = editor

        self.tool_frame = ScrollableToolFrame(
            editor.root, width=300,
            corner_radius=15,
            border_width=2,
            border_color=("#4a4a4a", "#2b2b2b"),
            fg_color=("#2b2b2b", "#1e1e1e")
        )

        self.debug_var = ctk.BooleanVar(value=False)
        self.grid_var = ctk.BooleanVar(value=False)
        self.algorithm_var = ctk.StringVar(value="DDA")
        self.curve_type_var = ctk.StringVar(value="circle")

        self._create_widgets()

    def pack_widget(self):
        self.tool_frame.pack(side="right", fill="y", padx=5, pady=5)
        self.tool_frame.after_idle(self.tool_frame.check_scrollbar_visibility)

    def hide(self):
        self.tool_frame.pack_forget()

    def show(self):
        self.pack_widget()

    def _create_widgets(self):
        inner = self.tool_frame.inner_frame

        ctk.CTkLabel(inner, text="Инструменты",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=("#3a7eb6", "#4a8ec6")).pack(pady=(15, 10))

        btn_style = {
            "height": 45,
            "corner_radius": 12,
            "fg_color": (PRIMARY_BLUE, PRIMARY_BLUE_DARK),
            "hover_color": (PRIMARY_BLUE_HOVER, PRIMARY_BLUE_HOVER_DARK),
            "border_spacing": 10,
            "font": ctk.CTkFont(size=13, weight="bold")
        }

        self.line_tool_btn = ctk.CTkButton(inner, text="Отрезок", command=self.select_line_tool, **btn_style)
        self.line_tool_btn.pack(pady=10, padx=15)

        self.curves_tool_btn = ctk.CTkButton(inner, text="Кривые", command=self.select_curves_tool, **btn_style)
        self.curves_tool_btn.pack(pady=10, padx=15)

        self.spline_tool_btn = ctk.CTkButton(inner, text="Параметрические кривые", command=self.select_spline_tool, **btn_style)
        self.spline_tool_btn.pack(pady=10, padx=15)

        self.other_tool_btn = ctk.CTkButton(inner, text="Другой инструмент", command=self.select_other_tool, **btn_style)
        self.other_tool_btn.pack(pady=10, padx=15)

        self.common_settings_frame = ctk.CTkFrame(inner, fg_color="transparent")
        self.common_settings_frame.pack(fill="x", padx=10, pady=15)

        ctk.CTkLabel(self.common_settings_frame,
                     text="Общие настройки",
                     font=ctk.CTkFont(weight="bold")).pack(pady=5)

        scale_frame = ctk.CTkFrame(self.common_settings_frame, fg_color="transparent")
        scale_frame.pack(fill="x", padx=10, pady=5)

        self.zoom_out_btn = ctk.CTkButton(scale_frame, text="-", width=40,
                                          command=self.editor.canvas_widget.zoom_out)
        self.zoom_out_btn.pack(side="left", padx=5)

        self.zoom_label = ctk.CTkLabel(scale_frame, text="Масштаб", width=60)
        self.zoom_label.pack(side="left", padx=5)

        self.zoom_in_btn = ctk.CTkButton(scale_frame, text="+", width=40,
                                         command=self.editor.canvas_widget.zoom_in)
        self.zoom_in_btn.pack(side="left", padx=5)

        self.reset_zoom_btn = ctk.CTkButton(scale_frame, text="Сброс", width=60,
                                            command=self.editor.canvas_widget.reset_zoom)
        self.reset_zoom_btn.pack(side="left", padx=5)

        self.grid_checkbox = ctk.CTkCheckBox(
            self.common_settings_frame,
            text="Показать сетку",
            variable=self.grid_var,
            command=self.editor.canvas_widget.toggle_grid,
            checkbox_width=20, checkbox_height=20, corner_radius=4,
            border_width=2, fg_color=PRIMARY_BLUE, hover_color=PRIMARY_BLUE_DARK,
            font=ctk.CTkFont(size=12)
        )
        self.grid_checkbox.pack(pady=5, padx=10)

        control_frame = ctk.CTkFrame(self.common_settings_frame)
        control_frame.pack(fill="x", padx=10, pady=10)

        self.clear_btn = ctk.CTkButton(control_frame, text="Очистить холст",
                                       command=self.editor.canvas_widget.clear_canvas)
        self.clear_btn.pack(pady=5)

        self.reset_view_btn = ctk.CTkButton(control_frame, text="Сброс вида",
                                            command=self.editor.canvas_widget.reset_view)
        self.reset_view_btn.pack(pady=5)

        self.line_tool_frame = ctk.CTkFrame(inner)
        self.line_tool_frame.pack_forget()
        self.setup_line_tool_functionality()

        self.curves_tool_frame = ctk.CTkFrame(inner)
        self.curves_tool_frame.pack_forget()
        self.setup_curves_tool_functionality()

        self.spline_tool_frame = ctk.CTkFrame(inner)
        self.spline_tool_frame.pack_forget()
        self.setup_spline_tool_functionality()

    def _create_step_controls(self, parent):
        step_frame = ctk.CTkFrame(parent)
        step_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(step_frame, text="Пошаговый режим:").pack(anchor="w", pady=2)

        step_controls = ctk.CTkFrame(step_frame)
        step_controls.pack(fill="x", pady=5)

        self.first_btn = ctk.CTkButton(step_controls, text="<<", width=40,
                                       command=self.editor.canvas_widget.first_step,
                                       state="disabled")
        self.first_btn.pack(side="left", padx=2)

        self.prev_btn = ctk.CTkButton(step_controls, text="<", width=40,
                                      command=self.editor.canvas_widget.prev_step,
                                      state="disabled", corner_radius=20,
                                      fg_color="gray30", hover_color="gray20")
        self.prev_btn.pack(side="left", padx=2)

        self.step_label = ctk.CTkLabel(step_controls, text="0/0", width=50)
        self.step_label.pack(side="left", padx=5)

        self.next_btn = ctk.CTkButton(step_controls, text=">", width=40,
                                      command=self.editor.canvas_widget.next_step,
                                      state="disabled", corner_radius=20,
                                      fg_color="gray30", hover_color="gray20")
        self.next_btn.pack(side="left", padx=2)

        self.last_btn = ctk.CTkButton(step_controls, text=">>", width=40,
                                      command=self.editor.canvas_widget.last_step,
                                      state="disabled", corner_radius=20,
                                      fg_color="gray30", hover_color="gray20")
        self.last_btn.pack(side="left", padx=2)

        self.show_all_btn = ctk.CTkButton(
            step_frame,
            text="Показать все",
            width=120,
            command=self.editor.canvas_widget.toggle_show_all,
            state="disabled"
        )
        self.show_all_btn.pack(pady=5)

    def setup_spline_tool_functionality(self):
        for widget in self.spline_tool_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.spline_tool_frame, text="Тип кривой",
                     font=ctk.CTkFont(weight="bold")).pack(pady=5)

        self.spline_mode_var = ctk.StringVar(value="bezier")
        modes = [
            ("Эрмит", "hermite"),
            ("Безье", "bezier"),
            ("B-сплайн", "bspline")
        ]
        for text, value in modes:
            ctk.CTkRadioButton(
                self.spline_tool_frame, text=text,
                variable=self.spline_mode_var, value=value,
                command=self.on_spline_mode_change,
                font=ctk.CTkFont(size=12)
            ).pack(anchor="w", padx=20, pady=2)

        ctk.CTkLabel(self.spline_tool_frame, text="Режим редактирования",
                     font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))

        self.edit_var = ctk.BooleanVar(value=False)
        self.edit_checkbox = ctk.CTkCheckBox(
            self.spline_tool_frame,
            text="Редактировать точки",
            variable=self.edit_var,
            command=self.on_edit_toggled
        )
        self.edit_checkbox.pack(pady=5, padx=10)

        self.bspline_closed_var = ctk.BooleanVar(value=False)
        self.bspline_closed_check = ctk.CTkCheckBox(
            self.spline_tool_frame,
            text="Замкнутый B-сплайн",
            variable=self.bspline_closed_var,
            command=self.on_bspline_closed_change
        )
        self.bspline_closed_check.pack(pady=5, padx=10)
        self.bspline_closed_check.pack_forget()

        self.spline_info_label = ctk.CTkLabel(
            self.spline_tool_frame,
            text="Кликайте для задания точек",
            justify="left"
        )
        self.spline_info_label.pack(pady=5, padx=10)

    def on_edit_toggled(self):
        self.editor.spline_tool.toggle_edit_mode(self.edit_var.get())

    def on_spline_mode_change(self):
        mode = self.spline_mode_var.get()
        self.editor.spline_tool.set_mode(mode)
        if mode == "bspline":
            self.bspline_closed_check.pack(pady=5, padx=10)
        else:
            self.bspline_closed_check.pack_forget()

    def on_bspline_closed_change(self):
        self.editor.spline_tool.set_closed(self.bspline_closed_var.get())

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
                command=self.on_algorithm_change,
                radiobutton_width=18, radiobutton_height=18,
                corner_radius=5, border_width_checked=7,
                fg_color=PRIMARY_BLUE, border_color=PRIMARY_BLUE,
                font=ctk.CTkFont(size=12)
            )
            radio.pack(anchor="w", padx=20, pady=2)

        ctk.CTkLabel(self.line_tool_frame,
                     text="Режим отладки",
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

        self._create_step_controls(self.line_tool_frame)

    def setup_curves_tool_functionality(self):
        for widget in self.curves_tool_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.curves_tool_frame, text="Тип кривой",
                     font=ctk.CTkFont(weight="bold")).pack(pady=5)

        curves_types = [
            ("Окружность", "circle"),
            ("Эллипс", "ellipse"),
            ("Гипербола", "hyperbola"),
            ("Парабола", "parabola")
        ]

        for text, value in curves_types:
            ctk.CTkRadioButton(
                self.curves_tool_frame, text=text,
                variable=self.curve_type_var, value=value,
                command=self.on_curve_type_change,
                font=ctk.CTkFont(size=12)
            ).pack(anchor="w", padx=20, pady=2)

        ctk.CTkLabel(self.curves_tool_frame,
                     text="Режим отладки",
                     font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))

        debug_controls = ctk.CTkFrame(self.curves_tool_frame)
        debug_controls.pack(fill="x", padx=10, pady=5)

        self.debug_checkbox_curves = ctk.CTkCheckBox(
            debug_controls,
            text="Включить отладку",
            variable=self.debug_var,
            command=self.toggle_debug_mode
        )
        self.debug_checkbox_curves.pack(side="left", padx=5)

        self._create_step_controls(self.curves_tool_frame)

        self.curves_info_label = ctk.CTkLabel(self.curves_tool_frame,
                                              text="", justify="left")
        self.curves_info_label.pack(pady=5, padx=10)

        self.on_curve_type_change()

    def on_curve_type_change(self):
        self.editor.selected_curve_type = self.curve_type_var.get()

        hints = {
            "circle": "1. Центр (клик)\n2. Радиус (клик)",
            "ellipse": "1. Центр (клик)\n2. Полуось a (клик)\n3. Полуось b (клик)",
            "hyperbola": "1. Центр (клик)\n2. Полуось a (клик)\n3. Полуось b (клик)",
            "parabola": "1. Вершина (клик)\n2. Параметр p (расст. по X)"
        }
        self.curves_info_label.configure(text=hints[self.editor.selected_curve_type])

    def select_line_tool(self):
        self.editor.current_tool = "line"
        self._highlight_button(self.line_tool_btn)
        self.line_tool_frame.pack(fill="x", padx=10, pady=10)
        self.curves_tool_frame.pack_forget()
        self.spline_tool_frame.pack_forget()

    def select_curves_tool(self):
        self.editor.current_tool = "curves"
        self._highlight_button(self.curves_tool_btn)
        self.curves_tool_frame.pack(fill="x", padx=10, pady=10)
        self.line_tool_frame.pack_forget()
        self.spline_tool_frame.pack_forget()

    def select_spline_tool(self):
        self.editor.current_tool = "spline"
        self._highlight_button(self.spline_tool_btn)
        self.spline_tool_frame.pack(fill="x", padx=10, pady=10)
        self.line_tool_frame.pack_forget()
        self.curves_tool_frame.pack_forget()
        self.editor.spline_tool.reset_state()

    def select_other_tool(self):
        self.editor.current_tool = "other"
        self._highlight_button(self.other_tool_btn)
        self.line_tool_frame.pack_forget()
        self.curves_tool_frame.pack_forget()
        self.spline_tool_frame.pack_forget()

    def _highlight_button(self, active_btn):
        for btn in [self.line_tool_btn, self.curves_tool_btn, self.spline_tool_btn, self.other_tool_btn]:
            btn.configure(fg_color=(PRIMARY_BLUE, PRIMARY_BLUE_DARK))
        active_btn.configure(fg_color=(PRIMARY_BLUE_HOVER, PRIMARY_BLUE_HOVER_DARK))

    def on_algorithm_change(self):
        self.editor.selected_algorithm = self.algorithm_var.get()

    def toggle_debug_mode(self):
        self.editor.canvas_widget.toggle_debug_mode()