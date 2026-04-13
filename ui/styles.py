import tkinter as tk
from tkinter import ttk


class ModernStyle:
    COLORS = {
        'bg_primary': '#0f172a',
        'bg_secondary': '#1e293b',
        'bg_tertiary': '#334155',
        'bg_accent': '#475569',
        'text_primary': '#f1f5f9',
        'text_secondary': '#cbd5e1',
        'text_muted': '#94a3b8',
        'accent_primary': '#10b981',
        'accent_secondary': '#14b8a6',
        'accent_success': '#22c55e',
        'accent_warning': '#f59e0b',
        'accent_error': '#ef4444',
        'border': '#334155',
        'hover': '#3b82f6',
        'selected': '#10b981',
        'canvas_bg': '#0f172a',
        'placeholder_text': '#64748b',
    }

    FONTS = {
        'title': ('Segoe UI', 11, 'bold'),
        'body': ('Segoe UI', 10),
        'small': ('Segoe UI', 9),
        'code': ('Cascadia Code', 10, 'normal'),
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

        root.option_add('*BorderWidth', 0)
        root.option_add('*highlightThickness', 0)
        root.option_add('*highlightBackground', cls.COLORS['bg_primary'])

        style.theme_use('clam')

        style.configure('.',
            background=cls.COLORS['bg_primary'],
            foreground=cls.COLORS['text_primary'],
            bordercolor=cls.COLORS['bg_primary'],
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
            bordercolor=cls.COLORS['bg_primary'],
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
            focuscolor='none',
            font=cls.FONTS['button'],
            padding=(15, 8),
            relief='flat',
            anchor='center'
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
            font=cls.FONTS['button'],
            padding=(15, 8)
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
            borderwidth=0,
            tabmargins=[2, 8, 0, 0]
        )
        style.configure('TNotebook.Tab',
            background=cls.COLORS['bg_secondary'],
            foreground=cls.COLORS['text_muted'],
            padding=[24, 12],
            font=cls.FONTS['body']
        )
        style.map('TNotebook.Tab',
            background=[
                ('selected', cls.COLORS['accent_primary']),
                ('active', cls.COLORS['bg_tertiary'])
            ],
            foreground=[
                ('selected', cls.COLORS['bg_primary']),
                ('active', cls.COLORS['text_primary'])
            ],
            padding=[
                ('selected', [24, 12]),
                ('!selected', [20, 10])
            ]
        )
        try:
            style.layout('TNotebook.Tab', [
                ('Notebook.tab', {
                    'sticky': 'nswe',
                    'children': [
                        ('Notebook.padding', {
                            'side': 'top',
                            'sticky': 'nswe',
                            'children': [
                                ('Notebook.label', {'side': 'top', 'sticky': ''})
                            ]
                        })
                    ]
                })
            ])
        except Exception:
            pass

        style.configure('TScrollbar',
            background='#1b2742',
            troughcolor='#0f172a',
            borderwidth=0,
            arrowcolor='#1b2742',
            gripcount=0,
            width=8,
            relief='flat'
        )
        style.map('TScrollbar',
            background=[
                ('active', '#10b981'),
                ('!active', '#1b2742')
            ],
            relief=[
                ('active', 'flat'),
                ('!active', 'flat')
            ]
        )

        try:
            style.layout('TScrollbar', [
                ('Vertical.Scrollbar.trough', {
                    'sticky': 'ns',
                    'children': [
                        ('Vertical.Scrollbar.thumb', {'unit': '1', 'sticky': 'ns'})
                    ]
                })
            ])
        except Exception:
            pass

        style.configure('Treeview',
            background=cls.COLORS['bg_secondary'],
            foreground=cls.COLORS['text_primary'],
            fieldbackground=cls.COLORS['bg_secondary'],
            bordercolor=cls.COLORS['border'],
            font=cls.FONTS['body'],
            rowheight=28
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
            troughcolor=cls.COLORS['bg_secondary'],
            thickness=8
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
            insertbackground=cls.COLORS['accent_primary'],
            selectbackground=cls.COLORS['accent_primary'],
            selectforeground=cls.COLORS['bg_primary'],
            inactiveselectbackground=cls.COLORS['bg_tertiary'],
            relief='flat',
            borderwidth=0,
            padx=cls.PADDING['medium'],
            pady=cls.PADDING['medium'],
            font=font,
            highlightthickness=0,
            spacing1=4,
            spacing2=4,
            tabstyle='wordprocessor'
        )
        return text

    @classmethod
    def create_styled_listbox(cls, parent, height=30, selectmode=tk.SINGLE):
        listbox = tk.Listbox(
            parent,
            height=height,
            selectmode=selectmode,
            exportselection=0,
            bg=cls.COLORS['bg_secondary'],
            fg=cls.COLORS['text_primary'],
            selectbackground=cls.COLORS['accent_primary'],
            selectforeground=cls.COLORS['bg_primary'],
            relief='flat',
            borderwidth=0,
            highlightthickness=0,
            font=cls.FONTS['body'],
            activestyle='none',
            selectborderwidth=0,
            cursor='hand2'
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

