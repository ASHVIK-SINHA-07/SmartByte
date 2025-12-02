"""
Modern UI Components for Smart Study Assistant
Provides reusable widgets with consistent styling
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import config
from logger import get_logger

logger = get_logger(__name__)


class CardFrame(ttk.Frame):
    """A modern card-style frame with padding and optional shadow effect"""

    def __init__(self, parent, title=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(padding=config.PADDING_LARGE)

        if title:
            title_label = ttk.Label(self, text=title, font=config.FONT_HEADING)
            title_label.pack(anchor="nw", pady=(0, config.PADDING_MEDIUM))


class RoundedButton(ttk.Button):
    """A styled button with modern appearance, hover effects, and icons"""

    def __init__(self, parent, text="", icon="", bootstyle="primary", **kwargs):
        # If icon provided, prepend it to text
        if icon:
            text = f"{icon} {text}"

        # Initialize with bootstyle
        super().__init__(parent, text=text, bootstyle=bootstyle, **kwargs)

        # Store original style for hover effects
        self.original_bootstyle = bootstyle

        # Bind hover events for visual feedback
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)

        # Configure cursor to show it's clickable
        self.config(cursor="hand2")

    def _on_hover(self, event):
        """Apply hover effect"""
        # ttkbootstrap handles most hover styling, but we can enhance it
        pass

    def _on_leave(self, event):
        """Remove hover effect"""
        pass


class SearchBox(ttk.Frame):
    """A search input with icon and live search capability"""

    def __init__(self, parent, placeholder="Search...", on_search=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_search = on_search
        self.placeholder = placeholder
        self.is_placeholder = True  # Set this BEFORE creating StringVar with trace
        self.search_var = tk.StringVar()

        # Search icon label
        search_icon = ttk.Label(self, text="🔍", font=config.FONT_BODY)
        search_icon.pack(side="left", padx=(0, 5))

        # Search entry
        self.entry = ttk.Entry(
            self, textvariable=self.search_var, font=config.FONT_BODY, width=30
        )
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.insert(0, placeholder)
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)

        # Add trace AFTER is_placeholder is set
        self.search_var.trace("w", self._on_text_change)

        # Clear button
        self.clear_btn = ttk.Button(
            self, text="✕", width=3, command=self.clear, bootstyle="secondary"
        )
        self.clear_btn.pack(side="left", padx=(5, 0))

    def _on_focus_in(self, event):
        if self.is_placeholder:
            self.entry.delete(0, tk.END)
            self.is_placeholder = False

    def _on_focus_out(self, event):
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.is_placeholder = True

    def _on_text_change(self, *args):
        if not self.is_placeholder and self.on_search:
            self.on_search(self.search_var.get())

    def clear(self):
        self.entry.delete(0, tk.END)
        self.is_placeholder = False
        if self.on_search:
            self.on_search("")

    def get(self):
        return "" if self.is_placeholder else self.search_var.get()


class TagWidget(ttk.Frame):
    """Widget for displaying and managing tags"""

    def __init__(self, parent, tags=None, on_tag_click=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_tag_click = on_tag_click
        self.tag_labels = []

        if tags:
            self.set_tags(tags)

    def set_tags(self, tags):
        """Display a list of tags"""
        # Clear existing tags
        for label in self.tag_labels:
            label.destroy()
        self.tag_labels.clear()

        # Create new tag labels
        for i, tag in enumerate(tags):
            if not tag.strip():
                continue

            tag_frame = ttk.Frame(self)
            tag_frame.pack(side="left", padx=2, pady=2)

            color_idx = i % len(config.TAG_COLORS)

            tag_label = tk.Label(
                tag_frame,
                text=f" {tag} ",
                font=config.FONT_SMALL,
                bg=config.TAG_COLORS[color_idx],
                fg="white",
                cursor="hand2",
                padx=8,
                pady=3,
            )
            tag_label.pack()

            if self.on_tag_click:
                tag_label.bind("<Button-1>", lambda e, t=tag: self.on_tag_click(t))

            self.tag_labels.append(tag_label)


class Modal(tk.Toplevel):
    """A modal dialog with consistent styling"""

    def __init__(self, parent, title="", width=500, height=400, **kwargs):
        super().__init__(parent, **kwargs)
        self.title(title)
        self.geometry(f"{width}x{height}")

        # Center on parent
        self.transient(parent)
        self.grab_set()

        # Center the window
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

        # Main container (also aliased as content for convenience)
        self.container = ttk.Frame(self, padding=config.PADDING_LARGE)
        self.container.pack(fill="both", expand=True)
        self.content = self.container  # Alias for easier access

        # Button bar container (created on demand)
        self._button_bar = None

        logger.info(f"Modal opened: {title}")

    def add_button(self, text, command, bootstyle="primary"):
        """Add a single button to the button bar"""
        if self._button_bar is None:
            self._button_bar = ttk.Frame(self.container)
            self._button_bar.pack(
                side="bottom", fill="x", pady=(config.PADDING_MEDIUM, 0)
            )

        btn = RoundedButton(
            self._button_bar, text=text, bootstyle=bootstyle, command=command
        )
        btn.pack(side="right", padx=(5, 0))
        return btn

    def add_button_bar(self, buttons):
        """Add a button bar at the bottom
        buttons: list of tuples (text, command, style_type)
        """
        if self._button_bar is None:
            self._button_bar = ttk.Frame(self.container)
            self._button_bar.pack(
                side="bottom", fill="x", pady=(config.PADDING_MEDIUM, 0)
            )

        for text, command, style_type in buttons:
            btn = RoundedButton(
                self._button_bar, text=text, bootstyle=style_type, command=command
            )
            btn.pack(side="right", padx=(5, 0))


class LoadingSpinner(ttk.Frame):
    """A simple loading indicator"""

    def __init__(self, parent, text="Loading...", **kwargs):
        super().__init__(parent, **kwargs)
        self.is_running = False

        self.label = ttk.Label(self, text=text, font=config.FONT_BODY)
        self.label.pack()

        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.current_char = 0

    def start(self):
        """Start the spinning animation"""
        self.is_running = True
        self._animate()

    def stop(self):
        """Stop the spinning animation"""
        self.is_running = False

    def _animate(self):
        if self.is_running:
            self.label.config(
                text=f"{self.spinner_chars[self.current_char]} Loading..."
            )
            self.current_char = (self.current_char + 1) % len(self.spinner_chars)
            self.after(100, self._animate)


class AutosaveIndicator(ttk.Frame):
    """Shows autosave status"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.label = ttk.Label(self, text="", font=config.FONT_SMALL, foreground="gray")
        self.label.pack()

    def show_saving(self):
        """Show 'Saving...' message"""
        self.label.config(text="💾 Saving...", foreground="gray")

    def show_saved(self):
        """Show 'Saved' message"""
        self.label.config(text="✓ Saved", foreground=config.LIGHT_COLORS["success"])
        self.after(2000, self._clear)

    def show_error(self, error_msg=""):
        """Show error message"""
        self.label.config(
            text=f"✗ Save failed {error_msg}", foreground=config.LIGHT_COLORS["danger"]
        )
        self.after(3000, self._clear)

    def _clear(self):
        """Clear the indicator"""
        self.label.config(text="")


class SummaryModal(Modal):
    """Enhanced modal for displaying AI summaries"""

    def __init__(self, parent, summary_text="", original_text="", **kwargs):
        # Extract title if provided, otherwise use default
        title = kwargs.pop("title", "✨ AI Summary")
        super().__init__(parent, title=title, width=700, height=500, **kwargs)

        self.summary_text = summary_text
        self.original_text = original_text

        # Summary text area
        self.text_area = scrolledtext.ScrolledText(
            self.container, wrap="word", font=config.FONT_BODY, height=20
        )
        self.text_area.pack(fill="both", expand=True, pady=(0, config.PADDING_MEDIUM))
        self.text_area.insert("1.0", summary_text)
        self.text_area.config(state="disabled")

        # Button bar
        self.add_button_bar(
            [
                ("Close", self.destroy, "secondary"),
                ("Copy", self._copy_to_clipboard, "info"),
                (
                    "Save to Note",
                    lambda: (
                        self._save_callback()
                        if hasattr(self, "_save_callback")
                        else None
                    ),
                    "success",
                ),
            ]
        )

    def _copy_to_clipboard(self):
        """Copy summary to clipboard"""
        text = self.text_area.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(text)
        logger.info("Summary copied to clipboard")

    def set_save_callback(self, callback):
        """Set callback for save button"""
        self._save_callback = callback
