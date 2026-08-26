import tkinter as tk

class HoverButton(tk.Button):
    """Botão flat personalizado com efeito hover automático"""
    def __init__(self, master=None, bg_normal="#2B2B2B", bg_hover="#3A3A3A", fg_normal="#FFFFFF", fg_hover="#00E5FF", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.bg_normal = bg_normal or self.cget("bg")
        self.bg_hover = bg_hover or self.bg_normal
        self.fg_normal = fg_normal or self.cget("fg")
        self.fg_hover = fg_hover or self.fg_normal

        self.configure(
            bg=self.bg_normal,
            fg=self.fg_normal,
            activebackground=self.bg_hover,
            activeforeground=self.fg_hover,
            bd=0,
            relief="flat",
            cursor="hand2"
        )

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        self.configure(bg=self.bg_hover, fg=self.fg_hover)

    def _on_leave(self, event):
        self.configure(bg=self.bg_normal, fg=self.fg_normal)
