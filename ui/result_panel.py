import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os

from .styles import ModernStyle


class ResultPanel:
    def __init__(self, parent, clipboard_func, status_func):
        self.clipboard_func = clipboard_func
        self.status_func = status_func
        self.metadata = {}
        self.file_path = ""
        
        self.frame = ttk.LabelFrame(parent, text="  Metadata  ", padding="10")
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.prompt_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(self.prompt_tab, text="  ✨ Prompt  ")
        
        self.prompt_text = ModernStyle.create_styled_text(self.prompt_tab, wrap=tk.WORD)
        self.prompt_scrollbar = ttk.Scrollbar(self.prompt_tab, orient=tk.VERTICAL, command=self.prompt_text.yview)
        self.prompt_text.config(yscrollcommand=self.prompt_scrollbar.set)
        self.prompt_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.prompt_text.pack(fill=tk.BOTH, expand=True)
        
        self.params_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(self.params_tab, text="  ⚙ Params  ")
        
        self.params_text = ModernStyle.create_styled_text(self.params_tab, wrap=tk.WORD)
        self.params_scrollbar = ttk.Scrollbar(self.params_tab, orient=tk.VERTICAL, command=self.params_text.yview)
        self.params_text.config(yscrollcommand=self.params_scrollbar.set)
        self.params_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.params_text.pack(fill=tk.BOTH, expand=True)
        
        self.workflow_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(self.workflow_tab, text="  🔧 Workflow  ")
        
        self.workflow_text = ModernStyle.create_styled_text(self.workflow_tab, wrap=tk.WORD)
        self.workflow_scrollbar = ttk.Scrollbar(self.workflow_tab, orient=tk.VERTICAL, command=self.workflow_text.yview)
        self.workflow_text.config(yscrollcommand=self.workflow_scrollbar.set)
        self.workflow_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.workflow_text.pack(fill=tk.BOTH, expand=True)
        
        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.copy_button = ttk.Button(
            self.button_frame, 
            text="📋 Copy", 
            command=self.copy_current_tab, 
            width=10
        )
        self.copy_button.pack(side=tk.LEFT, padx=3)
        
        self.export_json_button = ttk.Button(
            self.button_frame, 
            text="📄 Export JSON", 
            command=self.export_json, 
            width=12
        )
        self.export_json_button.pack(side=tk.LEFT, padx=3)
        
        self.export_txt_button = ttk.Button(
            self.button_frame, 
            text="📝 Export TXT", 
            command=self.export_txt, 
            width=12
        )
        self.export_txt_button.pack(side=tk.LEFT, padx=3)
        
        self._configure_tags()
    
    def _configure_tags(self):
        header_font = ('Segoe UI', 11, 'bold')
        label_font = ('Segoe UI', 10, 'bold')
        
        self.prompt_text.tag_configure('header', font=header_font, foreground=ModernStyle.COLORS['accent_primary'])
        self.prompt_text.tag_configure('label', font=label_font, foreground=ModernStyle.COLORS['accent_secondary'])
        self.prompt_text.tag_configure('negative', foreground=ModernStyle.COLORS['accent_error'])
        
        self.params_text.tag_configure('label', font=label_font, foreground=ModernStyle.COLORS['accent_secondary'])
        self.params_text.tag_configure('value', foreground=ModernStyle.COLORS['text_primary'])
        
        self.workflow_text.tag_configure('json_key', foreground=ModernStyle.COLORS['accent_secondary'])
        self.workflow_text.tag_configure('json_string', foreground=ModernStyle.COLORS['accent_success'])
        self.workflow_text.tag_configure('json_number', foreground=ModernStyle.COLORS['accent_warning'])
    
    def update(self, metadata, file_path=""):
        self.metadata = metadata
        self.file_path = file_path
        
        self.prompt_text.config(state=tk.NORMAL)
        self.prompt_text.delete(1.0, tk.END)
        
        self.prompt_text.insert(tk.END, metadata['prompt'] or "No prompt data")
        
        if metadata['negative_prompt']:
            self.prompt_text.insert(tk.END, "\n\n")
            self.prompt_text.insert(tk.END, "Negative Prompt:\n", 'label')
            self.prompt_text.insert(tk.END, metadata['negative_prompt'])
        self.prompt_text.config(state=tk.DISABLED)
        
        self.params_text.config(state=tk.NORMAL)
        self.params_text.delete(1.0, tk.END)
        
        params_data = [
            ("Seed", metadata['seed']),
            ("Steps", metadata['steps']),
            ("CFG", metadata['cfg']),
            ("Sampler", metadata['sampler_name']),
            ("Model", metadata['model'])
        ]
        
        for label, value in params_data:
            self.params_text.insert(tk.END, f"{label}:  ", 'label')
            self.params_text.insert(tk.END, f"{value}\n", 'value')
        
        self.params_text.config(state=tk.DISABLED)
        
        self.workflow_text.config(state=tk.NORMAL)
        self.workflow_text.delete(1.0, tk.END)
        
        if metadata['workflow']:
            try:
                workflow_json = json.loads(metadata['workflow'])
                formatted_json = json.dumps(workflow_json, ensure_ascii=False, indent=2)
                self.workflow_text.insert(tk.END, formatted_json)
            except:
                self.workflow_text.insert(tk.END, metadata['workflow'])
        else:
            self.workflow_text.insert(tk.END, "No workflow data")
        
        self.workflow_text.config(state=tk.DISABLED)
    
    def copy_current_tab(self):
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab == 0:
            if self.metadata['prompt']:
                prompt = self.metadata['prompt']
                if self.metadata['negative_prompt']:
                    prompt += f"\n\nNegative prompt: {self.metadata['negative_prompt']}"
                self.clipboard_func(prompt)
                self.status_func("Prompt copied to clipboard")
            else:
                self.status_func("No prompt to copy")
        elif current_tab == 1:
            params_info = [
                f"Seed: {self.metadata['seed']}",
                f"Steps: {self.metadata['steps']}",
                f"CFG: {self.metadata['cfg']}",
                f"Sampler: {self.metadata['sampler_name']}",
                f"Model: {self.metadata['model']}"
            ]
            params_text = '\n'.join(params_info)
            if params_text:
                self.clipboard_func(params_text)
                self.status_func("Params copied to clipboard")
            else:
                self.status_func("No params to copy")
        elif current_tab == 2:
            if self.metadata['workflow']:
                self.clipboard_func(self.metadata['workflow'])
                self.status_func("Workflow copied to clipboard")
            else:
                self.status_func("No workflow to copy")
    
    def export_json(self):
        if not self.metadata:
            messagebox.showwarning("Warning", "No data to export")
            return
        
        initialfile = ""
        if self.file_path:
            filename = os.path.basename(self.file_path)
            initialfile = os.path.splitext(filename)[0]
        
        file_path = filedialog.asksaveasfilename(
            title="Export as JSON",
            defaultextension=".json",
            initialfile=initialfile,
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.metadata, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Success", f"Data exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error exporting file: {str(e)}")
    
    def export_txt(self):
        if not self.metadata:
            messagebox.showwarning("Warning", "No data to export")
            return
        
        initialfile = ""
        if self.file_path:
            filename = os.path.basename(self.file_path)
            initialfile = os.path.splitext(filename)[0]
        
        file_path = filedialog.asksaveasfilename(
            title="Export as TXT",
            defaultextension=".txt",
            initialfile=initialfile,
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("=" * 50 + "\n")
                    f.write("    ComfyUI Image Metadata Export Report\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"Prompt:\n{self.metadata['prompt']}\n\n")
                    if self.metadata['negative_prompt']:
                        f.write(f"Negative Prompt:\n{self.metadata['negative_prompt']}\n\n")
                    f.write("Generation Parameters:\n")
                    f.write(f"  + Seed: {self.metadata['seed']}\n")
                    f.write(f"  + Steps: {self.metadata['steps']}\n")
                    f.write(f"  + CFG: {self.metadata['cfg']}\n")
                    f.write(f"  + Sampler: {self.metadata['sampler_name']}\n")
                    f.write(f"  - Model: {self.metadata['model']}\n\n")
                    if self.metadata['workflow']:
                        f.write(f"Workflow:\n{self.metadata['workflow']}")
                messagebox.showinfo("Success", f"Data exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error exporting file: {str(e)}")
