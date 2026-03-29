import tkinter as tk
from tkinter import ttk


class ModernStyle:
    COLORS = {
        'bg_primary': '#1e1e2e',
        'bg_secondary': '#2a2a3e',
        'bg_tertiary': '#363650',
        'bg_accent': '#45475a',
        'text_primary': '#cdd6f4',
        'text_secondary': '#a6adc8',
        'text_muted': '#6c7086',
        'accent_primary': '#89b4fa',
        'accent_secondary': '#74c7ec',
        'accent_success': '#a6e3a1',
        'accent_warning': '#f9e2af',
        'accent_error': '#f38ba8',
        'border': '#45475a',
        'hover': '#585b70',
        'selected': '#89b4fa',
        'canvas_bg': '#181825',
        'placeholder_text': '#6c7086',
    }
    
    FONTS = {
        'title': ('Segoe UI', 11, 'bold'),
        'body': ('Segoe UI', 10),
        'small': ('Segoe UI', 9),
        'code': ('Consolas', 10),
        'button': ('Segoe UI', 9, 'bold'),
    }
    
    PADDING = {
        'small': 5,
        'medium': 10,
        'large': 15,
    }
    
    @classmethod
    def configure_style(cls, root):
        style = ttk.Style()
        
        style.theme_use('clam')
        
        style.configure('.',
            background=cls.COLORS['bg_primary'],
            foreground=cls.COLORS['text_primary'],
            bordercolor=cls.COLORS['border'],
            troughcolor=cls.COLORS['bg_secondary'],
            focuscolor=cls.COLORS['accent_primary'],
            font=cls.FONTS['body']
        )
        
        style.configure('TFrame',
            background=cls.COLORS['bg_primary']
        )
        
        style.configure('TLabelframe',
            background=cls.COLORS['bg_primary'],
            foreground=cls.COLORS['text_primary'],
            bordercolor=cls.COLORS['border'],
            relief='flat'
        )
        style.configure('TLabelframe.Label',
            background=cls.COLORS['bg_primary'],
            foreground=cls.COLORS['accent_primary'],
            font=cls.FONTS['title']
        )
        
        style.configure('TLabel',
            background=cls.COLORS['bg_primary'],
            foreground=cls.COLORS['text_primary'],
            font=cls.FONTS['body']
        )
        
        style.configure('TButton',
            background=cls.COLORS['bg_tertiary'],
            foreground=cls.COLORS['text_primary'],
            bordercolor=cls.COLORS['border'],
            focuscolor=cls.COLORS['accent_primary'],
            font=cls.FONTS['button'],
            padding=(12, 6),
            relief='flat'
        )
        style.map('TButton',
            background=[
                ('active', cls.COLORS['hover']),
                ('pressed', cls.COLORS['accent_primary']),
                ('!active', cls.COLORS['bg_tertiary'])
            ],
            foreground=[
                ('active', cls.COLORS['text_primary']),
                ('pressed', cls.COLORS['bg_primary'])
            ]
        )
        
        style.configure('Accent.TButton',
            background=cls.COLORS['accent_primary'],
            foreground=cls.COLORS['bg_primary'],
            font=cls.FONTS['button']
        )
        style.map('Accent.TButton',
            background=[
                ('active', cls.COLORS['accent_secondary']),
                ('pressed', cls.COLORS['bg_primary'])
            ],
            foreground=[
                ('active', cls.COLORS['bg_primary']),
                ('pressed', cls.COLORS['accent_primary'])
            ]
        )
        
        style.configure('TNotebook',
            background=cls.COLORS['bg_primary'],
            bordercolor=cls.COLORS['border'],
            tabmargins=[0, 0, 0, 0]
        )
        style.configure('TNotebook.Tab',
            background=cls.COLORS['bg_secondary'],
            foreground=cls.COLORS['text_secondary'],
            padding=[16, 6],
            font=cls.FONTS['body']
        )
        style.map('TNotebook.Tab',
            background=[
                ('selected', cls.COLORS['accent_primary']),
                ('active', cls.COLORS['hover'])
            ],
            foreground=[
                ('selected', cls.COLORS['bg_primary']),
                ('active', cls.COLORS['text_primary'])
            ],
            padding=[
                ('selected', [20, 8]),
                ('!selected', [16, 6])
            ]
        )
        
        style.configure('TScrollbar',
            background=cls.COLORS['bg_secondary'],
            troughcolor=cls.COLORS['bg_primary'],
            bordercolor=cls.COLORS['border'],
            arrowcolor=cls.COLORS['text_secondary'],
            gripcount=0
        )
        style.map('TScrollbar',
            background=[
                ('active', cls.COLORS['hover']),
                ('!active', cls.COLORS['bg_secondary'])
            ]
        )
        
        style.configure('Treeview',
            background=cls.COLORS['bg_secondary'],
            foreground=cls.COLORS['text_primary'],
            fieldbackground=cls.COLORS['bg_secondary'],
            bordercolor=cls.COLORS['border'],
            font=cls.FONTS['body']
        )
        style.configure('Treeview.Heading',
            background=cls.COLORS['bg_tertiary'],
            foreground=cls.COLORS['text_primary'],
            font=cls.FONTS['button']
        )
        style.map('Treeview',
            background=[
                ('selected', cls.COLORS['accent_primary']),
                ('!selected', cls.COLORS['bg_secondary'])
            ],
            foreground=[
                ('selected', cls.COLORS['bg_primary']),
                ('!selected', cls.COLORS['text_primary'])
            ]
        )
        
        style.configure('Horizontal.TProgressbar',
            background=cls.COLORS['accent_primary'],
            troughcolor=cls.COLORS['bg_secondary']
        )
        
        return style
    
    @classmethod
    def create_rounded_button(cls, parent, text, command, width=None, style='TButton'):
        btn = ttk.Button(parent, text=text, command=command, style=style)
        if width:
            btn.configure(width=width)
        return btn
    
    @classmethod
    def create_styled_text(cls, parent, wrap=tk.WORD, state=tk.DISABLED, font=None):
        if font is None:
            font = cls.FONTS['code']
        
        text = tk.Text(
            parent,
            wrap=wrap,
            state=state,
            bg=cls.COLORS['bg_secondary'],
            fg=cls.COLORS['text_primary'],
            insertbackground=cls.COLORS['text_primary'],
            selectbackground=cls.COLORS['accent_primary'],
            selectforeground=cls.COLORS['bg_primary'],
            inactiveselectbackground=cls.COLORS['bg_tertiary'],
            relief='flat',
            borderwidth=0,
            padx=cls.PADDING['medium'],
            pady=cls.PADDING['small'],
            font=font,
            highlightthickness=1,
            highlightcolor=cls.COLORS['border'],
            highlightbackground=cls.COLORS['border']
        )
        return text
    
    @classmethod
    def create_styled_listbox(cls, parent, height=30):
        listbox = tk.Listbox(
            parent,
            height=height,
            exportselection=0,
            bg=cls.COLORS['bg_secondary'],
            fg=cls.COLORS['text_primary'],
            selectbackground=cls.COLORS['accent_primary'],
            selectforeground=cls.COLORS['bg_primary'],
            relief='flat',
            borderwidth=0,
            highlightthickness=1,
            highlightcolor=cls.COLORS['border'],
            highlightbackground=cls.COLORS['border'],
            font=cls.FONTS['body'],
            activestyle='none'
        )
        return listbox
    
    @classmethod
    def create_styled_canvas(cls, parent, **kwargs):
        canvas = tk.Canvas(
            parent,
            bg=cls.COLORS['canvas_bg'],
            highlightthickness=0,
            **kwargs
        )
        return canvas
