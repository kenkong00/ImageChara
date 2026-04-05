import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import os

from .styles import ModernStyle


class FileListPanel:
    def __init__(self, parent, on_file_select, shorten_filename_func, on_create_character=None, on_clear_preview=None):
        self.on_file_select = on_file_select
        self.shorten_filename = shorten_filename_func
        self.on_create_character = on_create_character
        self.on_clear_preview = on_clear_preview
        
        self.frame = ttk.LabelFrame(parent, text="  Files  ", padding="10", width=320)
        self.frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        self.frame.pack_propagate(False)
        
        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.import_file_button = ttk.Button(
            self.button_frame, 
            text="📁File", 
            command=self.import_files, 
            width=6
        )
        self.import_file_button.pack(side=tk.LEFT, padx=1)
        
        self.import_dir_button = ttk.Button(
            self.button_frame, 
            text="📂Dir", 
            command=self.import_dir, 
            width=6
        )
        self.import_dir_button.pack(side=tk.LEFT, padx=1)
        
        self.clear_button = ttk.Button(
            self.button_frame, 
            text="🗑Clear", 
            command=self.clear, 
            width=6
        )
        self.clear_button.pack(side=tk.LEFT, padx=1)
        
        self.list_style = "list"
        self.toggle_button = ttk.Button(
            self.button_frame, 
            text="🖼Thumb", 
            command=self.toggle_style, 
            width=6
        )
        self.toggle_button.pack(side=tk.LEFT, padx=1)
        
        self.create_char_button = ttk.Button(
            self.button_frame, 
            text="👤Char", 
            command=self.create_character, 
            width=6
        )
        self.create_char_button.pack(side=tk.LEFT, padx=1)
        
        self.list_container = ttk.Frame(self.frame)
        self.list_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.file_list = ModernStyle.create_styled_listbox(self.list_container, height=30, selectmode=tk.EXTENDED)
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scrollbar = ttk.Scrollbar(self.list_container, orient=tk.VERTICAL, command=self.file_list.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_list.config(yscrollcommand=self.scrollbar.set)
        
        self.file_list.bind("<<ListboxSelect>>", self._on_select)
        self.file_list.bind("<Delete>", self._on_delete_key)
        self.file_list.bind("<Button-3>", self._on_right_click)
        
        self.thumbnail_container = ttk.Frame(self.frame)
        self.thumbnail_container.pack_forget()
        
        self.thumbnail_scrollbar = ttk.Scrollbar(self.thumbnail_container, orient=tk.VERTICAL)
        self.thumbnail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.thumbnail_canvas = ModernStyle.create_styled_canvas(
            self.thumbnail_container, 
            yscrollcommand=self.thumbnail_scrollbar.set
        )
        self.thumbnail_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.thumbnail_scrollbar.config(command=self.thumbnail_canvas.yview)
        
        self.thumbnail_frame = ttk.Frame(self.thumbnail_canvas)
        self.thumbnail_canvas.create_window((0, 0), window=self.thumbnail_frame, anchor=tk.NW)
        
        self.thumbnail_canvas.bind("<MouseWheel>", self._on_thumbnail_scroll)
        self.thumbnail_frame.bind("<MouseWheel>", self._on_thumbnail_scroll)
        
        self.thumbnail_items = []
        self.file_paths = []
        self.selected_index = -1
        self.selected_thumbnail_index = -1
        self.selected_thumbnail_indices = set()
        self._last_clicked_thumbnail = -1
    
    def _on_select(self, event):
        selection = self.file_list.curselection()
        if selection:
            index = selection[-1]
            if index < len(self.file_paths):
                self.selected_index = index
                self.on_file_select(self.file_paths[index])
    
    def _on_delete_key(self, event):
        self._remove_selected_files()
    
    def _on_right_click(self, event):
        selection = self.file_list.curselection()
        if selection:
            menu = tk.Menu(self.frame, tearoff=0)
            menu.add_command(label="Delete selected", command=self._remove_selected_files)
            menu.tk_popup(event.x_root, event.y_root)
    
    def _remove_selected_files(self):
        selection = self.file_list.curselection()
        if not selection:
            return
        
        for index in reversed(selection):
            if 0 <= index < len(self.file_paths):
                del self.file_paths[index]
                self.file_list.delete(index)
        
        if self.list_style == "thumbnail":
            self.update_thumbnail_view()
        
        self.selected_index = -1
        self.selected_thumbnail_index = -1
        
        if self.on_clear_preview:
            self.on_clear_preview()
    
    def _on_thumbnail_scroll(self, event):
        delta = event.delta // 120
        self.thumbnail_canvas.yview_scroll(-delta, "units")
        return "break"
    
    def import_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Image Files",
            filetypes=[("Image Files", "*.png *.webp *.jpg *.jpeg"), ("PNG Images", "*.png"), ("WebP Images", "*.webp"), ("JPEG Images", "*.jpg *.jpeg"), ("All Files", "*.*")]
        )
        if file_paths:
            added = 0
            for fp in file_paths:
                if os.path.isfile(fp) and fp not in self.file_paths:
                    self.file_paths.append(fp)
                    self.file_list.insert(tk.END, self.shorten_filename(os.path.basename(fp)))
                    added += 1
            if added > 0:
                if self.list_style == "thumbnail":
                    self.update_thumbnail_view()
                return added
        return 0
    
    def import_dir(self):
        directory = filedialog.askdirectory(title="Select Image Directory")
        if directory:
            added = 0
            for filename in os.listdir(directory):
                if filename.lower().endswith(('.png', '.webp', '.jpg', '.jpeg')):
                    fp = os.path.join(directory, filename)
                    if fp not in self.file_paths:
                        self.file_paths.append(fp)
                        self.file_list.insert(tk.END, self.shorten_filename(filename))
                        added += 1
            if added > 0:
                if self.list_style == "thumbnail":
                    self.update_thumbnail_view()
                return added
        return 0
    
    def add_files(self, paths):
        added = 0
        last_index = -1
        for path in paths:
            if os.path.isfile(path) and path not in self.file_paths:
                self.file_paths.append(path)
                self.file_list.insert(tk.END, self.shorten_filename(os.path.basename(path)))
                last_index = len(self.file_paths) - 1
                added += 1
        if added > 0:
            if self.list_style == "thumbnail":
                self.update_thumbnail_view()
            self.select_index(last_index)
            if self.list_style == "thumbnail":
                self.selected_thumbnail_index = last_index
                self._update_thumbnail_selection()
            if last_index >= 0:
                self.on_file_select(self.file_paths[last_index])
        return added
    
    def add_and_select_file(self, file_path):
        if os.path.isfile(file_path) and file_path not in self.file_paths:
            self.file_paths.append(file_path)
            self.file_list.insert(tk.END, self.shorten_filename(os.path.basename(file_path)))
            index = len(self.file_paths) - 1
            
            if self.list_style == "thumbnail":
                self.update_thumbnail_view()
            
            self.select_index(index)
            
            if self.list_style == "thumbnail":
                self.selected_thumbnail_index = index
                self.selected_thumbnail_indices = {index}
                self._last_clicked_thumbnail = index
                self._update_thumbnail_selection()
            
            self.on_file_select(file_path)
            return True
        return False
    
    def clear(self):
        self.file_list.delete(0, tk.END)
        self.file_paths = []
        for item in self.thumbnail_items:
            item.destroy()
        self.thumbnail_items = []
        self.thumbnail_frame.update_idletasks()
        self.thumbnail_canvas.config(scrollregion=self.thumbnail_canvas.bbox("all"))
        self.selected_index = -1
        self.selected_thumbnail_index = -1
        self.selected_thumbnail_indices = set()
        self._last_clicked_thumbnail = -1
        
        if self.on_clear_preview:
            self.on_clear_preview()
    
    def toggle_style(self):
        if self.list_style == "list":
            self.list_style = "thumbnail"
            self.toggle_button.config(text="📝List")
            self.list_container.pack_forget()
            self.thumbnail_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            selection = self.file_list.curselection()
            if selection:
                self.selected_thumbnail_indices = set(selection)
                if selection:
                    self.selected_thumbnail_index = selection[-1]
                    self._last_clicked_thumbnail = selection[-1]
            self.update_thumbnail_view()
        else:
            self.list_style = "list"
            self.toggle_button.config(text="🖼Thumb")
            self.thumbnail_container.pack_forget()
            self.list_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.thumbnail_canvas.unbind_all("<Delete>")
            saved_selection = self.selected_thumbnail_indices.copy()
            self.selected_thumbnail_indices = set()
            self._last_clicked_thumbnail = -1
            for idx in saved_selection:
                if 0 <= idx < len(self.file_paths):
                    self.file_list.selection_set(idx)
    
    def update_thumbnail_view(self):
        for item in self.thumbnail_items:
            item.destroy()
        self.thumbnail_items = []
        
        row, col = 0, 0
        max_cols = 2
        
        for i, fp in enumerate(self.file_paths):
            try:
                img = Image.open(fp)
                img.thumbnail((120, 120), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                thumb_frame = tk.Frame(
                    self.thumbnail_frame, 
                    bg=ModernStyle.COLORS['bg_secondary'],
                    highlightthickness=2,
                    highlightbackground=ModernStyle.COLORS['border'],
                    highlightcolor=ModernStyle.COLORS['accent_primary'],
                    width=134, 
                    height=158
                )
                if i in self.selected_thumbnail_indices:
                    thumb_frame.configure(
                        highlightbackground=ModernStyle.COLORS['accent_primary']
                    )
                thumb_frame.grid(row=row, column=col, padx=3, pady=5, sticky=tk.NSEW)
                thumb_frame.pack_propagate(False)
                
                thumb_label = tk.Label(
                    thumb_frame, 
                    image=photo, 
                    cursor="hand2", 
                    bg=ModernStyle.COLORS['bg_secondary'],
                    padx=0, 
                    pady=0
                )
                thumb_label.image = photo
                thumb_label.pack(padx=0, pady=(5, 2))
                
                name_label = tk.Label(
                    thumb_frame, 
                    text=self.shorten_filename(os.path.basename(fp), 15), 
                    font=ModernStyle.FONTS['small'],
                    fg=ModernStyle.COLORS['text_secondary'],
                    bg=ModernStyle.COLORS['bg_secondary'],
                    wraplength=120, 
                    anchor=tk.CENTER
                )
                name_label.pack(pady=(0, 5))
                
                thumb_frame.bind("<Button-1>", lambda e, idx=i: self._on_thumbnail_click(e, idx))
                thumb_label.bind("<Button-1>", lambda e, idx=i: self._on_thumbnail_click(e, idx))
                name_label.bind("<Button-1>", lambda e, idx=i: self._on_thumbnail_click(e, idx))
                
                thumb_frame.bind("<Button-3>", lambda e, idx=i: self._on_thumbnail_right_click(e, idx))
                thumb_label.bind("<Button-3>", lambda e, idx=i: self._on_thumbnail_right_click(e, idx))
                name_label.bind("<Button-3>", lambda e, idx=i: self._on_thumbnail_right_click(e, idx))
                
                thumb_frame.bind("<MouseWheel>", self._on_thumbnail_scroll)
                thumb_label.bind("<MouseWheel>", self._on_thumbnail_scroll)
                name_label.bind("<MouseWheel>", self._on_thumbnail_scroll)
                
                thumb_frame.bind("<Enter>", lambda e, f=thumb_frame: self._on_thumbnail_hover(f, True))
                thumb_frame.bind("<Leave>", lambda e, f=thumb_frame, idx=i: self._on_thumbnail_hover(f, False, idx))
                
                self.thumbnail_items.append(thumb_frame)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            except:
                pass
        
        self.thumbnail_frame.update_idletasks()
        self.thumbnail_canvas.config(scrollregion=self.thumbnail_canvas.bbox("all"))
        
        self.thumbnail_canvas.bind_all("<Delete>", self._on_thumbnail_delete_key)
    
    def _on_thumbnail_hover(self, frame, is_enter, index=-1):
        if is_enter:
            frame.configure(highlightbackground=ModernStyle.COLORS['hover'])
        else:
            if index in self.selected_thumbnail_indices:
                frame.configure(highlightbackground=ModernStyle.COLORS['accent_primary'])
            else:
                frame.configure(highlightbackground=ModernStyle.COLORS['border'])
    
    def _on_thumbnail_click(self, event, index):
        if index < len(self.file_paths):
            if event.state & 0x0004:
                if index in self.selected_thumbnail_indices:
                    self.selected_thumbnail_indices.discard(index)
                else:
                    self.selected_thumbnail_indices.add(index)
            elif event.state & 0x0001:
                start = min(self._last_clicked_thumbnail, index)
                end = max(self._last_clicked_thumbnail, index)
                self.selected_thumbnail_indices = set(range(start, end + 1))
            else:
                self.selected_thumbnail_indices = {index}
            
            self._last_clicked_thumbnail = index
            
            if self.selected_thumbnail_indices:
                last_selected = max(self.selected_thumbnail_indices)
                self.selected_thumbnail_index = last_selected
                self.selected_index = last_selected
                self.on_file_select(self.file_paths[last_selected])
            
            self._update_thumbnail_selection()
    
    def _on_thumbnail_right_click(self, event, index):
        if index not in self.selected_thumbnail_indices:
            self.selected_thumbnail_indices = {index}
            self._last_clicked_thumbnail = index
            self._update_thumbnail_selection()
        
        menu = tk.Menu(self.frame, tearoff=0)
        menu.add_command(label="Delete selected", command=self._remove_selected_thumbnails)
        menu.tk_popup(event.x_root, event.y_root)
    
    def _on_thumbnail_delete_key(self, event):
        if self.list_style == "thumbnail" and self.selected_thumbnail_indices:
            self._remove_selected_thumbnails()
    
    def _remove_selected_thumbnails(self):
        if not self.selected_thumbnail_indices:
            return
        
        indices_to_remove = sorted(self.selected_thumbnail_indices, reverse=True)
        
        for index in indices_to_remove:
            if 0 <= index < len(self.file_paths):
                del self.file_paths[index]
                self.file_list.delete(index)
        
        self.selected_thumbnail_indices = set()
        self.selected_index = -1
        self.selected_thumbnail_index = -1
        self._last_clicked_thumbnail = -1
        
        self.update_thumbnail_view()
        
        if self.on_clear_preview:
            self.on_clear_preview()
    
    def _update_thumbnail_selection(self):
        for i, item in enumerate(self.thumbnail_items):
            if i in self.selected_thumbnail_indices:
                item.configure(highlightbackground=ModernStyle.COLORS['accent_primary'])
            else:
                item.configure(highlightbackground=ModernStyle.COLORS['border'])
    
    def select_index(self, index):
        if 0 <= index < len(self.file_paths):
            self.selected_index = index
            self.file_list.selection_clear(0, tk.END)
            self.file_list.selection_set(index)
            self.file_list.activate(index)
    
    def get_count(self):
        return len(self.file_paths)
    
    def create_character(self):
        if self.on_create_character:
            self.on_create_character()
