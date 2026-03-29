import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image
from tkinterdnd2 import TkinterDnD, DND_FILES
import os

from parsers import MetadataParser
from ui import ImagePanel, FileListPanel, ResultPanel, ModernStyle
from utils import shorten_filename, parse_dropped_files, get_timestamp


class ComfyUIMetadataReader:
    def __init__(self, root):
        self.root = root
        self.root.title("ComfyUI Metadata Reader")
        self.root.geometry("1200x750")
        self.root.resizable(True, True)
        
        self.root.configure(bg=ModernStyle.COLORS['bg_primary'])
        ModernStyle.configure_style(self.root)
        
        self.parser = MetadataParser()
        self.current_file = ""
        self.operation_history = []
        
        self.main_frame = ttk.Frame(self.root, padding="15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.file_list_panel = FileListPanel(
            self.main_frame,
            on_file_select=self.on_file_select,
            shorten_filename_func=shorten_filename
        )
        
        self.image_panel = ImagePanel(self.main_frame)
        
        self.result_panel = ResultPanel(
            self.main_frame,
            clipboard_func=self.copy_to_clipboard,
            status_func=self.update_status
        )
        
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=8, padx=15)
        
        self.status_label = ttk.Label(
            self.status_frame, 
            text="File list: 0 files", 
            anchor=tk.W,
            font=ModernStyle.FONTS['body']
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.detail_button = ttk.Button(
            self.status_frame, 
            text="ℹ", 
            width=3, 
            command=self.show_details
        )
        self.detail_button.pack(side=tk.RIGHT, padx=5)
        
        self.detail_window = None
        
        self.setup_drag_drop()
    
    def setup_drag_drop(self):
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.on_drop)
        
        self.image_panel.canvas.drop_target_register(DND_FILES)
        self.image_panel.canvas.dnd_bind("<<Drop>>", self.on_drop)
        
        self.file_list_panel.list_container.drop_target_register(DND_FILES)
        self.file_list_panel.list_container.dnd_bind("<<Drop>>", self.on_drop)
    
    def on_drop(self, event):
        paths = parse_dropped_files(event.data)
        
        if paths:
            added = self.file_list_panel.add_files(paths)
            if added > 0:
                self.update_status(f"Added {added} file(s) to list")
            else:
                self.update_status("File already in list")
    
    def on_file_select(self, file_path):
        self.process_file(file_path)
    
    def process_file(self, file_path):
        try:
            self.current_file = file_path
            with Image.open(file_path) as img:
                self.image_panel.show_image(img)
                metadata = self.parser.parse(img)
                self.result_panel.update(metadata, file_path)
                
                filename = os.path.basename(file_path)
                self.update_status(f"Displaying: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error processing file: {str(e)}")
    
    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
    
    def update_status(self, message):
        timestamp = get_timestamp()
        self.operation_history.append(f"[{timestamp}] {message}")
        if len(self.operation_history) > 50:
            self.operation_history = self.operation_history[-50:]
        
        file_count = self.file_list_panel.get_count()
        status_text = f"File list: {file_count} files | {message}"
        self.status_label.config(text=status_text)
        
        self.update_detail_window()
    
    def show_details(self):
        if self.detail_window and self.detail_window.winfo_exists():
            self.detail_window.lift()
            self.detail_window.focus_set()
            self.update_detail_window()
            return
        
        self.detail_window = tk.Toplevel(self.root)
        self.detail_window.title("History")
        self.detail_window.geometry("450x350")
        self.detail_window.configure(bg=ModernStyle.COLORS['bg_primary'])
        
        def on_close():
            if self.detail_window:
                self.detail_window.destroy()
                self.detail_window = None
        
        self.detail_window.protocol("WM_DELETE_WINDOW", on_close)
        
        self.detail_text = ModernStyle.create_styled_text(self.detail_window, wrap=tk.WORD)
        self.detail_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.update_detail_window()
    
    def update_detail_window(self):
        if hasattr(self, 'detail_text') and self.detail_text.winfo_exists():
            self.detail_text.config(state=tk.NORMAL)
            self.detail_text.delete(1.0, tk.END)
            
            if self.operation_history:
                for i, operation in enumerate(reversed(self.operation_history)):
                    self.detail_text.insert(tk.END, f"{i+1}. {operation}\n")
            else:
                self.detail_text.insert(tk.END, "No history")
            
            self.detail_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = ComfyUIMetadataReader(root)
    root.mainloop()
