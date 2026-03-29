import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from .styles import ModernStyle


class ImagePanel:
    def __init__(self, parent):
        self.parent = parent
        self.normal_width = 400
        self.maximized_width = 800
        
        self.frame = ttk.LabelFrame(parent, text="  Preview  ", padding="10", width=self.normal_width)
        self.frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        self.frame.pack_propagate(False)
        
        self.canvas = ModernStyle.create_styled_canvas(self.frame)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.original_image = None
        self.current_image = None
        self.image_scale = 1.0
        self.image_offset_x = 0
        self.image_offset_y = 0
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False
        self.cached_image = None
        self.cached_scale = 0
        self.canvas_image_id = None
        
        self.canvas.bind("<MouseWheel>", self.on_scroll)
        self.canvas.bind("<Button-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_end)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<Configure>", self._on_resize)
        
        self.placeholder_shown = False
        self.after_id = None
        
        self._check_window_state()
    
    def _check_window_state(self):
        try:
            toplevel = self.frame.winfo_toplevel()
            if toplevel:
                is_maximized = toplevel.state() == 'zoomed'
                new_width = self.maximized_width if is_maximized else self.normal_width
                if self.frame.winfo_width() != new_width:
                    self.frame.configure(width=new_width)
        except:
            pass
        self.frame.after(200, self._check_window_state)
        
    def _on_resize(self, event):
        if self.original_image is None and not self.placeholder_shown:
            self.show_placeholder()
        elif self.original_image is not None:
            self.fit_to_canvas()
    
    def show_placeholder(self):
        self.canvas.delete("all")
        self.canvas_image_id = None
        self.placeholder_shown = True
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width < 10 or canvas_height < 10:
            if self.after_id:
                self.canvas.after_cancel(self.after_id)
            self.after_id = self.canvas.after(100, self.show_placeholder)
            return
        
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        self.canvas.create_rectangle(
            center_x - 60, center_y - 60,
            center_x + 60, center_y + 60,
            outline=ModernStyle.COLORS['border'],
            width=2,
            dash=(5, 3)
        )
        
        self.canvas.create_text(
            center_x, center_y - 20,
            text="🖼",
            font=('Segoe UI', 32),
            fill=ModernStyle.COLORS['text_muted']
        )
        
        self.canvas.create_text(
            center_x, center_y + 35,
            text="Drag image here\nor select from list",
            font=ModernStyle.FONTS['body'],
            fill=ModernStyle.COLORS['text_muted'],
            justify=tk.CENTER
        )
        
        hint_y = canvas_height - 30
        self.canvas.create_text(
            center_x, hint_y,
            text="Scroll to zoom · Drag to pan · Double-click to reset",
            font=ModernStyle.FONTS['small'],
            fill=ModernStyle.COLORS['text_muted'],
            justify=tk.CENTER
        )
    
    def show_image(self, img):
        self.original_image = img.copy()
        self.placeholder_shown = False
        self.image_scale = 1.0
        self.image_offset_x = 0
        self.image_offset_y = 0
        self.cached_image = None
        self.cached_scale = 0
        self.canvas_image_id = None
        self.fit_to_canvas()
    
    def fit_to_canvas(self):
        if self.original_image is None:
            return
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width < 10 or canvas_height < 10:
            canvas_width = 400
            canvas_height = 600
        
        img_width, img_height = self.original_image.size
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        self.image_scale = min(scale_x, scale_y, 1.0) * 0.95
        
        self.image_offset_x = 0
        self.image_offset_y = 0
        
        self.update_display()
    
    def update_display(self):
        if self.original_image is None:
            return
        
        img_width, img_height = self.original_image.size
        new_width = int(img_width * self.image_scale)
        new_height = int(img_height * self.image_scale)
        
        if new_width < 1 or new_height < 1:
            return
        
        scale_key = (new_width, new_height)
        if self.cached_image is None or self.cached_scale != scale_key:
            resized_image = self.original_image.resize((new_width, new_height), Image.LANCZOS)
            self.cached_image = ImageTk.PhotoImage(resized_image)
            self.cached_scale = scale_key
        
        self.current_image = self.cached_image
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        x = (canvas_width - new_width) // 2 + self.image_offset_x
        y = (canvas_height - new_height) // 2 + self.image_offset_y
        
        if self.canvas_image_id is None:
            self.canvas.delete("all")
            self.canvas_image_id = self.canvas.create_image(x, y, anchor=tk.NW, image=self.current_image)
        else:
            self.canvas.coords(self.canvas_image_id, x, y)
            self.canvas.itemconfig(self.canvas_image_id, image=self.current_image)
    
    def on_scroll(self, event):
        if self.original_image is None:
            return
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        mouse_x = self.canvas.canvasx(event.x)
        mouse_y = self.canvas.canvasy(event.y)
        
        center_x = canvas_width / 2 + self.image_offset_x
        center_y = canvas_height / 2 + self.image_offset_y
        
        rel_x = mouse_x - center_x
        rel_y = mouse_y - center_y
        
        old_scale = self.image_scale
        
        if event.delta > 0:
            self.image_scale *= 1.1
        else:
            self.image_scale /= 1.1
        
        self.image_scale = max(0.1, min(10.0, self.image_scale))
        
        scale_ratio = self.image_scale / old_scale
        self.image_offset_x -= rel_x * (scale_ratio - 1)
        self.image_offset_y -= rel_y * (scale_ratio - 1)
        
        self.update_display()
        return "break"
    
    def on_drag_start(self, event):
        if self.original_image is None:
            return
        
        self.is_dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.canvas.config(cursor="hand2")
    
    def on_drag(self, event):
        if not self.is_dragging or self.original_image is None:
            return
        
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        
        self.image_offset_x += dx
        self.image_offset_y += dy
        
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        self.update_display()
    
    def on_drag_end(self, event):
        self.is_dragging = False
        self.canvas.config(cursor="")
    
    def on_double_click(self, event):
        if self.original_image is None:
            return
        self.fit_to_canvas()
