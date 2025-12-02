"""
Configuration file for Smart Study Assistant
Contains constants, colors, and settings
"""

# UI Settings
WINDOW_TITLE = "🎓 Smart Study Assistant"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 950
MIN_WIDTH = 1100
MIN_HEIGHT = 750

# Fonts
FONT_FAMILY = "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 16, "bold")
FONT_HEADING = (FONT_FAMILY, 12, "bold")
FONT_BODY = (FONT_FAMILY, 10)
FONT_SMALL = (FONT_FAMILY, 9)
FONT_CODE = ("Consolas", 10)

# Colors - Light Mode
LIGHT_COLORS = {
    "bg": "#f8f9fa",
    "background": "#f8f9fa",  # Alias for bg
    "fg": "#212529",
    "text": "#212529",  # Alias for fg
    "card_bg": "#ffffff",
    "surface": "#ffffff",  # Alias for card_bg
    "card_border": "#e9ecef",
    "primary": "#4361ee",
    "primary_hover": "#3651d4",
    "secondary": "#6c757d",
    "success": "#06d6a0",
    "danger": "#ef476f",
    "warning": "#ffc300",
    "info": "#4cc9f0",
    "text_muted": "#6c757d",
    "text_secondary": "#6c757d",  # Alias for text_muted
    "border": "#dee2e6",
    "shadow": "#00000015",
    "accent": "#7209b7",
}

# Colors - Dark Mode
DARK_COLORS = {
    "bg": "#1a1a2e",
    "background": "#1a1a2e",  # Alias for bg
    "fg": "#eaeaea",
    "text": "#eaeaea",  # Alias for fg
    "card_bg": "#16213e",
    "surface": "#16213e",  # Alias for card_bg
    "card_border": "#0f3460",
    "primary": "#4361ee",
    "primary_hover": "#5a77ff",
    "secondary": "#495057",
    "success": "#06d6a0",
    "danger": "#ef476f",
    "warning": "#ffc300",
    "info": "#4cc9f0",
    "text_muted": "#adb5bd",
    "text_secondary": "#adb5bd",  # Alias for text_muted
    "border": "#343a40",
    "shadow": "#00000040",
    "accent": "#7209b7",
}

# Spacing
PADDING_SMALL = 5
PADDING_MEDIUM = 10
PADDING_LARGE = 15
PADDING_XL = 20

# Features
AUTOSAVE_INTERVAL = 3000  # milliseconds (3 seconds)
MAX_SEARCH_RESULTS = 50
TAG_COLORS = ["#4361ee", "#06d6a0", "#ef476f", "#ffc300", "#4cc9f0", "#7209b7"]

# Logging
LOG_FILE = "logs/app.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# Keyboard Shortcuts
SHORTCUTS = {
    "save": "<Control-s>",
    "new": "<Control-n>",
    "search": "<Control-f>",
    "quit": "<Control-q>",
    "refresh": "<F5>",
    "undo": "<Control-z>",
    "redo": "<Control-y>",
    "theme_toggle": "<Control-t>",
}

# XP System
XP_PER_NOTE = 10
XP_PER_QUIZ = 25
XP_PER_TIMER = 5
LEVELS = [0, 100, 250, 500, 1000, 2000, 5000, 10000]  # XP thresholds for levels
