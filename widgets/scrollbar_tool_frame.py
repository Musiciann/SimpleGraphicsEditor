import customtkinter as ctk

class ScrollableToolFrame(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.canvas = ctk.CTkCanvas(self, highlightthickness=0, bg=self._fg_color[1] if ctk.get_appearance_mode() == "Dark" else self._fg_color[0])
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self._handle_scrollbar_set)

        self.inner_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.inner_frame.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.bind("<Configure>", self._on_self_configure)
        self._bind_mousewheel()

    def _handle_scrollbar_set(self, first, last):
        self.scrollbar.set(first, last)
        self.check_scrollbar_visibility()

    def _on_inner_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_self_configure(self, event):
        self.after_idle(self.check_scrollbar_visibility)

    def check_scrollbar_visibility(self):
        self.update_idletasks()
        canvas_height = self.canvas.winfo_height()
        bbox = self.canvas.bbox("all")
        if bbox:
            content_height = bbox[3] - bbox[1]
            if content_height > canvas_height:
                self.scrollbar.pack(side="right", fill="y")
            else:
                self.scrollbar.pack_forget()

    def _bind_mousewheel(self):
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.canvas.bind("<MouseWheel>", on_mousewheel)
        self.inner_frame.bind("<MouseWheel>", on_mousewheel)

    def clear_mousewheel_binding(self):
        self.canvas.unbind("<MouseWheel>")
        self.inner_frame.unbind("<MouseWheel>")
