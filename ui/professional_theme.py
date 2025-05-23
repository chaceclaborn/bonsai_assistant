# File: ui/professional_theme.py

import tkinter as tk
from tkinter import ttk
import platform

class BonsaiTheme:
    """Professional green theme for Bonsai Assistant"""
    
    # Professional Green Color Palette
    COLORS = {
        'primary_green': '#2E7D32',      # Deep forest green
        'secondary_green': '#4CAF50',     # Medium green
        'accent_green': '#81C784',        # Light green
        'bg_main': '#F1F8E9',            # Very light green background
        'bg_card': '#FFFFFF',            # White cards
        'bg_accent': '#E8F5E8',          # Light green accent
        'text_primary': '#1B5E20',        # Dark green text
        'text_secondary': '#2E7D32',      # Medium green text
        'text_muted': '#757575',          # Gray text
        'success': '#4CAF50',            # Success green
        'warning': '#FF9800',            # Warning orange
        'error': '#F44336',              # Error red
        'info': '#2196F3',               # Info blue
    }
    
    # Typography
    FONTS = {
        'heading_large': ('Segoe UI', 16, 'bold'),
        'heading_medium': ('Segoe UI', 14, 'bold'),
        'heading_small': ('Segoe UI', 12, 'bold'),
        'body': ('Segoe UI', 10),
        'body_bold': ('Segoe UI', 10, 'bold'),
        'caption': ('Segoe UI', 9),
        'mono': ('Courier New', 9),
    }
    
    # Spacing
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 12,
        'lg': 16,
        'xl': 24,
        'xxl': 32,
    }

def setup_professional_style(root):
    """Setup professional styling for the entire application"""
    
    # Configure root window
    root.configure(bg=BonsaiTheme.COLORS['bg_main'])
    
    # Create custom style
    style = ttk.Style()
    
    # Use native theme as base
    if platform.system() == "Windows":
        style.theme_use('winnative')
    else:
        style.theme_use('clam')
    
    # Configure Notebook (tabs)
    style.configure('TNotebook', background=BonsaiTheme.COLORS['bg_main'])
    style.configure('TNotebook.Tab', 
                   background=BonsaiTheme.COLORS['accent_green'],
                   foreground=BonsaiTheme.COLORS['text_primary'],
                   padding=[16, 8],
                   font=BonsaiTheme.FONTS['body_bold'])
    
    style.map('TNotebook.Tab',
             background=[('selected', BonsaiTheme.COLORS['secondary_green']),
                        ('active', BonsaiTheme.COLORS['accent_green'])],
             foreground=[('selected', 'white'),
                        ('active', BonsaiTheme.COLORS['text_primary'])])
    
    # Configure Frames
    style.configure('TFrame', background=BonsaiTheme.COLORS['bg_main'])
    style.configure('Card.TFrame', 
                   background=BonsaiTheme.COLORS['bg_card'],
                   relief='solid',
                   borderwidth=1)
    
    # Configure LabelFrames
    style.configure('TLabelframe', 
                   background=BonsaiTheme.COLORS['bg_card'],
                   foreground=BonsaiTheme.COLORS['text_primary'],
                   borderwidth=2,
                   relief='solid')
    
    style.configure('TLabelframe.Label',
                   background=BonsaiTheme.COLORS['bg_card'],
                   foreground=BonsaiTheme.COLORS['primary_green'],
                   font=BonsaiTheme.FONTS['heading_small'])
    
    # Configure Labels
    style.configure('TLabel',
                   background=BonsaiTheme.COLORS['bg_main'],
                   foreground=BonsaiTheme.COLORS['text_primary'],
                   font=BonsaiTheme.FONTS['body'])
    
    style.configure('Heading.TLabel',
                   font=BonsaiTheme.FONTS['heading_medium'],
                   foreground=BonsaiTheme.COLORS['primary_green'])
    
    style.configure('Caption.TLabel',
                   font=BonsaiTheme.FONTS['caption'],
                   foreground=BonsaiTheme.COLORS['text_muted'])
    
    # Configure Buttons
    style.configure('TButton',
                   font=BonsaiTheme.FONTS['body_bold'],
                   padding=[16, 8])
    
    style.configure('Accent.TButton',
                   background=BonsaiTheme.COLORS['secondary_green'],
                   foreground='white',
                   font=BonsaiTheme.FONTS['body_bold'])
    
    style.map('Accent.TButton',
             background=[('active', BonsaiTheme.COLORS['primary_green']),
                        ('pressed', BonsaiTheme.COLORS['primary_green'])])
    
    # Configure Entry widgets
    style.configure('TEntry',
                   fieldbackground='white',
                   borderwidth=1,
                   relief='solid')
    
    # Configure Scales
    style.configure('TScale',
                   background=BonsaiTheme.COLORS['bg_main'],
                   troughcolor=BonsaiTheme.COLORS['accent_green'],
                   borderwidth=0)
    
    return style

def create_bonsai_ascii():
    """Return beautiful ASCII art of a juniper bonsai tree"""
    return '''
            🌿🌿🌲🌿🌿
           🌲🌿🌲🌿🌲🌿
          🌿🌲🌿🌲🌿🌲🌿
           🌲🌿🌲🌿🌲
         🌿🌲🌿    🌿🌲🌿
        🌲🌿         🌿🌲
           🌿🌲🌿🌲🌿
          🌲🌿🌲🌿🌲
            🌿🌲🌿
             |||
             |||
           ═══🪴═══
    '''

def create_bonsai_header(parent):
    """Create a compact, beautiful header with juniper bonsai art
    
    NOTE: To add a real bonsai image instead of ASCII art:
    1. Save a juniper bonsai image as 'assets/bonsai.png' (150x120 pixels recommended)
    2. Replace the ASCII art section with:
       try:
           from PIL import Image, ImageTk
           img = Image.open("assets/bonsai.png")
           img = img.resize((150, 120), Image.Resampling.LANCZOS)
           photo = ImageTk.PhotoImage(img)
           bonsai_label = ttk.Label(art_frame, image=photo)
           bonsai_label.image = photo  # Keep a reference
           bonsai_label.pack()
       except:
           # Fallback to ASCII art
           bonsai_label = ttk.Label(art_frame, text=create_bonsai_ascii(), ...)
    """
    header_frame = ttk.Frame(parent)
    header_frame.configure(style='Card.TFrame')
    
    # Compact container with reduced padding
    container = ttk.Frame(header_frame)
    container.pack(fill='x', padx=BonsaiTheme.SPACING['md'], pady=BonsaiTheme.SPACING['sm'])
    
    # Left side - Compact Bonsai ASCII art
    art_frame = ttk.Frame(container)
    art_frame.pack(side='left')
    
    bonsai_label = ttk.Label(art_frame, 
                            text=create_bonsai_ascii(),
                            font=('Courier New', 7),  # Smaller font
                            foreground=BonsaiTheme.COLORS['secondary_green'],
                            justify='center')
    bonsai_label.pack()
    
    # Middle - Title and info (more compact)
    info_frame = ttk.Frame(container)
    info_frame.pack(side='left', fill='x', expand=True, padx=(BonsaiTheme.SPACING['lg'], 0))
    
    # Compact title row
    title_row = ttk.Frame(info_frame)
    title_row.pack(fill='x')
    
    # Main title - smaller
    title_label = ttk.Label(title_row,
                           text="🌱 Bonsai Assistant Professional",
                           font=BonsaiTheme.FONTS['heading_small'],  # Smaller heading
                           foreground=BonsaiTheme.COLORS['primary_green'])
    title_label.pack(side='left')
    
    # Version on same line
    version_label = ttk.Label(title_row,
                             text="v2.0",
                             font=BonsaiTheme.FONTS['caption'],
                             foreground=BonsaiTheme.COLORS['text_muted'])
    version_label.pack(side='right')
    
    # Compact subtitle
    subtitle_label = ttk.Label(info_frame,
                              text="Intelligent Juniper Care & Automation System",
                              font=BonsaiTheme.FONTS['caption'],
                              foreground=BonsaiTheme.COLORS['text_secondary'])
    subtitle_label.pack(anchor='w')
    
    return header_frame

def create_professional_card(parent, title, content_frame_class=None):
    """Create a professional card container"""
    card = ttk.LabelFrame(parent, 
                         text=f"  {title}  ",
                         padding=BonsaiTheme.SPACING['lg'])
    
    if content_frame_class:
        content = content_frame_class(card)
        content.pack(fill='both', expand=True)
        return card, content
    
    return card

def create_status_card(parent, title, value, unit="", status="normal"):
    """Create a beautiful status card with value display"""
    card_frame = ttk.Frame(parent)
    card_frame.configure(style='Card.TFrame')
    
    # Main container
    container = ttk.Frame(card_frame)
    container.pack(fill='both', expand=True, padx=BonsaiTheme.SPACING['md'], 
                  pady=BonsaiTheme.SPACING['md'])
    
    # Title
    title_label = ttk.Label(container,
                           text=title,
                           font=BonsaiTheme.FONTS['caption'],
                           foreground=BonsaiTheme.COLORS['text_muted'])
    title_label.pack(anchor='w')
    
    # Value container
    value_frame = ttk.Frame(container)
    value_frame.pack(fill='x', pady=(BonsaiTheme.SPACING['xs'], 0))
    
    # Main value
    color = BonsaiTheme.COLORS['success']
    if status == "warning":
        color = BonsaiTheme.COLORS['warning']
    elif status == "error":
        color = BonsaiTheme.COLORS['error']
    elif status == "info":
        color = BonsaiTheme.COLORS['info']
    
    value_label = ttk.Label(value_frame,
                           text=str(value),
                           font=BonsaiTheme.FONTS['heading_medium'],
                           foreground=color)
    value_label.pack(side='left')
    
    # Unit
    if unit:
        unit_label = ttk.Label(value_frame,
                              text=f" {unit}",
                              font=BonsaiTheme.FONTS['body'],
                              foreground=BonsaiTheme.COLORS['text_muted'])
        unit_label.pack(side='left')
    
    return card_frame, value_label, title_label

def create_action_button(parent, text, command, style="normal"):
    """Create a professional action button"""
    button_style = 'TButton'
    if style == "primary":
        button_style = 'Accent.TButton'
    
    button = ttk.Button(parent,
                       text=text,
                       command=command,
                       style=button_style)
    return button

def create_info_panel(parent, title, items):
    """Create an information panel with key-value pairs"""
    panel = ttk.LabelFrame(parent, 
                          text=f"  {title}  ",
                          padding=BonsaiTheme.SPACING['md'])
    
    for i, (key, value) in enumerate(items.items()):
        row_frame = ttk.Frame(panel)
        row_frame.pack(fill='x', pady=BonsaiTheme.SPACING['xs'])
        
        # Key
        key_label = ttk.Label(row_frame,
                             text=f"{key}:",
                             font=BonsaiTheme.FONTS['body'],
                             foreground=BonsaiTheme.COLORS['text_secondary'])
        key_label.pack(side='left')
        
        # Value
        value_label = ttk.Label(row_frame,
                               text=str(value),
                               font=BonsaiTheme.FONTS['body_bold'],
                               foreground=BonsaiTheme.COLORS['text_primary'])
        value_label.pack(side='right')
    
    return panel

def add_separator(parent, orient='horizontal'):
    """Add a styled separator"""
    sep = ttk.Separator(parent, orient=orient)
    if orient == 'horizontal':
        sep.pack(fill='x', pady=BonsaiTheme.SPACING['md'])
    else:
        sep.pack(fill='y', padx=BonsaiTheme.SPACING['md'])
    return sep

def create_section_header(parent, text, level=1):
    """Create a section header with proper hierarchy"""
    if level == 1:
        font = BonsaiTheme.FONTS['heading_medium']
        color = BonsaiTheme.COLORS['primary_green']
    elif level == 2:
        font = BonsaiTheme.FONTS['heading_small']
        color = BonsaiTheme.COLORS['text_primary']
    else:
        font = BonsaiTheme.FONTS['body_bold']
        color = BonsaiTheme.COLORS['text_secondary']
    
    header = ttk.Label(parent,
                      text=text,
                      font=font,
                      foreground=color)
    header.pack(anchor='w', pady=(BonsaiTheme.SPACING['lg'], BonsaiTheme.SPACING['xs']))
    return header