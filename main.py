import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from tkinterdnd2 import TkinterDnD, DND_FILES
import os

from parsers import MetadataParser
from ui import ImagePanel, FileListPanel, ResultPanel, ModernStyle
from utils import shorten_filename, parse_dropped_files, get_timestamp


class ComfyUIMetadataReader:
    def __init__(self, root):
        self.root = root
        self.root.title("图灵注 ImageChara")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Set window icon
        try:
            if os.path.exists('logo_256x256.png'):
                icon_image = Image.open('logo_256x256.png')
                icon_photo = ImageTk.PhotoImage(icon_image)
                self.root.iconphoto(True, icon_photo)
        except:
            pass
        
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
            shorten_filename_func=shorten_filename,
            on_create_character=self.create_character,
            on_clear_preview=self.clear_preview,
            on_export_json=self.export_to_json
        )
        
        self.image_panel = ImagePanel(self.main_frame)
        
        self.result_panel = ResultPanel(
            self.main_frame,
            clipboard_func=self.copy_to_clipboard,
            status_func=self.update_status,
            on_file_added=self.on_file_added
        )
        
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5, padx=15)

        self.status_label = ttk.Label(
            self.status_frame,
            text="File list: 0 files",
            anchor=tk.W,
            font=ModernStyle.FONTS['small']
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.detail_button = ttk.Button(
            self.status_frame,
            text="  i ",
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
            try:
                added = self.file_list_panel.add_files(paths)
            except Exception as e:
                added = 0

            if added > 0:
                self.update_status(f"Added {added} file(s) to list")
                last_index = len(self.file_list_panel.file_paths) - 1
                self.file_list_panel.select_index(last_index)
                file_path = self.file_list_panel.file_paths[last_index]
                try:
                    self.process_file(file_path)
                except Exception as e:
                    pass
            else:
                self.update_status("File already in list")
    
    def on_file_select(self, file_path):
        self.process_file(file_path)

    def clear_preview(self):
        self.image_panel.clear_image()
        self.result_panel.clear()

    def on_file_added(self, file_path):
        self.file_list_panel.add_and_select_file(file_path)

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
    
    def create_character(self):
        from tkinter import simpledialog, filedialog
        import json
        
        # Create character creation dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Create AI Chat Character")
        dialog.geometry("500x600")
        dialog.configure(bg=ModernStyle.COLORS['bg_primary'])
        
        # Character name
        name_label = ttk.Label(dialog, text="Character Name:", font=ModernStyle.FONTS['body'])
        name_label.pack(pady=(20, 5), padx=20, anchor=tk.W)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=40)
        name_entry.pack(pady=(0, 15), padx=20, fill=tk.X)
        
        # Character description
        desc_label = ttk.Label(dialog, text="Description:", font=ModernStyle.FONTS['body'])
        desc_label.pack(pady=(10, 5), padx=20, anchor=tk.W)
        desc_text = ModernStyle.create_styled_text(dialog, wrap=tk.WORD, height=10)
        desc_text.pack(pady=(0, 15), padx=20, fill=tk.X)
        
        # First message
        first_mes_label = ttk.Label(dialog, text="First Message:", font=ModernStyle.FONTS['body'])
        first_mes_label.pack(pady=(10, 5), padx=20, anchor=tk.W)
        first_mes_text = ModernStyle.create_styled_text(dialog, wrap=tk.WORD, height=5)
        first_mes_text.pack(pady=(0, 15), padx=20, fill=tk.X)
        
        # Scenario
        scenario_label = ttk.Label(dialog, text="Scenario:", font=ModernStyle.FONTS['body'])
        scenario_label.pack(pady=(10, 5), padx=20, anchor=tk.W)
        scenario_text = ModernStyle.create_styled_text(dialog, wrap=tk.WORD, height=5)
        scenario_text.pack(pady=(0, 20), padx=20, fill=tk.X)
        
        def save_character():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Character name is required")
                return
            
            desc = desc_text.get(1.0, tk.END).strip()
            first_mes = first_mes_text.get(1.0, tk.END).strip()
            scenario = scenario_text.get(1.0, tk.END).strip()
            
            # Create character data
            chara_data = {
                "name": name,
                "description": desc,
                "first_mes": first_mes,
                "scenario": scenario,
                "avatar": "none",
                "chara": f"{name} - {desc[:30]}...",
                "create_date": "2026-04-05",
                "data": {
                    "character_books": []
                }
            }
            
            # Save as JSON
            file_path = filedialog.asksaveasfilename(
                title="Save Character",
                defaultextension=".json",
                initialfile=name.replace(' ', '_'),
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
            )
            
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(chara_data, f, ensure_ascii=False, indent=2)
                    messagebox.showinfo("Success", f"Character saved to {file_path}")
                    self.update_status(f"Created character: {name}")
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Error saving character: {str(e)}")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20, padx=20, fill=tk.X)
        
        save_button = ttk.Button(button_frame, text="💾 Save", command=save_character, width=15)
        save_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="❌ Cancel", command=dialog.destroy, width=15)
        cancel_button.pack(side=tk.RIGHT, padx=5)

    def export_to_json(self):
        from tkinter import filedialog
        import json

        file_paths = self.file_list_panel.file_paths
        if not file_paths:
            messagebox.showwarning("Warning", "File list is empty")
            return

        save_path = filedialog.asksaveasfilename(
            title="Export Prompts to JSON",
            defaultextension=".json",
            initialfile="prompts_export",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if not save_path:
            return

        try:
            result_list = []
            success_count = 0
            fail_count = 0

            for i, file_path in enumerate(file_paths):
                filename = os.path.basename(file_path)
                try:
                    with Image.open(file_path) as img:
                        metadata = self.parser.parse(img)
                        prompt = metadata.get('prompt', '')

                        item = {
                            "id": filename,
                            "prompt": prompt
                        }
                        result_list.append(item)
                        success_count += 1
                except Exception as e:
                    item = {
                        "id": filename,
                        "prompt": f"Error: {str(e)}"
                    }
                    result_list.append(item)
                    fail_count += 1

            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(result_list, f, ensure_ascii=False, indent=2)

            self.update_status(f"Exported {success_count} prompts to JSON ({fail_count} failed)")
            messagebox.showinfo("Success", f"Successfully exported {success_count} prompts to:\n{save_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Error exporting to JSON: {str(e)}")


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = ComfyUIMetadataReader(root)
    root.mainloop()
