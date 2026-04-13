import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os

from .styles import ModernStyle


class ResultPanel:
    def __init__(self, parent, clipboard_func, status_func, on_file_added=None):
        self.clipboard_func = clipboard_func
        self.status_func = status_func
        self.on_file_added = on_file_added
        self.metadata = {}
        self.file_path = ""
        self.is_edit_mode = False
        self.original_character_text = ""
        
        self.frame = ttk.LabelFrame(parent, text="  Metadata  ", padding="10")
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
        self.prompt_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(self.prompt_tab, text="Prompt")

        self.prompt_text = ModernStyle.create_styled_text(self.prompt_tab, wrap=tk.WORD)
        self.prompt_scrollbar = ttk.Scrollbar(self.prompt_tab, orient=tk.VERTICAL, command=self.prompt_text.yview, style='TScrollbar')
        self.prompt_text.config(yscrollcommand=self.prompt_scrollbar.set)
        self.prompt_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.prompt_text.pack(fill=tk.BOTH, expand=True)

        self.params_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(self.params_tab, text="Params")

        self.params_text = ModernStyle.create_styled_text(self.params_tab, wrap=tk.WORD)
        self.params_scrollbar = ttk.Scrollbar(self.params_tab, orient=tk.VERTICAL, command=self.params_text.yview, style='TScrollbar')
        self.params_text.config(yscrollcommand=self.params_scrollbar.set)
        self.params_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.params_text.pack(fill=tk.BOTH, expand=True)

        self.workflow_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(self.workflow_tab, text="Workflow")

        self.workflow_text = ModernStyle.create_styled_text(self.workflow_tab, wrap=tk.WORD)
        self.workflow_scrollbar = ttk.Scrollbar(self.workflow_tab, orient=tk.VERTICAL, command=self.workflow_text.yview, style='TScrollbar')
        self.workflow_text.config(yscrollcommand=self.workflow_scrollbar.set)
        self.workflow_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.workflow_text.pack(fill=tk.BOTH, expand=True)

        self.character_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(self.character_tab, text="Character")

        self.character_frame = tk.Frame(self.character_tab, bg=ModernStyle.COLORS['bg_secondary'], padx=2, pady=2)
        self.character_frame.pack(fill=tk.BOTH, expand=True)

        self.character_text = ModernStyle.create_styled_text(self.character_frame, wrap=tk.WORD)
        self.character_scrollbar = ttk.Scrollbar(self.character_frame, orient=tk.VERTICAL, command=self.character_text.yview, style='TScrollbar')
        self.character_text.config(yscrollcommand=self.character_scrollbar.set)
        self.character_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.character_text.pack(fill=tk.BOTH, expand=True)
        
        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(20, 10))
        
        self.copy_button = ttk.Button(
            self.button_frame,
            text="Copy",
            command=self.on_copy_click,
            width=10
        )
        self.copy_button.pack(side=tk.LEFT, padx=3)

        self.edit_button = tk.Button(`n            self.button_frame,`n            text="Edit",`n            command=self.toggle_edit_mode,`n            width=12,`n            height=2,
            bg=ModernStyle.COLORS['bg_tertiary'],
            fg=ModernStyle.COLORS['text_primary'],
            relief=tk.FLAT,
            cursor='hand2',
            font=ModernStyle.FONTS['button'],
            activebackground=ModernStyle.COLORS['accent_primary'],
            activeforeground=ModernStyle.COLORS['bg_primary']
        )
        self.edit_button.pack(side=tk.LEFT, padx=3)

        self.export_json_button = ttk.Button(
            self.button_frame,
            text="JSON",
            command=self.on_export_json_click,
            width=10
        )
        self.export_json_button.pack(side=tk.LEFT, padx=3)

        self.export_txt_button = ttk.Button(
            self.button_frame,
            text="TXT",
            command=self.on_export_txt_click,
            width=10
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
        
        self.character_text.tag_configure('header', font=header_font, foreground=ModernStyle.COLORS['accent_primary'])
        self.character_text.tag_configure('label', font=label_font, foreground=ModernStyle.COLORS['accent_secondary'])
        self.character_text.tag_configure('value', foreground=ModernStyle.COLORS['text_primary'])
    
    def clear(self):
        self.metadata = {}
        self.file_path = ""
        
        self.prompt_text.config(state=tk.NORMAL)
        self.prompt_text.delete(1.0, tk.END)
        self.prompt_text.config(state=tk.DISABLED)
        
        self.params_text.config(state=tk.NORMAL)
        self.params_text.delete(1.0, tk.END)
        self.params_text.config(state=tk.DISABLED)
        
        self.workflow_text.config(state=tk.NORMAL)
        self.workflow_text.delete(1.0, tk.END)
        self.workflow_text.config(state=tk.DISABLED)
        
        self.character_text.config(state=tk.NORMAL)
        self.character_text.delete(1.0, tk.END)
        self.character_text.config(state=tk.DISABLED)
    
    def has_unsaved_changes(self):
        if not self.is_edit_mode:
            return False
        current_text = self.character_text.get(1.0, tk.END).strip()
        return current_text != self.original_character_text
    
    def prompt_save_if_needed(self):
        if not self.has_unsaved_changes():
            if self.is_edit_mode:
                self.cancel_edit_mode()
            return True
        
        result = messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Do you want to save them?")
        
        if result is None:
            return False
        elif result:
            self.save_character_changes()
            self.exit_edit_mode_ui()
            return True
        else:
            self.cancel_edit_mode()
            return True
    
    def on_copy_click(self):
        if not self.prompt_save_if_needed():
            return
        self.copy_current_tab()
    
    def on_export_json_click(self):
        if not self.prompt_save_if_needed():
            return
        self.export_json()
    
    def on_export_txt_click(self):
        if not self.prompt_save_if_needed():
            return
        self.export_txt()
    
    def on_tab_changed(self, event):
        if self.is_edit_mode:
            current_tab = self.notebook.index(self.notebook.select())
            character_tab_index = self.notebook.index(self.character_tab)
            
            if current_tab != character_tab_index:
                result = messagebox.askyesnocancel("Edit Mode", "You are editing character info. Do you want to save changes?")
                
                if result is None:
                    self.notebook.select(self.character_tab)
                elif result:
                    if self.save_character_changes():
                        pass
                    else:
                        self.notebook.select(self.character_tab)
                else:
                    self.cancel_edit_mode()
    
    def set_edit_mode_ui(self, editing):
        if editing:
            self.notebook.select(self.character_tab)
            self.character_frame.config(bg=ModernStyle.COLORS['accent_primary'], padx=3, pady=3)
            self.notebook.tab(self.character_tab, text="Character *")
            self.edit_button.config(
                text="Save",
                bg=ModernStyle.COLORS['accent_primary'],
                fg=ModernStyle.COLORS['bg_primary'],
                relief=tk.FLAT
            )
        else:
            self.character_frame.config(bg=ModernStyle.COLORS['bg_secondary'], padx=2, pady=2)
            self.notebook.tab(self.character_tab, text="Character")
            self.edit_button.config(
                text="Edit",
                bg=ModernStyle.COLORS['bg_tertiary'],
                fg=ModernStyle.COLORS['text_primary'],
                relief=tk.FLAT
            )
    
    def cancel_edit_mode(self):
        self.is_edit_mode = False
        self.character_text.config(state=tk.NORMAL)
        self.character_text.delete(1.0, tk.END)
        self.character_text.insert(tk.END, self.original_character_text)
        self.character_text.config(state=tk.DISABLED)
        self.set_edit_mode_ui(False)
    
    def exit_edit_mode_ui(self):
        self.is_edit_mode = False
        self.character_text.config(state=tk.DISABLED)
        self.set_edit_mode_ui(False)
    
    def update(self, metadata, file_path=""):
        if self.is_edit_mode and self.has_unsaved_changes():
            result = messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Do you want to save them before loading new image?")
            if result is None:
                return
            elif result:
                self.save_character_changes()
        
        self.metadata = metadata
        self.file_path = file_path
        self.is_edit_mode = False
        self.set_edit_mode_ui(False)
        
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
        
        self.character_text.config(state=tk.NORMAL)
        self.character_text.delete(1.0, tk.END)
        
        chara_raw = metadata.get('chara_raw', {})
        
        if chara_raw:
            field_label_map = {
                'name': 'Name',
                'description': 'Description',
                'personality': 'Personality',
                'scenario': 'Scenario',
                'first_mes': 'First Message',
                'mes_example': 'Message Example',
                'creator_notes': 'Creator Notes',
                'tags': 'Tags',
                'creator': 'Creator',
                'character_version': 'Version',
                'create_date': 'Create Date',
                'talkativeness': 'Talkativeness',
                'avatar': 'Avatar',
                'chat': 'Chat',
                'fav': 'Favorite',
                'declaration': 'Declaration',
            }
            
            data_only_keys = ['first_mes', 'creator_notes']
            
            for key, value in chara_raw.items():
                if key == 'data':
                    continue
                if key in data_only_keys:
                    continue
                if isinstance(value, list):
                    value = ', '.join(str(v) for v in value)
                if value:
                    label = field_label_map.get(key, key.replace('_', ' ').title())
                    self.character_text.insert(tk.END, f"{label}: {value}\n")
            
            if 'data' in chara_raw:
                data = chara_raw['data']
                if isinstance(data, dict):
                    if 'creator_notes' in data and data['creator_notes']:
                        self.character_text.insert(tk.END, f"Creator Notes: {data['creator_notes']}\n")
                    if 'first_mes' in data and data['first_mes']:
                        self.character_text.insert(tk.END, f"First Message: {data['first_mes']}\n")
        elif metadata['model'] == 'AI Chat Character' and 'AI Chat Character Info' in metadata['workflow']:
            lines = metadata['workflow'].split('\n')
            for line in lines[1:]:
                if line.strip():
                    if ': ' in line:
                        label, value = line.split(': ', 1)
                        if label != 'Character Books':
                            self.character_text.insert(tk.END, f"{label}: {value}\n")
        elif metadata.get('chara_workflow') and 'AI Chat Character Info' in metadata.get('chara_workflow', ''):
            lines = metadata['chara_workflow'].split('\n')
            for line in lines[1:]:
                if line.strip():
                    if ': ' in line:
                        label, value = line.split(': ', 1)
                        if label != 'Character Books':
                            self.character_text.insert(tk.END, f"{label}: {value}\n")
        else:
            self.character_text.insert(tk.END, "No character data")
        
        self.character_text.config(state=tk.DISABLED)
        self.original_character_text = self.character_text.get(1.0, tk.END).strip()
    
    def toggle_edit_mode(self):
        if not self.is_edit_mode:
            self.is_edit_mode = True
            self.original_character_text = self.character_text.get(1.0, tk.END).strip()
            self.character_text.config(state=tk.NORMAL)
            self.set_edit_mode_ui(True)
        else:
            current_text = self.character_text.get(1.0, tk.END).strip()
            if current_text != self.original_character_text:
                if self.save_character_changes():
                    self.exit_edit_mode_ui()
            else:
                self.exit_edit_mode_ui()
    
    def save_character_changes(self):
        if not self.file_path:
            messagebox.showerror("Error", "No file selected")
            return False
        
        try:
            from PIL import Image
            import json
            import base64
            import re
            import copy
            
            edited_text = self.character_text.get(1.0, tk.END).strip()
            
            field_pattern = re.compile(r'^([^:\n]+): (.*)$', re.MULTILINE)
            
            chara_info = {}
            matches = list(field_pattern.finditer(edited_text))
            
            for i, match in enumerate(matches):
                key = match.group(1).strip()
                first_line_value = match.group(2)
                
                if i + 1 < len(matches):
                    value_end = matches[i + 1].start()
                    value = edited_text[match.start():value_end]
                    value = value.split(': ', 1)[1].strip() if ': ' in value else first_line_value
                else:
                    remaining = edited_text[match.start():]
                    value = remaining.split(': ', 1)[1].strip() if ': ' in remaining else first_line_value
                
                chara_info[key] = value
            
            field_mapping = {
                'Name': 'name',
                'Description': 'description',
                'First Message': 'first_mes',
                'Scenario': 'scenario',
                'Personality': 'personality',
                'Create Date': 'create_date',
                'Creator Notes': 'creator_notes',
                'Message Example': 'mes_example',
                'Tags': 'tags',
                'Creator': 'creator',
                'Version': 'character_version',
                'Talkativeness': 'talkativeness',
                'Avatar': 'avatar',
                'Chat': 'chat',
                'Favorite': 'fav',
                'Declaration': 'declaration',
            }
            
            data_only_fields = ['Creator Notes', 'First Message']
            
            if self.metadata.get('chara_raw'):
                original_data = copy.deepcopy(self.metadata['chara_raw'])
            else:
                original_data = {
                    "name": "",
                    "description": "",
                    "first_mes": "",
                    "scenario": "",
                    "personality": "",
                    "create_date": "",
                    "data": {
                        "character_books": []
                    }
                }
            
            chara_data = {}
            
            for key, value in chara_info.items():
                if value and key not in data_only_fields:
                    original_key = field_mapping.get(key, key.lower().replace(' ', '_'))
                    chara_data[original_key] = value
            
            if 'data' in original_data:
                chara_data['data'] = copy.deepcopy(original_data['data'])
            else:
                chara_data['data'] = {"character_books": []}
            
            if 'character_books' not in chara_data['data']:
                chara_data['data']['character_books'] = []
            
            if 'Creator Notes' in chara_info:
                if chara_info['Creator Notes']:
                    chara_data['data']['creator_notes'] = chara_info['Creator Notes']
                elif 'creator_notes' in chara_data['data']:
                    del chara_data['data']['creator_notes']
            elif 'creator_notes' in chara_data['data']:
                del chara_data['data']['creator_notes']
            
            if 'First Message' in chara_info:
                if chara_info['First Message']:
                    chara_data['data']['first_mes'] = chara_info['First Message']
                elif 'first_mes' in chara_data['data']:
                    del chara_data['data']['first_mes']
            elif 'first_mes' in chara_data['data']:
                del chara_data['data']['first_mes']
            
            json_data = json.dumps(chara_data, ensure_ascii=False, indent=2)
            encoded_data = base64.b64encode(json_data.encode('utf-8')).decode('utf-8')
            
            from PIL.PngImagePlugin import PngInfo
            
            import os
            file_path = os.path.abspath(self.file_path)
            
            temp_path = file_path + ".tmp"
            
            with Image.open(file_path) as img:
                file_format = img.format.upper()
                
                if file_format == 'PNG':
                    pnginfo = PngInfo()
                    
                    for key, value in img.info.items():
                        if key == 'chara':
                            continue
                        if isinstance(value, str):
                            pnginfo.add_text(key, value)
                        elif isinstance(value, bytes):
                            pnginfo.add_text(key, value.decode('utf-8', errors='ignore'))
                    
                    pnginfo.add_text('chara', encoded_data)
                    
                    img.save(temp_path, format='PNG', pnginfo=pnginfo)
                
                elif file_format == 'WEBP':
                    exif_data = img.info.get('exif', b'')
                    
                    png_path = os.path.splitext(file_path)[0] + '.png'
                    temp_path = png_path + ".tmp"
                    
                    from PIL.PngImagePlugin import PngInfo
                    pnginfo = PngInfo()
                    
                    if exif_data:
                        import base64
                        exif_b64 = base64.b64encode(exif_data).decode('ascii')
                        pnginfo.add_text('exif_b64', exif_b64)
                    
                    pnginfo.add_text('chara', encoded_data)
                    
                    img.save(temp_path, format='PNG', pnginfo=pnginfo)
                    
                    file_path = png_path
                    
                    self._converted_path = png_path
                    
                    messagebox.showinfo("Format Conversion", "WebP format doesn't support character metadata.\n\nCharacter info has been saved to a new PNG file:\n" + os.path.basename(png_path))
                
                elif file_format in ('JPEG', 'JPG'):
                    exif_data = img.info.get('exif', b'')
                    
                    png_path = os.path.splitext(file_path)[0] + '.png'
                    temp_path = png_path + ".tmp"
                    
                    from PIL.PngImagePlugin import PngInfo
                    pnginfo = PngInfo()
                    
                    if exif_data:
                        import base64
                        exif_b64 = base64.b64encode(exif_data).decode('ascii')
                        pnginfo.add_text('exif_b64', exif_b64)
                    
                    pnginfo.add_text('chara', encoded_data)
                    
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    
                    img.save(temp_path, format='PNG', pnginfo=pnginfo)
                    
                    file_path = png_path
                    
                    self._converted_path = png_path
                    
                    messagebox.showinfo("Format Conversion", "JPEG format doesn't support character metadata.\n\nCharacter info has been saved to a new PNG file:\n" + os.path.basename(png_path))
                
                else:
                    img.save(temp_path, format=file_format)
            
            os.replace(temp_path, file_path)
            
            self.is_edit_mode = False
            self.set_edit_mode_ui(False)
            
            messagebox.showinfo("Success", "Character info saved to image")
            self.status_func("Character info saved")
            
            if hasattr(self, '_converted_path') and self._converted_path:
                if self.on_file_added:
                    self.on_file_added(self._converted_path)
                self._converted_path = None
            
            from parsers import MetadataParser
            parser = MetadataParser()
            with Image.open(file_path) as img:
                new_metadata = parser.parse(img)
                self.metadata = new_metadata
                self._update_display_only(new_metadata, file_path)
            
            return True
            
        except Exception as e:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            messagebox.showerror("Error", f"Error saving character info: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _update_display_only(self, metadata, file_path=""):
        self.metadata = metadata
        self.file_path = file_path
        
        self.character_text.config(state=tk.NORMAL)
        self.character_text.delete(1.0, tk.END)
        
        chara_raw = metadata.get('chara_raw', {})
        
        if chara_raw:
            field_label_map = {
                'name': 'Name',
                'description': 'Description',
                'personality': 'Personality',
                'scenario': 'Scenario',
                'first_mes': 'First Message',
                'mes_example': 'Message Example',
                'creator_notes': 'Creator Notes',
                'tags': 'Tags',
                'creator': 'Creator',
                'character_version': 'Version',
                'create_date': 'Create Date',
                'talkativeness': 'Talkativeness',
                'avatar': 'Avatar',
                'chat': 'Chat',
                'fav': 'Favorite',
                'declaration': 'Declaration',
            }
            
            data_only_keys = ['first_mes', 'creator_notes']
            
            for key, value in chara_raw.items():
                if key == 'data':
                    continue
                if key in data_only_keys:
                    continue
                if isinstance(value, list):
                    value = ', '.join(str(v) for v in value)
                if value:
                    label = field_label_map.get(key, key.replace('_', ' ').title())
                    self.character_text.insert(tk.END, f"{label}: {value}\n")
            
            if 'data' in chara_raw:
                data = chara_raw['data']
                if isinstance(data, dict):
                    if 'creator_notes' in data and data['creator_notes']:
                        self.character_text.insert(tk.END, f"Creator Notes: {data['creator_notes']}\n")
                    if 'first_mes' in data and data['first_mes']:
                        self.character_text.insert(tk.END, f"First Message: {data['first_mes']}\n")
        else:
            self.character_text.insert(tk.END, "No character data")
        
        self.character_text.config(state=tk.DISABLED)
        self.original_character_text = self.character_text.get(1.0, tk.END).strip()
    
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
        elif current_tab == 3:
            if self.metadata['model'] == 'AI Chat Character' and 'AI Chat Character Info' in self.metadata['workflow']:
                self.clipboard_func(self.metadata['workflow'])
                self.status_func("Character info copied to clipboard")
            else:
                self.status_func("No character info to copy")
    
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








