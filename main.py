import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv
from PIL import Image, ImageTk

# Load environment variables from .env file
load_dotenv()

# Import configuration and utilities
import config
from logger import get_logger
from ui_components import (
    CardFrame,
    RoundedButton,
    SearchBox,
    TagWidget,
    Modal,
    LoadingSpinner,
    AutosaveIndicator,
    SummaryModal,
)
import ai_utils

# Setup logging
logger = get_logger(__name__)
logger.info("Smart Study Assistant starting...")

# Import ttkbootstrap for modern styling
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *

    TTKBOOTSTRAP_AVAILABLE = True
    logger.info("ttkbootstrap available")
except ImportError:
    from tkinter import ttk

    TTKBOOTSTRAP_AVAILABLE = False
    logger.warning("ttkbootstrap not installed. Install with: pip install ttkbootstrap")


def _chunk_text(text, max_chars=3000):
    paras = [p for p in text.split("\n\n") if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if len(cur) + len(p) + 2 < max_chars:
            cur = cur + "\n\n" + p if cur else p
        else:
            if cur:
                chunks.append(cur)
            cur = p
    if cur:
        chunks.append(cur)
    return chunks


# --- Gemini summarization support ---
try:
    import google.generativeai as genai

    GENAI_AVAILABLE = True
except Exception:
    genai = None
    GENAI_AVAILABLE = False

# GEMINI_API_KEY
GEMINI_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if GEMINI_KEY and GENAI_AVAILABLE:
    try:
        genai.configure(api_key=GEMINI_KEY)
        print(f"✓ Gemini API configured successfully")
    except Exception as e:
        print(f"✗ Gemini API configuration failed: {e}")


def gemini_summarize(text, max_sentences=6):
    """Summarize text using Gemini API with better error handling."""
    if not text or not text.strip():
        return "No text to summarize."

    if not GEMINI_KEY:
        return "Error: GEMINI_API_KEY not found in .env file"

    if not GENAI_AVAILABLE:
        return "Error: google-generativeai package not installed"

    # Try multiple model names in order of preference
    model_names = [
        "gemini-2.5-flash",
        "gemini-flash-latest",
        "gemini-pro-latest",
        "gemini-2.0-flash-exp",
    ]

    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)

            prompt = f"""Please summarize the following text concisely in {max_sentences} bullet points or less. 
Make it clear and informative. End with a brief TL;DR.

Text to summarize:
{text[:10000]}"""

            print(f"Trying model: {model_name}...")
            response = model.generate_content(prompt)

            # Better response handling
            if response and hasattr(response, "text") and response.text:
                summary = response.text.strip()
                print(f"✓ Success with {model_name} ({len(summary)} chars)")
                return summary
            elif response and hasattr(response, "candidates"):
                # Try to extract text from candidates
                for candidate in response.candidates:
                    if hasattr(candidate, "content") and hasattr(
                        candidate.content, "parts"
                    ):
                        for part in candidate.content.parts:
                            if hasattr(part, "text") and part.text:
                                summary = part.text.strip()
                                print(
                                    f"✓ Success with {model_name} ({len(summary)} chars)"
                                )
                                return summary

        except Exception as e:
            error_str = str(e)
            print(f"✗ {model_name} failed: {error_str}")
            # If this is a 404 model not found, try next model
            if "404" in error_str or "not found" in error_str.lower():
                continue
            # For other errors, return immediately
            return f"Summarization error: {error_str}"

    return "Error: All Gemini models failed. Please check your API key and internet connection."


from modules import storage, speech_notes, quizgen, reminders

storage.ensure_files()


class App(ttk.Window if TTKBOOTSTRAP_AVAILABLE else tk.Tk):
    def __init__(self):
        # Initialize with ttkbootstrap theme if available
        if TTKBOOTSTRAP_AVAILABLE:
            super().__init__(
                themename="cosmo"
            )  # Modern, clean theme with good contrast
        else:
            super().__init__()

        self.title("🎓 Smart Study Assistant")
        self.geometry("1300x920")
        self.resizable(True, True)

        # Set window icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.png')
            if os.path.exists(icon_path):
                icon_image = Image.open(icon_path)
                self.icon_photo = ImageTk.PhotoImage(icon_image)
                self.iconphoto(True, self.icon_photo)
                logger.info("Window icon set successfully")
        except Exception as e:
            logger.warning(f"Could not set window icon: {e}")

        # Set minimum window size
        self.minsize(1000, 700)

        self.timer_thread = None
        self.timer_stop_event = None
        self.current_timer_seconds = 0

        # Autosave and modification tracking
        self.autosave_timer = None
        self.is_modified = False
        
        # Track currently loaded note to prevent duplicates
        self.current_note_id = None  # ID of note currently in editor

        # Undo/Redo stacks for notes
        self.undo_stack = []
        self.redo_stack = []
        self.last_saved_state = ""

        # Theme tracking
        self.current_theme = "light"  # Start with light theme

        # status var used for lightweight toasts instead of blocking dialogs
        self.status_var = tk.StringVar(value="")

        logger.info("Creating widgets...")
        self.create_widgets()

        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()
        logger.info("Keyboard shortcuts registered")

        # Start autosave timer
        self.start_autosave_timer()
        logger.info("Autosave timer started")

        # Set up proper cleanup on window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initial refresh
        self.refresh_notes()
        self.refresh_reminders()
        self.refresh_dashboard()

    # ---------------- UI creation ----------------
    def create_widgets(self):
        # Configure custom styles for tabs
        style = ttk.Style()

        # Make tabs bigger and more modern
        style.configure("TNotebook", tabmargins=[12, 12, 12, 0])
        style.configure(
            "TNotebook.Tab", padding=[28, 14], font=("Segoe UI", 16, "bold")
        )

        # Active tab styling
        style.map(
            "TNotebook.Tab",
            padding=[("selected", [28, 17])],
            font=[("selected", ("Segoe UI", 16, "bold"))],
        )

        # Main container with padding
        main_container = ttk.Frame(self, padding=10)
        main_container.pack(fill="both", expand=True)

        # Add a stylish header bar
        header_bar = ttk.Frame(main_container, padding=(15, 10))
        header_bar.pack(fill="x", pady=(0, 15))

        # App title with logo
        title_frame = ttk.Frame(header_bar)
        title_frame.pack(side="left")

        # Load and display logo
        try:
            logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'logo.png')
            if os.path.exists(logo_path):
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((48, 48), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                logo_label = ttk.Label(title_frame, image=self.logo_photo)
                logo_label.pack(side="left", padx=(0, 12))
            else:
                # Fallback to emoji if logo not found
                ttk.Label(title_frame, text="🎓", font=("Segoe UI", 32)).pack(side="left", padx=(0, 8))
        except Exception as e:
            logger.warning(f"Could not load logo: {e}")
            ttk.Label(title_frame, text="🎓", font=("Segoe UI", 32)).pack(side="left", padx=(0, 8))

        ttk.Label(
            title_frame, text="Smart Study Assistant", font=("Segoe UI", 21, "bold")
        ).pack(side="left")

        ttk.Label(
            title_frame,
            text="  •  Your AI-powered learning companion",
            font=("Segoe UI", 15),
            foreground="gray",
        ).pack(side="left", padx=(10, 0))

        # Theme toggle button
        if TTKBOOTSTRAP_AVAILABLE:
            RoundedButton(
                header_bar,
                text="Theme",
                icon="🌓",
                command=self.toggle_theme,
                bootstyle="secondary",
            ).pack(side="right", padx=(8, 0))

        # Quick stats in header
        stats_frame = ttk.Frame(header_bar)
        stats_frame.pack(side="right")

        self.header_stats = ttk.Label(
            stats_frame, text="📊 Loading...", font=("Segoe UI", 14)
        )
        self.header_stats.pack()

        # Separator line
        ttk.Separator(main_container, orient="horizontal").pack(fill="x", pady=(0, 10))

        # Notebook with custom styling
        nb = ttk.Notebook(main_container)
        nb.pack(fill="both", expand=True)

        tab_notes = ttk.Frame(nb)
        nb.add(tab_notes, text=" 📝  Notes ")

        tab_rem = ttk.Frame(nb)
        nb.add(tab_rem, text=" ⏰  Reminders ")

        tab_quiz = ttk.Frame(nb)
        nb.add(tab_quiz, text=" 🎯  Quiz ")

        tab_timer = ttk.Frame(nb)
        nb.add(tab_timer, text=" ⏱️  Timer ")

        tab_dash = ttk.Frame(nb)
        nb.add(tab_dash, text="📊 Dashboard")

        self.build_notes_tab(tab_notes)
        self.build_reminders_tab(tab_rem)
        self.build_quiz_tab(tab_quiz)
        self.build_timer_tab(tab_timer)
        self.build_dashboard_tab(tab_dash)

    # ---------------- Notes Tab ----------------
    def build_notes_tab(self, parent):
        # Use a PanedWindow so the notes list is resizable by the user
        paned = ttk.Panedwindow(parent, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        left = ttk.Frame(paned, width=350)
        right = ttk.Frame(paned)
        paned.add(left, weight=1)
        paned.add(right, weight=3)

        # Header with count
        header_frame = ttk.Frame(left)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(header_frame, text="📝 Recent Notes", font=("Segoe UI", 17, "bold")).pack(
            side="left"
        )
        
        self.notes_count_label = ttk.Label(
            header_frame, text="(0)", font=("Segoe UI", 15), foreground="gray"
        )
        self.notes_count_label.pack(side="left", padx=(6, 0))

        # Search box with live filtering
        search_frame = ttk.Frame(left)
        search_frame.pack(fill="x", pady=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.filter_notes_live())
        
        self.search_entry = ttk.Entry(
            search_frame, 
            textvariable=self.search_var,
            font=("Segoe UI", 15)
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        
        # Placeholder handling
        self.search_placeholder = "🔍 Search notes..."
        self.search_entry.insert(0, self.search_placeholder)
        self.search_entry.config(foreground="gray")
        
        def on_search_focus_in(event):
            if self.search_entry.get() == self.search_placeholder:
                self.search_entry.delete(0, tk.END)
                self.search_entry.config(foreground="black" if self.current_theme == "light" else "white")
        
        def on_search_focus_out(event):
            if not self.search_entry.get():
                self.search_entry.insert(0, self.search_placeholder)
                self.search_entry.config(foreground="gray")
        
        self.search_entry.bind("<FocusIn>", on_search_focus_in)
        self.search_entry.bind("<FocusOut>", on_search_focus_out)
        
        # Search clear button
        clear_btn = ttk.Button(
            search_frame,
            text="✕",
            width=3,
            command=lambda: (self.search_var.set(""), self.search_entry.delete(0, tk.END), self.search_entry.insert(0, self.search_placeholder), self.search_entry.config(foreground="gray"))
        )
        clear_btn.pack(side="right", padx=(4, 0))

        # Simple Listbox instead of Treeview (more reliable)
        list_frame = ttk.Frame(left)
        list_frame.pack(fill="both", expand=True, pady=(0, 8))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.notes_listbox = tk.Listbox(
            list_frame,
            font=("Segoe UI", 15),
            height=20,
            selectmode="single",
            yscrollcommand=scrollbar.set,
            activestyle="dotbox"
        )
        self.notes_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.notes_listbox.yview)
        
        # Bind selection to handler
        self.notes_listbox.bind("<<ListboxSelect>>", self.on_note_select)
        
        # Store note objects for reference
        self.notes = []
        self.filtered_notes = []

        # Button panel with ttkbootstrap styled buttons
        btns = ttk.Frame(left)
        btns.pack(fill="x", pady=(0, 4))

        if TTKBOOTSTRAP_AVAILABLE:
            ttk.Button(
                btns, text="➕ New", command=self.new_note, bootstyle="success"
            ).pack(side="left", padx=2, expand=True, fill="x")
            ttk.Button(
                btns,
                text="🗑️ Delete",
                command=self.delete_selected_note,
                bootstyle="danger",
            ).pack(side="left", padx=2, expand=True, fill="x")
        else:
            ttk.Button(btns, text="➕ New", command=self.new_note).pack(
                side="left", padx=2, expand=True, fill="x"
            )
            ttk.Button(btns, text="🗑️ Delete", command=self.delete_selected_note).pack(
                side="left", padx=2, expand=True, fill="x"
            )

        btns2 = ttk.Frame(left)
        btns2.pack(fill="x", pady=(0, 4))

        if TTKBOOTSTRAP_AVAILABLE:
            ttk.Button(
                btns2,
                text="⏰ Remind",
                command=self.remind_for_selected_note,
                bootstyle="info",
            ).pack(side="left", padx=2, expand=True, fill="x")
            ttk.Button(
                btns2,
                text="✨ Summarize",
                command=self.summarize_selected,
                bootstyle="primary",
            ).pack(side="left", padx=2, expand=True, fill="x")
        else:
            ttk.Button(
                btns2, text="⏰ Remind", command=self.remind_for_selected_note
            ).pack(side="left", padx=2, expand=True, fill="x")
            ttk.Button(
                btns2, text="✨ Summarize", command=self.summarize_selected
            ).pack(side="left", padx=2, expand=True, fill="x")
        
        # Refresh button
        btns3 = ttk.Frame(left)
        btns3.pack(fill="x", pady=(0, 4))
        ttk.Button(
            btns3,
            text="🔄 Refresh List",
            command=self.refresh_notes
        ).pack(fill="x", padx=2)

        # Right: editor
        editor_frame = ttk.Frame(right, padding=10)
        editor_frame.pack(fill="both", expand=True)

        # Title section
        ttk.Label(editor_frame, text="✏️ Title", font=("Segoe UI", 16, "bold")).pack(
            anchor="nw", pady=(0, 5)
        )
        self.entry_title = ttk.Entry(editor_frame, font=("Segoe UI", 16))
        self.entry_title.pack(fill="x", pady=(0, 10))

        # Content section
        content_header = ttk.Frame(editor_frame)
        content_header.pack(fill="x", pady=(0, 5))

        ttk.Label(
            content_header, text="📄 Content", font=("Segoe UI", 16, "bold")
        ).pack(side="left")

        # Autosave indicator
        self.autosave_indicator = AutosaveIndicator(content_header)
        self.autosave_indicator.pack(side="right", padx=(12, 0))

        self.txt_content = scrolledtext.ScrolledText(
            editor_frame, height=18, font=("Segoe UI", 15), wrap="word"
        )
        self.txt_content.pack(fill="both", expand=True, pady=(0, 10))

        # Tags section
        ttk.Label(
            editor_frame, text="🏷️ Tags (comma-separated)", font=("Segoe UI", 16, "bold")
        ).pack(anchor="nw", pady=(0, 5))
        self.entry_tags = ttk.Entry(editor_frame, font=("Segoe UI", 15))
        self.entry_tags.pack(fill="x", pady=(0, 10))

        # NOW bind text changes to mark as modified (after all widgets are created)
        self.txt_content.bind("<<Modified>>", self._on_text_modified)
        self.entry_title.bind("<KeyRelease>", lambda e: self.mark_modified())
        self.entry_tags.bind("<KeyRelease>", lambda e: self.mark_modified())

        # Action buttons
        action_frame = ttk.Frame(editor_frame)
        action_frame.pack(fill="x", pady=(0, 4))

        # First row of buttons
        action_row1 = ttk.Frame(action_frame)
        action_row1.pack(fill="x", pady=(0, 4))

        if TTKBOOTSTRAP_AVAILABLE:
            RoundedButton(
                action_row1,
                text="Save Note",
                icon="💾",
                command=self.save_note,
                bootstyle="success",
            ).pack(side="left", padx=(0, 4))
            RoundedButton(
                action_row1,
                text="Flashcards",
                icon="🎴",
                command=self.generate_flashcards,
                bootstyle="info-outline",
            ).pack(side="left", padx=(0, 4))
            RoundedButton(
                action_row1,
                text="Rewrite Text",
                icon="✍️",
                command=self.show_rewrite_menu,
                bootstyle="warning-outline",
            ).pack(side="left", padx=(0, 4))
            RoundedButton(
                action_row1,
                text="Export PDF",
                icon="📄",
                command=self.export_note_to_pdf,
                bootstyle="secondary",
            ).pack(side="left")
        else:
            ttk.Button(action_row1, text="💾 Save Note", command=self.save_note).pack(
                side="left", padx=(0, 4)
            )
            ttk.Button(
                action_frame, text="🎴 Flashcards", command=self.generate_flashcards
            ).pack(side="left", padx=(0, 4))
            ttk.Button(
                action_frame, text="✍️ Rewrite Text", command=self.show_rewrite_menu
            ).pack(side="left")

    def refresh_notes(self):
        """Populate the notes listbox with all available notes.
        Simple and reliable - just clears and rebuilds the list.
        """
        try:
            logger.info("Refreshing notes list...")
            
            # Clear the listbox completely
            self.notes_listbox.delete(0, tk.END)
            
            # Load notes from storage
            self.notes = storage.list_notes(limit=200)
            self.filtered_notes = self.notes.copy()  # Keep a copy for filtering
            
            logger.info(f"Loaded {len(self.notes)} notes from storage")
            
            # Update count label
            if hasattr(self, 'notes_count_label'):
                self.notes_count_label.config(text=f"({len(self.notes)})")
            
            if not self.notes:
                logger.warning("No notes found in storage")
                self.notes_listbox.insert(tk.END, "📭 No notes yet - click New to create one!")
                return
            
            # Add each note to the listbox with a formatted display
            for note in self.notes:
                try:
                    nid = note.get("id")
                    title = note.get("title", "").strip() or f"Untitled #{nid}"
                    raw_date = note.get("datetime", "")
                    
                    # Format date
                    try:
                        dt = datetime.fromisoformat(raw_date)
                        display_date = dt.strftime("%b %d, %Y")
                    except Exception:
                        display_date = "No date"
                    
                    # Create display text: "📄 Title - Date"
                    display_text = f"📄 {title} - {display_date}"
                    
                    # Insert into listbox
                    self.notes_listbox.insert(tk.END, display_text)
                    
                except Exception as e:
                    logger.error(f"Failed to display note {note.get('id', '?')}: {e}")
                    continue
            
            logger.info(f"Successfully displayed {len(self.notes)} notes in listbox")
            
            # Update header stats
            if hasattr(self, 'header_stats'):
                self.header_stats.config(text=f"📊 {len(self.notes)} Notes")
            
        except Exception as e:
            logger.error(f"Failed to refresh notes: {e}", exc_info=True)
            messagebox.showerror(
                "📝 Notes Loading Error", 
                f"Could not load your notes from the database:\n{e}\n\n"
                "Possible causes:\n"
                "• Database file may be corrupted\n"
                "• Insufficient file permissions\n"
                "• Missing data directory"
            )

    def filter_notes_live(self):
        """Live filter notes as user types in search box"""
        # Safety check: ensure listbox exists before filtering
        if not hasattr(self, 'notes_listbox'):
            return
        
        query = self.search_var.get().strip().lower()
        
        # If query is the placeholder text, ignore it and show all
        if query.startswith("🔍") or query == self.search_placeholder.lower():
            query = ""
        
        # Clear listbox
        self.notes_listbox.delete(0, tk.END)
        
        # Filter notes
        if not query:
            # Show all notes
            self.filtered_notes = self.notes.copy()
        else:
            # Filter by title or content
            self.filtered_notes = [
                n for n in self.notes
                if query in n.get("title", "").lower() 
                or query in n.get("text", "").lower()
            ]
        
        # Update count
        if hasattr(self, 'notes_count_label'):
            self.notes_count_label.config(
                text=f"({len(self.filtered_notes)}/{len(self.notes)})"
            )
        
        # Display filtered notes
        if not self.filtered_notes:
            self.notes_listbox.insert(tk.END, "🔍 No matching notes found")
            return
        
        for note in self.filtered_notes:
            try:
                nid = note.get("id")
                title = note.get("title", "").strip() or f"Untitled #{nid}"
                raw_date = note.get("datetime", "")
                
                try:
                    dt = datetime.fromisoformat(raw_date)
                    display_date = dt.strftime("%b %d, %Y")
                except Exception:
                    display_date = "No date"
                
                display_text = f"📄 {title} - {display_date}"
                self.notes_listbox.insert(tk.END, display_text)
            except Exception as e:
                logger.error(f"Error displaying filtered note: {e}")

    def on_note_select(self, event):
        """Handle selection from the listbox and populate the editor fields."""
        selection = self.notes_listbox.curselection()
        if not selection:
            return
        
        # Get the selected index
        idx = selection[0]
        
        # Check if it's a placeholder message
        if not self.filtered_notes or idx >= len(self.filtered_notes):
            return
        
        # Get the selected note
        note = self.filtered_notes[idx]
        
        # IMPORTANT: Track the currently loaded note ID
        self.current_note_id = note.get("id")
        
        # Populate editor fields
        self.entry_title.delete(0, tk.END)
        self.entry_title.insert(0, note.get("title", ""))
        
        self.txt_content.delete("1.0", tk.END)
        self.txt_content.insert(tk.END, note.get("text", ""))
        
        self.entry_tags.delete(0, tk.END)
        self.entry_tags.insert(0, note.get("tags", ""))
        
        # Reset modified flag since we just loaded
        self.is_modified = False
        
        logger.info(f"Loaded note ID {self.current_note_id}: {note.get('title', 'Untitled')}")

    def new_note(self):
        self.entry_title.delete(0, tk.END)
        self.txt_content.delete("1.0", tk.END)
        self.entry_tags.delete(0, tk.END)
        # Clear current note ID to indicate this is a new note
        self.current_note_id = None
        self.is_modified = False
        logger.info("New note started - cleared current note ID")

    def save_note(self):
        # determine title; if blank, auto-name as "Untitled note #N"
        title = self.entry_title.get().strip()
        if not title:
            notes_list = storage.list_notes(limit=9999)
            untitled_nums = []
            for n in notes_list:
                t = n.get("title") or ""
                if t.startswith("Untitled note #"):
                    parts = t.split("#")[-1]
                    if parts.isdigit():
                        untitled_nums.append(int(parts))
            next_idx = max(untitled_nums) + 1 if untitled_nums else 1
            title = f"Untitled note #{next_idx}"
        text = self.txt_content.get("1.0", tk.END).strip()
        tags = self.entry_tags.get().strip()
        if not text:
            messagebox.showwarning("Empty", "Please enter some content")
            return
        xp = 5 + min(50, len(text) // 20)
        
        # Check if we're editing an existing note or creating new one
        if self.current_note_id is not None:
            # UPDATE existing note
            success = storage.update_note(self.current_note_id, title, text, tags, xp)
            if success:
                self.status_var.set(f"Updated note ID {self.current_note_id}")
                logger.info(f"Note updated: {title} (ID: {self.current_note_id})")
            else:
                # Note not found, create new one
                nid = storage.save_note(title, text, tags, xp=xp)
                self.current_note_id = nid
                self.status_var.set(f"Saved new note ID {nid} (+{xp} XP)")
                logger.info(f"Note created (original not found): {title} (ID: {nid})")
        else:
            # CREATE new note
            nid = storage.save_note(title, text, tags, xp=xp)
            self.current_note_id = nid
            self.status_var.set(f"Saved new note ID {nid} (+{xp} XP)")
            logger.info(f"Note created: {title} (ID: {nid})")
        
        self.after(2500, lambda: self.status_var.set(""))
        self.is_modified = False  # Reset modification flag
        if hasattr(self, "autosave_indicator"):
            self.autosave_indicator.show_saved()
        self.refresh_notes()
        self.refresh_dashboard()

    def save_note_silent(self):
        """Autosave without showing message"""
        try:
            title = self.entry_title.get().strip()
            text = self.txt_content.get("1.0", tk.END).strip()
            
            # Don't save if text is empty or too short (prevents empty note creation)
            if not text or len(text) < 3:
                logger.debug("Autosave skipped - content too short or empty")
                return
            
            # Don't save if fields are completely empty (prevents accidental saves during deletion)
            if not title and not text:
                logger.debug("Autosave skipped - all fields empty")
                return

            if not title:
                notes_list = storage.list_notes(limit=9999)
                untitled_nums = []
                for n in notes_list:
                    t = n.get("title") or ""
                    if t.startswith("Untitled note #"):
                        parts = t.split("#")[-1]
                        if parts.isdigit():
                            untitled_nums.append(int(parts))
                next_idx = max(untitled_nums) + 1 if untitled_nums else 1
                title = f"Untitled note #{next_idx}"

            tags = self.entry_tags.get().strip()
            xp = 5 + min(50, len(text) // 20)
            
            # Check if editing existing note or creating new
            if self.current_note_id is not None:
                # UPDATE existing note
                success = storage.update_note(self.current_note_id, title, text, tags, xp)
                if success:
                    logger.debug(f"Autosave updated note ID {self.current_note_id}: '{title[:30]}...'")
                else:
                    # Note not found, create new
                    nid = storage.save_note(title, text, tags, xp=xp)
                    self.current_note_id = nid
                    logger.debug(f"Autosave created new note ID {nid} (original not found)")
            else:
                # CREATE new note
                nid = storage.save_note(title, text, tags, xp=xp)
                self.current_note_id = nid
                logger.debug(f"Autosave created new note ID {nid}: '{title[:30]}...'")

            self.is_modified = False
            if hasattr(self, "autosave_indicator"):
                self.autosave_indicator.show_saved()
        except Exception as e:
            logger.error(f"Autosave failed: {e}")
            if hasattr(self, "autosave_indicator"):
                self.autosave_indicator.show_error()

    def mark_modified(self, *args):
        """Mark content as modified"""
        self.is_modified = True
        if hasattr(self, "autosave_indicator"):
            self.autosave_indicator.show_saving()

    def _on_text_modified(self, event=None):
        """Handle text widget modification event"""
        # Clear the modified flag to prevent repeated triggers
        if self.txt_content.edit_modified():
            # Save current state to undo stack
            current_text = self.txt_content.get("1.0", tk.END)
            if current_text != self.last_saved_state:
                if len(self.undo_stack) == 0 or self.undo_stack[-1] != current_text:
                    self.undo_stack.append(self.last_saved_state)
                    # Limit undo stack size
                    if len(self.undo_stack) > 50:
                        self.undo_stack.pop(0)
                self.last_saved_state = current_text
            self.mark_modified()
            self.txt_content.edit_modified(False)

    def undo_note(self):
        """Undo the last change in the note editor"""
        if not self.undo_stack:
            logger.info("Nothing to undo")
            return

        # Save current state to redo stack
        current_text = self.txt_content.get("1.0", tk.END)
        self.redo_stack.append(current_text)

        # Restore previous state
        previous_state = self.undo_stack.pop()
        self.txt_content.delete("1.0", tk.END)
        self.txt_content.insert("1.0", previous_state)
        self.last_saved_state = previous_state
        logger.info("Undo performed")

    def redo_note(self):
        """Redo the last undone change"""
        if not self.redo_stack:
            logger.info("Nothing to redo")
            return

        # Save current state to undo stack
        current_text = self.txt_content.get("1.0", tk.END)
        self.undo_stack.append(current_text)

        # Restore next state
        next_state = self.redo_stack.pop()
        self.txt_content.delete("1.0", tk.END)
        self.txt_content.insert("1.0", next_state)
        self.last_saved_state = next_state
        logger.info("Redo performed")

    def delete_selected_note(self):
        """Delete the currently selected note from the listbox"""
        selection = self.notes_listbox.curselection()
        if not selection:
            messagebox.showwarning("Select Note", "Please select a note to delete")
            return
        
        # Get the selected index
        idx = selection[0]
        
        logger.info(f"Delete request - listbox index: {idx}")
        
        # Check if it's a valid note (not a placeholder message)
        if not self.filtered_notes or idx >= len(self.filtered_notes):
            messagebox.showwarning("Select Note", "No valid note selected")
            return
        
        # Get the note to delete
        note = self.filtered_notes[idx]
        nid = note.get("id")
        note_title = note.get("title", "Untitled")
        
        logger.info(f"Deleting note ID: {nid}, Title: {note_title}")
        
        # CRITICAL: Stop autosave timer to prevent resurrection
        self.stop_autosave_timer()
        logger.info("Autosave timer stopped")
        
        # Store original note data in case user cancels
        original_title = note.get("title", "")
        original_text = note.get("text", "")
        original_tags = note.get("tags", "")
        
        # CRITICAL: Clear the editor fields BEFORE showing the confirmation dialog
        # This prevents autosave from re-saving the note while the dialog is open
        self.entry_title.delete(0, tk.END)
        self.txt_content.delete("1.0", tk.END)
        self.entry_tags.delete(0, tk.END)
        
        # Reset modification flag to prevent autosave
        self.is_modified = False
        if hasattr(self, "autosave_indicator"):
            self.autosave_indicator.show_saved()
        
        logger.info("Editor cleared before deletion to prevent autosave resurrection")

        # Confirm deletion
        ok = messagebox.askyesno(
            "Delete Note", 
            f"Are you sure you want to delete:\n\n'{note_title}'?"
        )
        
        if not ok:
            logger.info("Delete cancelled by user - restoring note to editor")
            # Reload the note if user cancels using stored data
            self.entry_title.insert(0, original_title)
            self.txt_content.insert(tk.END, original_text)
            self.entry_tags.insert(0, original_tags)
            # Restart autosave timer
            self.start_autosave_timer()
            logger.info("Autosave timer restarted after cancel")
            return

        try:
            logger.info(f"Calling storage.delete_note({nid})")
            removed = storage.delete_note(nid)
            logger.info(f"Delete result: {removed}")
        except Exception as e:
            logger.error(f"Exception during delete: {e}", exc_info=True)
            messagebox.showerror(
                "🗑️ Delete Error", 
                f"Could not delete the note:\n{e}\n\n"
                "Possible causes:\n"
                "• Database access issue\n"
                "• File permissions problem\n"
                "• Note may be locked by another process"
            )
            # Restart autosave timer after error
            self.start_autosave_timer()
            logger.info("Autosave timer restarted after error")
            return

        if removed:
            logger.info(f"Successfully deleted note {nid}")
            self.status_var.set(f"✓ Note '{note_title}' deleted")
            self.after(3000, lambda: self.status_var.set(""))
            # Clear current note ID since note was deleted
            self.current_note_id = None
            self.refresh_notes()
            self.refresh_dashboard()
            # Restart autosave timer after successful deletion
            self.start_autosave_timer()
            logger.info("Autosave timer restarted after successful deletion")
        else:
            logger.warning(f"Note {nid} could not be deleted (not found?)")
            messagebox.showerror(
                "🗑️ Delete Failed", 
                "The note could not be deleted.\n\n"
                "Possible reasons:\n"
                "• Note may have already been deleted\n"
                "• Database synchronization issue\n\n"
                "Try refreshing the notes list (Ctrl+R)"
            )
            # Restart autosave timer even if delete failed
            self.start_autosave_timer()
            logger.info("Autosave timer restarted after failed deletion")

    def record_note_thread(self):
        threading.Thread(target=self.record_note, daemon=True).start()

    def record_note(self):
        res = speech_notes.transcribe_from_microphone()
        if isinstance(res, dict) and res.get("error"):
            error_msg = res.get("error")
            messagebox.showerror(
                "🎤 Voice Recording Error", 
                f"Could not record audio:\n{error_msg}\n\n"
                "Troubleshooting:\n"
                "• Check microphone permissions\n"
                "• Ensure microphone is connected\n"
                "• Try speaking louder and clearer"
            )
            return
        text = res.get("text") if isinstance(res, dict) else str(res)
        self.txt_content.delete("1.0", tk.END)
        self.txt_content.insert(tk.END, text)
        messagebox.showinfo("✅ Transcribed", "Voice note successfully transcribed and added to editor!")

    def summarize_selected(self):
        """Generate AI summary using new SummaryModal and ai_utils"""
        text = self.txt_content.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("No text", "Write or select a note first")
            return

        logger.info("Starting AI summary generation")

        # Show loading spinner
        loading = LoadingSpinner(self, "Generating AI summary...")
        loading.pack(pady=20)
        loading.start()

        def _worker():
            try:
                summary = ai_utils.summarize_text(text)
                self.after(0, lambda: _finish_summary(summary))
            except Exception as e:
                logger.error(f"Summary generation failed: {e}")
                self.after(0, lambda err=e: _finish_summary(None, str(err)))

        def _finish_summary(summary, error=None):
            loading.stop()
            loading.destroy()

            if error:
                messagebox.showerror(
                    "Summary Error", f"Failed to generate summary:\n{error}"
                )
                return

            if summary:
                logger.info("Summary generated successfully")
                # Use the new SummaryModal
                modal = SummaryModal(
                    self,
                    title="✨ AI Summary",
                    summary_text=summary,
                    original_text=text,
                )
            else:
                messagebox.showwarning("No Summary", "Could not generate summary")

        threading.Thread(target=_worker, daemon=True).start()

    def generate_flashcards(self):
        """Generate AI flashcards with flip animation"""
        text = self.txt_content.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Empty", "Select a note or write something")
            return

        logger.info("Starting flashcard generation")

        # Show loading spinner
        loading = LoadingSpinner(self, "Generating flashcards...")
        loading.pack(pady=20)
        loading.start()

        def _worker():
            try:
                flashcards = ai_utils.generate_flashcards(text, num_cards=5)
                self.after(0, lambda: _show_flashcards(flashcards))
            except Exception as e:
                logger.error(f"Flashcard generation failed: {e}")
                self.after(0, lambda err=e: _show_flashcards(None, str(err)))

        def _show_flashcards(cards, error=None):
            loading.stop()
            loading.destroy()

            if error:
                messagebox.showerror(
                    "Flashcard Error", f"Failed to generate flashcards:\n{error}"
                )
                return

            if not cards:
                messagebox.showwarning(
                    "No Flashcards", "Could not generate flashcards from this text"
                )
                return

            logger.info(f"Generated {len(cards)} flashcards")
            self._show_flashcard_modal(cards)

        threading.Thread(target=_worker, daemon=True).start()

    def _show_flashcard_modal(self, flashcards):
        """Display flashcards in an interactive modal with flip animation"""
        modal = Modal(self, title="🎴 Flashcards", width=700, height=500)

        current_index = [0]  # Use list to allow modification in nested function
        showing_question = [True]  # True = question side, False = answer side

        # Card display frame
        card_frame = CardFrame(modal.content, title="")
        card_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Card text
        card_text = tk.Text(
            card_frame,
            wrap="word",
            font=(config.FONT_FAMILY, 17),
            relief="flat",
            bg=config.LIGHT_COLORS["surface"],
            fg=config.LIGHT_COLORS["text"],
            padx=22,
            pady=22,
            height=10,
        )
        card_text.pack(fill="both", expand=True)
        card_text.config(state="disabled")

        # Progress label
        progress_label = ttk.Label(
            card_frame,
            text="",
            font=(config.FONT_FAMILY, 13),
            foreground=config.LIGHT_COLORS["text_secondary"],
        )
        progress_label.pack(pady=(10, 0))

        def update_card():
            """Update the displayed card"""
            idx = current_index[0]
            card = flashcards[idx]
            is_question = showing_question[0]

            # Update card text
            card_text.config(state="normal")
            card_text.delete("1.0", tk.END)

            if is_question:
                card_text.insert("1.0", f"Question:\n\n{card['question']}")
                card_text.tag_add("header", "1.0", "1.9")
                card_text.tag_config("header", font=(config.FONT_FAMILY, 15, "bold"))
            else:
                card_text.insert("1.0", f"Answer:\n\n{card['answer']}")
                card_text.tag_add("header", "1.0", "1.7")
                card_text.tag_config("header", font=(config.FONT_FAMILY, 15, "bold"))

            card_text.config(state="disabled")

            # Update progress
            progress_label.config(text=f"Card {idx + 1} of {len(flashcards)}")

            # Update button states
            prev_btn.config(state="normal" if idx > 0 else "disabled")
            next_btn.config(state="normal" if idx < len(flashcards) - 1 else "disabled")
            flip_btn.config(text="Show Answer" if is_question else "Show Question")

        def flip_card():
            """Flip between question and answer"""
            showing_question[0] = not showing_question[0]
            update_card()

        def prev_card():
            """Go to previous card"""
            if current_index[0] > 0:
                current_index[0] -= 1
                showing_question[0] = True  # Reset to question side
                update_card()

        def next_card():
            """Go to next card"""
            if current_index[0] < len(flashcards) - 1:
                current_index[0] += 1
                showing_question[0] = True  # Reset to question side
                update_card()

        # Button bar
        button_frame = ttk.Frame(modal.content)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        prev_btn = RoundedButton(
            button_frame, text="◀ Previous", bootstyle="secondary", command=prev_card
        )
        prev_btn.pack(side="left", padx=5)

        flip_btn = RoundedButton(
            button_frame, text="Show Answer", bootstyle="info", command=flip_card
        )
        flip_btn.pack(side="left", expand=True, fill="x", padx=5)

        next_btn = RoundedButton(
            button_frame, text="Next ▶", bootstyle="secondary", command=next_card
        )
        next_btn.pack(side="left", padx=5)

        close_btn = RoundedButton(
            button_frame, text="Close", bootstyle="secondary", command=modal.destroy
        )
        close_btn.pack(side="right", padx=5)

        # Show first card
        update_card()

    def show_rewrite_menu(self):
        """Show menu with rewrite options"""
        text = self.txt_content.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Empty", "Write some text first")
            return

        # Create modal with style options
        modal = Modal(self, title="✍️ Rewrite Text", width=400, height=300)

        ttk.Label(
            modal.content,
            text="Choose a rewriting style:",
            font=(config.FONT_FAMILY, 15, "bold"),
        ).pack(pady=22)

        styles = [
            ("📝 Paraphrase", "paraphrase", "Reword while keeping the same meaning"),
            ("🔤 Simplify", "simplify", "Make it easier to understand"),
            ("🎩 Make Formal", "formal", "Use professional language"),
            ("💬 Make Casual", "casual", "Use conversational language"),
        ]

        for emoji_text, style_id, description in styles:
            frame = CardFrame(modal.content, title="")
            frame.pack(fill="x", padx=20, pady=5)

            btn = RoundedButton(
                frame,
                text=emoji_text,
                bootstyle="info-outline",
                command=lambda s=style_id: self._rewrite_with_style(s, text, modal),
            )
            btn.pack(fill="x", pady=5)

            ttk.Label(
                frame,
                text=description,
                font=(config.FONT_FAMILY, 12),
                foreground=config.LIGHT_COLORS["text_secondary"],
            ).pack(pady=(0, 6))

        modal.add_button("Cancel", modal.destroy, bootstyle="secondary")

    def _rewrite_with_style(self, style, original_text, menu_modal):
        """Rewrite text with the selected style"""
        menu_modal.destroy()
        logger.info(f"Rewriting text with style: {style}")

        # Show loading spinner
        loading = LoadingSpinner(self, f"Rewriting text ({style})...")
        loading.pack(pady=20)
        loading.start()

        def _worker():
            try:
                rewritten = ai_utils.rewrite_text(original_text, style)
                self.after(0, lambda: _finish_rewrite(rewritten))
            except Exception as e:
                logger.error(f"Rewrite failed: {e}")
                self.after(0, lambda err=e: _finish_rewrite(None, str(err)))

        def _finish_rewrite(rewritten_text, error=None):
            loading.stop()
            loading.destroy()

            if error:
                messagebox.showerror(
                    "Rewrite Error", f"Failed to rewrite text:\n{error}"
                )
                return

            if not rewritten_text:
                messagebox.showwarning("No Result", "Could not rewrite the text")
                return

            logger.info("Text rewritten successfully")
            self._show_rewrite_result(original_text, rewritten_text, style)

        threading.Thread(target=_worker, daemon=True).start()

    def _show_rewrite_result(self, original, rewritten, style):
        """Show the rewritten text with option to replace"""
        modal = Modal(
            self, title=f"✍️ Rewritten Text ({style.title()})", width=800, height=600
        )

        # Original text
        ttk.Label(
            modal.content, text="Original:", font=(config.FONT_FAMILY, 13, "bold")
        ).pack(anchor="w", padx=22, pady=(12, 6))

        original_text = tk.Text(
            modal.content,
            wrap="word",
            height=8,
            font=(config.FONT_FAMILY, 13),
            bg=config.LIGHT_COLORS["background"],
            fg=config.LIGHT_COLORS["text_secondary"],
        )
        original_text.pack(fill="both", expand=True, padx=22, pady=(0, 12))
        original_text.insert("1.0", original)
        original_text.config(state="disabled")

        # Arrow separator
        ttk.Label(
            modal.content,
            text="⬇ Rewritten ⬇",
            font=(config.FONT_FAMILY, 13, "bold"),
            foreground=config.LIGHT_COLORS["primary"],
        ).pack(pady=6)

        # Rewritten text
        rewritten_text = tk.Text(
            modal.content,
            wrap="word",
            height=8,
            font=(config.FONT_FAMILY, 13),
            bg=config.LIGHT_COLORS["surface"],
            fg=config.LIGHT_COLORS["text"],
        )
        rewritten_text.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        rewritten_text.insert("1.0", rewritten)

        def replace_text():
            """Replace the original text with rewritten version"""
            self.txt_content.delete("1.0", tk.END)
            self.txt_content.insert("1.0", rewritten)
            self.mark_modified()
            modal.destroy()
            messagebox.showinfo("Success", "Text replaced with rewritten version")

        def copy_rewritten():
            """Copy rewritten text to clipboard"""
            modal.clipboard_clear()
            modal.clipboard_append(rewritten)
            messagebox.showinfo("Copied", "Rewritten text copied to clipboard")

        # Buttons
        modal.add_button("Replace Original", replace_text, bootstyle="success")
        modal.add_button("Copy to Clipboard", copy_rewritten, bootstyle="info")
        modal.add_button("Close", modal.destroy, bootstyle="secondary")

    # ---------------- Reminders Tab ----------------
    def build_reminders_tab(self, parent):
        # Main container with padding
        main_container = ttk.Frame(parent, padding=15)
        main_container.pack(fill="both", expand=True)
        
        # Left side - Schedule form
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Header
        header_frame = ttk.Frame(left_frame)
        header_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(
            header_frame, text="⏰ Schedule New Reminder", font=("Segoe UI", 19, "bold")
        ).pack(anchor="w")
        
        ttk.Label(
            header_frame, 
            text="Set up study reminders to stay on track with your learning goals",
            font=("Segoe UI", 13),
            foreground="gray"
        ).pack(anchor="w", pady=(6, 0))
        
        # Date & Time Selection Card
        datetime_card = ttk.Labelframe(left_frame, text="📅 Date & Time", padding=15)
        datetime_card.pack(fill="x", pady=(0, 15))
        
        # Date Selection Row
        date_row = ttk.Frame(datetime_card)
        date_row.pack(fill="x", pady=(0, 10))
        
        ttk.Label(date_row, text="Date:", font=("Segoe UI", 14)).pack(side="left", padx=(0, 12))
        
        # Year dropdown
        current_year = datetime.now().year
        self.rem_year_var = tk.StringVar(value=str(current_year))
        year_combo = ttk.Combobox(
            date_row, 
            textvariable=self.rem_year_var,
            values=[str(current_year + i) for i in range(3)],  # Current year + 2 years ahead
            width=8,
            font=("Segoe UI", 14),
            state="readonly"
        )
        year_combo.pack(side="left", padx=(0, 6))
        
        # Month dropdown
        self.rem_month_var = tk.StringVar(value=str(datetime.now().month).zfill(2))
        month_combo = ttk.Combobox(
            date_row,
            textvariable=self.rem_month_var,
            values=[f"{i:02d} - {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][i-1]}" for i in range(1, 13)],
            width=12,
            font=("Segoe UI", 14),
            state="readonly"
        )
        month_combo.pack(side="left", padx=(0, 6))
        
        # Day dropdown
        self.rem_day_var = tk.StringVar(value=str(datetime.now().day).zfill(2))
        day_combo = ttk.Combobox(
            date_row,
            textvariable=self.rem_day_var,
            values=[f"{i:02d}" for i in range(1, 32)],
            width=6,
            font=("Segoe UI", 14),
            state="readonly"
        )
        day_combo.pack(side="left")
        
        # Time Selection Row
        time_row = ttk.Frame(datetime_card)
        time_row.pack(fill="x")
        
        ttk.Label(time_row, text="Time:", font=("Segoe UI", 14)).pack(side="left", padx=(0, 12))
        
        # Hour dropdown
        self.rem_hour_var = tk.StringVar(value=str(datetime.now().hour).zfill(2))
        hour_combo = ttk.Combobox(
            time_row,
            textvariable=self.rem_hour_var,
            values=[f"{i:02d}" for i in range(24)],
            width=6,
            font=("Segoe UI", 14),
            state="readonly"
        )
        hour_combo.pack(side="left", padx=(0, 6))
        
        ttk.Label(time_row, text=":", font=("Segoe UI", 17, "bold")).pack(side="left", padx=(0, 6))
        
        # Minute dropdown
        self.rem_minute_var = tk.StringVar(value="00")
        minute_combo = ttk.Combobox(
            time_row,
            textvariable=self.rem_minute_var,
            values=[f"{i:02d}" for i in range(0, 60, 5)],  # 5-minute intervals
            width=6,
            font=("Segoe UI", 14),
            state="readonly"
        )
        minute_combo.pack(side="left")
        
        # Quick time buttons
        quick_time_frame = ttk.Frame(datetime_card)
        quick_time_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Label(quick_time_frame, text="Quick select:", font=("Segoe UI", 12), foreground="gray").pack(side="left", padx=(0, 10))
        
        def set_quick_time(hours_ahead):
            future_time = datetime.now() + timedelta(hours=hours_ahead)
            self.rem_year_var.set(str(future_time.year))
            self.rem_month_var.set(f"{future_time.month:02d} - {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][future_time.month-1]}")
            self.rem_day_var.set(f"{future_time.day:02d}")
            self.rem_hour_var.set(f"{future_time.hour:02d}")
            self.rem_minute_var.set(f"{future_time.minute:02d}")
        
        quick_buttons = [
            ("1 Hour", 1),
            ("3 Hours", 3),
            ("Tomorrow", 24),
            ("1 Week", 168)
        ]
        
        for text, hours in quick_buttons:
            if TTKBOOTSTRAP_AVAILABLE:
                ttk.Button(
                    quick_time_frame,
                    text=text,
                    command=lambda h=hours: set_quick_time(h),
                    bootstyle="info-outline",
                    width=10
                ).pack(side="left", padx=2)
            else:
                ttk.Button(
                    quick_time_frame,
                    text=text,
                    command=lambda h=hours: set_quick_time(h),
                    width=10
                ).pack(side="left", padx=2)
        
        # Message Card
        message_card = ttk.Labelframe(left_frame, text="💬 Reminder Message", padding=15)
        message_card.pack(fill="x", pady=(0, 15))
        
        self.rem_msg = ttk.Entry(message_card, font=("Segoe UI", 15))
        self.rem_msg.pack(fill="x", pady=(0, 10))
        self.rem_msg.insert(0, "Time to study! 📚")
        
        # Suggested messages
        suggestions_frame = ttk.Frame(message_card)
        suggestions_frame.pack(fill="x")
        
        ttk.Label(suggestions_frame, text="Suggestions:", font=("Segoe UI", 12), foreground="gray").pack(side="left", padx=(0, 10))
        
        suggestions = ["Review notes 📝", "Practice quiz 🎯", "Study break 🧘", "Assignment due ⚠️"]
        for suggestion in suggestions:
            if TTKBOOTSTRAP_AVAILABLE:
                ttk.Button(
                    suggestions_frame,
                    text=suggestion,
                    command=lambda s=suggestion: (self.rem_msg.delete(0, tk.END), self.rem_msg.insert(0, s)),
                    bootstyle="secondary-outline",
                    width=15
                ).pack(side="left", padx=2)
            else:
                ttk.Button(
                    suggestions_frame,
                    text=suggestion,
                    command=lambda s=suggestion: (self.rem_msg.delete(0, tk.END), self.rem_msg.insert(0, s)),
                    width=15
                ).pack(side="left", padx=2)
        
        # Repeat Options Card
        repeat_card = ttk.Labelframe(left_frame, text="🔁 Repeat Schedule", padding=15)
        repeat_card.pack(fill="x", pady=(0, 15))
        
        self.repeat_var = tk.StringVar(value="once")
        
        repeat_options = [
            ("Once", "once", "🔵"),
            ("Daily", "daily", "📅"),
            ("Weekly", "weekly", "📆"),
            ("Monthly", "monthly", "🗓️"),
        ]
        
        for i, (text, value, icon) in enumerate(repeat_options):
            frame = ttk.Frame(repeat_card)
            frame.pack(side="left", padx=(0, 15) if i < len(repeat_options) - 1 else 0)
            
            ttk.Radiobutton(
                frame, 
                text=f"{icon} {text}", 
                variable=self.repeat_var, 
                value=value,
                style="Toolbutton" if TTKBOOTSTRAP_AVAILABLE else None
            ).pack()
        
        # Action Buttons
        action_frame = ttk.Frame(left_frame)
        action_frame.pack(fill="x", pady=(0, 10))
        
        if TTKBOOTSTRAP_AVAILABLE:
            ttk.Button(
                action_frame,
                text="✅ Schedule Reminder",
                command=self.schedule_reminder,
                bootstyle="success",
                width=20
            ).pack(side="left", padx=(0, 8))
            ttk.Button(
                action_frame,
                text="🔄 Refresh List",
                command=self.refresh_reminders,
                bootstyle="info-outline",
                width=15
            ).pack(side="left", padx=(0, 8))
            ttk.Button(
                action_frame,
                text="🗑️ Clear Form",
                command=self.clear_reminder_form,
                bootstyle="secondary-outline",
                width=12
            ).pack(side="left")
        else:
            ttk.Button(
                action_frame,
                text="✅ Schedule Reminder",
                command=self.schedule_reminder,
                width=20
            ).pack(side="left", padx=(0, 8))
            ttk.Button(
                action_frame,
                text="🔄 Refresh List",
                command=self.refresh_reminders,
                width=15
            ).pack(side="left", padx=(0, 8))
            ttk.Button(
                action_frame,
                text="🗑️ Clear Form",
                command=self.clear_reminder_form,
                width=12
            ).pack(side="left")
        
        # Right side - Active Reminders List
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side="right", fill="both", expand=True)
        
        # List header
        list_header = ttk.Frame(right_frame)
        list_header.pack(fill="x", pady=(0, 10))
        
        ttk.Label(
            list_header, text="📋 Active Reminders", font=("Segoe UI", 17, "bold")
        ).pack(side="left")
        
        # Reminder count badge
        self.reminder_count_label = ttk.Label(
            list_header, 
            text="0", 
            font=("Segoe UI", 13, "bold"),
            foreground="white",
            background="#007bff" if self.current_theme == "light" else "#0056b3",
            padding=(10, 5)
        )
        self.reminder_count_label.pack(side="left", padx=(12, 0))
        
        # Listbox with scrollbar
        list_container = ttk.Frame(right_frame)
        list_container.pack(fill="both", expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side="right", fill="y")
        
        self.lb_rem = tk.Listbox(
            list_container, 
            height=20, 
            font=("Segoe UI", 14),
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            relief="flat",
            borderwidth=2
        )
        self.lb_rem.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.lb_rem.yview)
        
        # List action buttons
        list_btns = ttk.Frame(right_frame)
        list_btns.pack(fill="x")
        
        if TTKBOOTSTRAP_AVAILABLE:
            ttk.Button(
                list_btns,
                text="❌ Cancel Selected",
                command=self.cancel_selected_reminder,
                bootstyle="danger",
                width=18
            ).pack(side="left", padx=(0, 8))
            ttk.Button(
                list_btns,
                text="�️ Clear All",
                command=self.clear_all_reminders,
                bootstyle="danger-outline",
                width=15
            ).pack(side="left")
        else:
            ttk.Button(
                list_btns,
                text="❌ Cancel Selected",
                command=self.cancel_selected_reminder,
                width=18
            ).pack(side="left", padx=(0, 8))
            ttk.Button(
                list_btns,
                text="�️ Clear All",
                command=self.clear_all_reminders,
                width=15
            ).pack(side="left")
    
    def clear_reminder_form(self):
        """Clear all reminder form fields"""
        now = datetime.now()
        self.rem_year_var.set(str(now.year))
        self.rem_month_var.set(f"{now.month:02d} - {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][now.month-1]}")
        self.rem_day_var.set(f"{now.day:02d}")
        self.rem_hour_var.set(f"{now.hour:02d}")
        self.rem_minute_var.set("00")
        self.rem_msg.delete(0, tk.END)
        self.rem_msg.insert(0, "Time to study! 📚")
        self.repeat_var.set("once")
    
    def clear_all_reminders(self):
        """Clear all active reminders"""
        if messagebox.askyesno("Clear All", "Are you sure you want to cancel ALL reminders?"):
            try:
                jobs = reminders.list_jobs()
                for jid, _ in jobs:
                    reminders.remove_job(jid)
                self.refresh_reminders()
                messagebox.showinfo("Success", "✅ All reminders cleared!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear reminders: {e}")

    def schedule_reminder(self):
        # Get values from dropdowns
        year = self.rem_year_var.get()
        month_str = self.rem_month_var.get().split(" - ")[0]  # Extract just the number from "01 - Jan"
        day = self.rem_day_var.get()
        hour = self.rem_hour_var.get()
        minute = self.rem_minute_var.get()
        msg = self.rem_msg.get().strip() or "Time to study! 📚"
        repeat = self.repeat_var.get()

        try:
            # Construct datetime from dropdown values
            dt = datetime(
                year=int(year),
                month=int(month_str),
                day=int(day),
                hour=int(hour),
                minute=int(minute)
            )
            
            # Validate that date is in the future
            if dt <= datetime.now():
                messagebox.showerror(
                    "⏰ Invalid Date", 
                    "Reminder time must be in the future!\n\n"
                    f"Selected: {dt.strftime('%Y-%m-%d %H:%M')}\n"
                    f"Current: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
                return
        except ValueError as e:
            messagebox.showerror(
                "❌ Invalid Date", 
                f"Invalid date combination:\n{e}\n\n"
                "Please check your date and time selections."
            )
            return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create reminder:\n{e}")
            return

        def _sched():
            try:
                # Schedule with repeat option
                if repeat == "once":
                    jid = reminders.schedule_reminder(dt, msg)
                    repeat_text = ""
                else:
                    # For repeating reminders, we'd need to enhance the reminders module
                    # For now, schedule the first occurrence
                    jid = reminders.schedule_reminder(dt, f"{msg} (Repeats: {repeat})")
                    repeat_text = f" (Repeating {repeat})"

                self.after(
                    200,
                    lambda: (
                        self.clear_reminder_form(),
                        self.refresh_reminders(),
                    ),
                )
                messagebox.showinfo(
                    "✅ Scheduled", 
                    f"Reminder scheduled successfully!\n\n"
                    f"📅 Time: {dt.strftime('%b %d, %Y %H:%M')}\n"
                    f"💬 Message: {msg}\n"
                    f"🔁 Repeat: {repeat.capitalize()}{repeat_text}"
                )
            except Exception as e:
                logger.error(f"Failed to schedule reminder: {e}")
                messagebox.showerror("❌ Schedule Error", f"Failed to schedule reminder:\n{e}")

        threading.Thread(target=_sched, daemon=True).start()

    def refresh_reminders(self):
        self.lb_rem.delete(0, tk.END)
        try:
            jobs = reminders.list_jobs()
            
            # Update count badge
            if hasattr(self, 'reminder_count_label'):
                self.reminder_count_label.config(text=str(len(jobs)))
            
            if not jobs:
                self.lb_rem.insert(tk.END, "")
                self.lb_rem.insert(tk.END, "   📭 No active reminders")
                self.lb_rem.insert(tk.END, "")
                self.lb_rem.insert(tk.END, "   Create your first reminder using the form on the left!")
            else:
                for i, (jid, nxt) in enumerate(jobs, 1):
                    # Format: "1. 📅 Message - Next: Dec 2, 2025 14:30"
                    try:
                        # Parse and format the datetime nicely
                        next_time = datetime.fromisoformat(nxt) if isinstance(nxt, str) else nxt
                        formatted_time = next_time.strftime("%b %d, %Y %H:%M")
                    except:
                        formatted_time = str(nxt)
                    
                    display_text = f"{i}. 📅 {jid} - Next: {formatted_time}"
                    self.lb_rem.insert(tk.END, display_text)
        except Exception as e:
            logger.error(f"Failed to refresh reminders: {e}")
            self.lb_rem.insert(tk.END, f"❌ Error loading reminders: {e}")
            if hasattr(self, 'reminder_count_label'):
                self.reminder_count_label.config(text="0")

    def cancel_selected_reminder(self):
        sel = self.lb_rem.curselection()
        if not sel:
            messagebox.showwarning("Select", "Select a reminder first")
            return
        text = self.lb_rem.get(sel[0])
        jid = text.split(" - ")[0]
        ok = reminders.remove_job(jid)
        if ok:
            messagebox.showinfo("Cancelled", f"{jid} removed")
        else:
            messagebox.showerror("Error", f"Could not remove {jid}")
        self.refresh_reminders()

    def remind_for_selected_note(self):
        """Set a reminder for the currently selected note"""
        selection = self.notes_listbox.curselection()
        if not selection:
            messagebox.showwarning("Select Note", "Please select a note first")
            return
        
        # Get the selected index
        idx = selection[0]
        
        # Check if it's a valid note
        if not self.filtered_notes or idx >= len(self.filtered_notes):
            messagebox.showwarning("Select Note", "No valid note selected")
            return
        
        # Get the selected note
        note = self.filtered_notes[idx]
        
        snippet = note.get("text", "")[:140].replace("\n", " ")
        pre_message = f"{note.get('title', '(no-title)')} - {snippet}"
        dt_txt = simpledialog.askstring(
            "Reminder time", "Enter reminder time (YYYY-MM-DD HH:MM)"
        )
        if not dt_txt:
            return
        try:
            dt = datetime.strptime(dt_txt.strip(), "%Y-%m-%d %H:%M")
        except Exception as e:
            messagebox.showerror("Invalid", f"Invalid datetime: {e}")
            return

        def _sched_note():
            jid = reminders.schedule_reminder(dt, pre_message)
            self.after(200, self.refresh_reminders)
            messagebox.showinfo("Scheduled", f"Reminder set for note (job id: {jid})")

        threading.Thread(target=_sched_note, daemon=True).start()

    # ---------------- Quiz Tab ----------------
    def build_quiz_tab(self, parent):
        parent.configure(style="TFrame")

        # Header with buttons
        header_frame = ttk.Frame(parent, padding=10)
        header_frame.pack(fill="x", padx=8, pady=8)

        ttk.Label(
            header_frame, text="🎯 Quiz Generator", font=("Segoe UI", 19, "bold")
        ).pack(anchor="nw", pady=(0, 10))

        top = ttk.Frame(header_frame)
        top.pack(fill="x", pady=(0, 5))
        ttk.Button(
            top,
            text="✨ Generate 5 Questions",
            command=self.generate_quiz,
            bootstyle="primary",
        ).pack(side="left", padx=4)
        self.btn_take_quiz = ttk.Button(
            top, text="📝 Take Quiz", command=self.take_quiz, bootstyle="success", state="disabled"
        )
        self.btn_take_quiz.pack(side="left", padx=4)

        # Quiz display area
        quiz_frame = ttk.Frame(parent, padding=10)
        quiz_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        ttk.Label(
            quiz_frame, text="📚 Questions & Answers", font=("Segoe UI", 17, "bold")
        ).pack(anchor="nw", pady=(0, 10))

        self.txt_quiz = scrolledtext.ScrolledText(
            quiz_frame,
            height=25,
            font=("Segoe UI", 16),
            relief="flat",
            padx=14,
            pady=14,
        )
        self.txt_quiz.pack(fill="both", expand=True, pady=(0, 4))

    def generate_quiz(self):
        # Clear previous quiz and disable take button
        self.current_quiz = None
        self.btn_take_quiz.config(state="disabled")
        self.txt_quiz.delete("1.0", tk.END)
        self.txt_quiz.insert(tk.END, "⏳ Generating intelligent quiz questions using AI...\nPlease wait...")
        
        # Show loading cursor
        self.config(cursor="wait")
        self.update()
        
        try:
            # Collect text from all notes to give AI comprehensive context
            all_notes_text = ""
            notes = storage.list_notes(limit=50)  # Get recent notes for context
            
            if not notes:
                self.txt_quiz.delete("1.0", tk.END)
                self.txt_quiz.insert(tk.END, "❌ No notes found.\n\nPlease create some notes first before generating quiz questions.")
                return
            
            # Combine note content
            for note in notes:
                title = note.get("title", "").strip()
                text = note.get("text", "").strip()
                if text:
                    all_notes_text += f"\n\n=== {title} ===\n{text}"
            
            if not all_notes_text.strip():
                self.txt_quiz.delete("1.0", tk.END)
                self.txt_quiz.insert(tk.END, "❌ Notes are empty.\n\nPlease add content to your notes before generating quiz questions.")
                return
            
            # Use AI to generate intelligent questions
            logger.info("Generating quiz using Gemini AI")
            qs = ai_utils.generate_quiz_questions(all_notes_text, num_questions=5)
            
            self.current_quiz = qs
            self.txt_quiz.delete("1.0", tk.END)
            
            if not qs:
                self.txt_quiz.insert(tk.END, "❌ Could not generate questions.\n\nPossible reasons:\n• Gemini API not configured\n• Notes content too short\n• API rate limit reached\n\nTry adding more detailed notes.")
                return
            
            # Enable take quiz button
            self.btn_take_quiz.config(state="normal")
            
            # Display questions with better formatting
            self.txt_quiz.insert(tk.END, "🎯 AI-Generated Quiz Questions\n")
            self.txt_quiz.insert(tk.END, "=" * 50 + "\n\n")
            
            for i, q in enumerate(qs, start=1):
                text = f"Question {i}:\n{q['question']}\n\n✓ Answer: {q['answer']}\n\n" + "-" * 50 + "\n\n"
                self.txt_quiz.insert(tk.END, text)
                
            logger.info(f"Successfully displayed {len(qs)} AI-generated questions")
        except Exception as e:
            logger.error(f"Error generating quiz: {e}")
            self.txt_quiz.delete("1.0", tk.END)
            self.txt_quiz.insert(tk.END, f"❌ Error generating quiz:\n{str(e)}\n\nPlease try again.")
        finally:
            # Restore cursor
            self.config(cursor="")

    def take_quiz(self):
        qs = getattr(self, "current_quiz", None)
        if not qs:
            messagebox.showwarning("No Quiz", "Generate a quiz first")
            return
        score = 0
        for i, q in enumerate(qs, start=1):
            ans = simpledialog.askstring("Quiz", f"Q{i}: {q['question']}")
            if ans and ans.strip().lower() == q["answer"].strip().lower():
                score += 1
        messagebox.showinfo("Result", f"Score: {score}/{len(qs)}")

    # ---------------- Timer Tab ----------------
    def build_timer_tab(self, parent):
        parent.configure(style="TFrame")

        # Timer control card
        control_frame = ttk.Frame(parent, padding=10)
        control_frame.pack(fill="x", padx=8, pady=8)

        ttk.Label(
            control_frame, text="⏱️ Study Timer", font=("Segoe UI", 19, "bold")
        ).pack(anchor="nw", pady=(0, 10))

        # Custom timer input
        custom_frame = ttk.Frame(control_frame)
        custom_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(custom_frame, text="⏲️ Custom Duration (minutes):", font=("Segoe UI", 15)).pack(
            anchor="w", pady=(0, 5)
        )

        input_row = ttk.Frame(custom_frame)
        input_row.pack(fill="x")

        self.timer_entry = ttk.Entry(input_row, width=12, font=("Segoe UI", 16))
        self.timer_entry.pack(side="left", padx=(0, 8))

        ttk.Button(
            input_row,
            text="▶️ Start",
            command=self.start_timer_from_ui,
            bootstyle="success",
        ).pack(side="left", padx=4)
        ttk.Button(
            input_row, text="⏹️ Stop", command=self.stop_timer, bootstyle="danger"
        ).pack(side="left", padx=4)

        # Quick actions
        quick_frame = ttk.Frame(control_frame)
        quick_frame.pack(fill="x", pady=(8, 0))

        ttk.Label(quick_frame, text="⚡ Quick Actions:").pack(anchor="w", pady=(0, 6))

        quick_btns = ttk.Frame(quick_frame)
        quick_btns.pack(fill="x")

        ttk.Button(
            quick_btns,
            text="🍅 Pomodoro (25 min)",
            command=lambda: self.start_timer(25),
            bootstyle="primary",
        ).pack(side="left", padx=4, expand=True, fill="x")
        ttk.Button(
            quick_btns,
            text="☕ Short Break (5 min)",
            command=lambda: self.start_timer(5),
            bootstyle="info",
        ).pack(side="left", padx=4, expand=True, fill="x")
        ttk.Button(
            quick_btns,
            text="🌳 Long Break (15 min)",
            command=lambda: self.start_timer(15),
            bootstyle="info",
        ).pack(side="left", padx=4, expand=True, fill="x")

        # Countdown display card
        display_frame = ttk.Frame(parent, padding=20)
        display_frame.pack(fill="x", padx=8, pady=(0, 8))

        self.timer_label = ttk.Label(
            display_frame, text="00:00", font=("Segoe UI", 59, "bold")
        )
        self.timer_label.pack(pady=(12, 6))

        ttk.Label(display_frame, text="Timer not running", font=("Segoe UI", 17)).pack(
            pady=(0, 12)
        )

        # History card
        history_frame = ttk.Frame(parent, padding=10)
        history_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        ttk.Label(
            history_frame,
            text="📜 Recent Study Sessions",
            font=("Segoe UI", 17, "bold"),
        ).pack(anchor="nw", pady=(0, 10))

        self.timer_history = tk.Listbox(
            history_frame, height=6, font=("Segoe UI", 15), relief="flat", borderwidth=0
        )
        self.timer_history.pack(fill="both", expand=True, pady=(0, 4))

    def start_timer_from_ui(self):
        val = self.timer_entry.get().strip()
        try:
            minutes = int(val)
            if minutes <= 0:
                raise ValueError("must be > 0")
        except Exception:
            messagebox.showerror(
                "Invalid", "Please enter a positive integer for minutes"
            )
            return
        self.start_timer(minutes)

    def start_timer(self, minutes):
        # stop existing timer if running
        self.stop_timer()
        self.current_timer_seconds = minutes * 60
        self.timer_stop_event = threading.Event()
        self.timer_thread = threading.Thread(
            target=self._timer_thread_fn, args=(self.timer_stop_event,), daemon=True
        )
        self.timer_thread.start()
        # record history
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.timer_history.insert(0, f"{now} - {minutes} min")

    def _timer_thread_fn(self, stop_event):
        # Runs in background thread, updates UI via after()
        while self.current_timer_seconds > 0 and not stop_event.is_set():
            mins = self.current_timer_seconds // 60
            secs = self.current_timer_seconds % 60
            # schedule UI update on main thread
            self.after(
                0, lambda m=mins, s=secs: self.timer_label.config(text=f"{m:02}:{s:02}")
            )
            time.sleep(1)
            self.current_timer_seconds -= 1

        if stop_event.is_set():
            # stopped by user
            self.after(0, lambda: self.timer_label.config(text="Timer stopped"))
            return

        # timer finished -> send notification using reminders.notify for consistency
        try:
            reminders.notify(
                f"Study timer finished ({(time.time() - 0) // 60:.0f} minutes). Great job!"
            )
        except Exception:
            # fallback to osascript via subprocess inside reminders module normally
            pass
        self.after(0, lambda: self.timer_label.config(text="Study time finished!"))

    def stop_timer(self):
        if self.timer_stop_event:
            self.timer_stop_event.set()
            self.timer_stop_event = None
        self.current_timer_seconds = 0

    # ---------------- Dashboard ----------------
    def build_dashboard_tab(self, parent):
        """Improved dashboard layout with styled cards."""
        parent.configure(style="TFrame")

        # Header
        header = ttk.Frame(parent, padding=10)
        header.pack(fill="x", padx=12, pady=(12, 8))
        ttk.Label(header, text="📊 Dashboard", font=("Segoe UI", 19, "bold")).pack(
            side="left"
        )
        ttk.Button(
            header,
            text="🔄 Refresh",
            command=self.refresh_dashboard,
            bootstyle="primary",
        ).pack(side="right")

        container = ttk.Frame(parent)
        container.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Stats cards row - simplified without custom colors
        cards_container = ttk.Frame(container)
        cards_container.pack(fill="x", pady=(0, 12))

        cards_fr = ttk.Frame(cards_container)
        cards_fr.pack(anchor="center")

        def _make_card(parent, emoji, title, var_text):
            fr = ttk.Frame(parent, padding=15)
            fr.pack(side="left", padx=8)

            emoji_lbl = ttk.Label(fr, text=emoji, font=("Segoe UI", 31))
            emoji_lbl.pack(anchor="center", pady=(0, 5))

            lbl_title = ttk.Label(fr, text=title, font=("Segoe UI", 15))
            lbl_title.pack(anchor="center")

            lbl_val = ttk.Label(fr, text=var_text, font=("Segoe UI", 29, "bold"))
            lbl_val.pack(anchor="center", pady=(7, 0))

            return fr, lbl_val

        self._card_total_xp_frame, self._card_total_xp_label = _make_card(
            cards_fr, "⭐", "Total XP", "0"
        )
        self._card_notes_frame, self._card_notes_label = _make_card(
            cards_fr, "📝", "Notes Created", "0"
        )
        self._card_badges_frame, self._card_badges_label = _make_card(
            cards_fr, "🏆", "Badges", "—"
        )

        # Two column layout for activity and reminders
        columns = ttk.Frame(container)
        columns.pack(fill="both", expand=True)

        # Left column - Recent activity
        left_frame = ttk.Frame(columns, padding=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 4))

        ttk.Label(
            left_frame, text="📌 Recent Activity", font=("Segoe UI", 17, "bold")
        ).pack(anchor="nw", pady=(0, 10))

        self.lb_activity = tk.Listbox(
            left_frame, height=12, font=("Segoe UI", 15), relief="flat", borderwidth=0
        )
        self.lb_activity.pack(fill="both", expand=True, pady=(0, 5))

        # Right column - Upcoming reminders
        right_frame = ttk.Frame(columns, padding=10)
        right_frame.pack(side="left", fill="both", expand=True, padx=(4, 0))

        ttk.Label(
            right_frame, text="⏰ Upcoming Reminders", font=("Segoe UI", 17, "bold")
        ).pack(anchor="nw", pady=(0, 10))

        self.lb_upcoming = tk.Listbox(
            right_frame, height=12, font=("Segoe UI", 15), relief="flat", borderwidth=0
        )
        self.lb_upcoming.pack(fill="both", expand=True, pady=(0, 4))

        # Status bar at bottom
        status_fr = ttk.Frame(parent)
        status_fr.pack(fill="x", padx=12, pady=(4, 8))
        self.lbl_last_updated = ttk.Label(
            status_fr, text="Last updated: never", font=("Segoe UI", 14)
        )
        self.lbl_last_updated.pack(side="left")
        # shared lightweight status (also used by notes save)
        ttk.Label(status_fr, textvariable=self.status_var, font=("Segoe UI", 14)).pack(
            side="left", padx=14
        )

    def refresh_dashboard(self):
        """Populate dashboard cards and lists using storage + reminders.
        Keep this method fast and resilient (catch exceptions from modules).
        """
        # Update cards from stats
        try:
            st = storage.load_stats()
            total_xp = st.get("total_xp", 0)
            notes_created = st.get("notes_created", 0)
            badges = st.get("badges", []) or []
        except Exception:
            total_xp = 0
            notes_created = 0
            badges = []

        # Update header stats
        try:
            if hasattr(self, "header_stats"):
                self.header_stats.config(
                    text=f"⭐ {total_xp} XP  •  📝 {notes_created} Notes"
                )
        except Exception:
            pass

        # update card labels (use string formatting for thousands)
        try:
            self._card_total_xp_label.config(text=f"{total_xp}")
            self._card_notes_label.config(text=f"{notes_created}")
            if badges:
                # show count + short preview of first 2 badges
                preview = ", ".join(badges[:2]) + (",..." if len(badges) > 2 else "")
                self._card_badges_label.config(text=f"{len(badges)} ({preview})")
            else:
                self._card_badges_label.config(text="—")
        except Exception:
            # widgets not present yet or other UI error; ignore silently
            pass

        # Recent activity: prefer recent notes, then recent timers (if any)
        self.lb_activity.delete(0, tk.END)
        try:
            recent_notes = storage.list_notes(limit=8)
            for n in recent_notes:
                title = n.get("title") or "(untitled)"
                ts = n.get("datetime", "")
                # short timestamp if ISO-like
                short_ts = ts
                try:
                    from datetime import datetime

                    short_ts = datetime.fromisoformat(ts).strftime("%b %d %H:%M")
                except Exception:
                    short_ts = ts[:16]
                self.lb_activity.insert(tk.END, f"Note: {title}  — {short_ts}")
        except Exception as e:
            self.lb_activity.insert(tk.END, f"Could not load recent notes: {e}")

        # Upcoming reminders
        self.lb_upcoming.delete(0, tk.END)
        try:
            jobs = reminders.list_jobs()
            if not jobs:
                self.lb_upcoming.insert(tk.END, "No upcoming reminders")
            else:
                for jid, nxt in jobs[:6]:
                    self.lb_upcoming.insert(tk.END, f"{jid} — next: {nxt}")
        except Exception as e:
            self.lb_upcoming.insert(tk.END, f"Error loading reminders: {e}")

        # update last-updated label
        from datetime import datetime as dt_class

        self.lbl_last_updated.config(
            text=f"Last updated: {dt_class.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def on_closing(self):
        """Clean up and close application properly"""
        logger.info("Application closing - running cleanup...")
        
        try:
            # Save any unsaved changes
            if self.is_modified:
                logger.info("Saving modified note before closing")
                self.save_note_silent()
            
            # Stop autosave timer
            if self.autosave_timer:
                logger.info("Cancelling autosave timer")
                self.after_cancel(self.autosave_timer)
            
            # Stop any running timer thread
            if self.timer_stop_event:
                logger.info("Stopping timer thread")
                self.timer_stop_event.set()
            
            # Stop reminder scheduler
            try:
                reminders.stop_scheduler()
                logger.info("Stopped reminder scheduler")
            except Exception as e:
                logger.warning(f"Could not stop reminder scheduler: {e}")
            
            logger.info("Cleanup completed successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        
        # Close the window
        self.destroy()

    # ---------------- Keyboard Shortcuts & Autosave ----------------
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for common actions"""
        try:
            self.bind(config.SHORTCUTS["save"], lambda e: self.save_note())
            self.bind(config.SHORTCUTS["new"], lambda e: self.new_note())
            self.bind(config.SHORTCUTS["quit"], lambda e: self.quit())
            self.bind(config.SHORTCUTS["refresh"], lambda e: self.refresh_dashboard())
            self.bind(config.SHORTCUTS["undo"], lambda e: self.undo_note())
            self.bind(config.SHORTCUTS["redo"], lambda e: self.redo_note())
            self.bind(config.SHORTCUTS["theme_toggle"], lambda e: self.toggle_theme())
            logger.info("Keyboard shortcuts configured (including undo/redo/theme)")
        except Exception as e:
            logger.error(f"Failed to setup keyboard shortcuts: {e}")

    def start_autosave_timer(self):
        """Start the autosave timer (saves every 3 seconds if modified)"""
        if self.is_modified and hasattr(self, "txt_content"):
            self.save_note_silent()
        # Schedule next check
        self.autosave_timer = self.after(
            config.AUTOSAVE_INTERVAL, self.start_autosave_timer
        )

    def stop_autosave_timer(self):
        """Stop the autosave timer"""
        if self.autosave_timer:
            self.after_cancel(self.autosave_timer)
            self.autosave_timer = None
            logger.info("Autosave timer stopped")

    # ---------------- Theme Toggle ----------------
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        if not TTKBOOTSTRAP_AVAILABLE:
            messagebox.showinfo("Theme", "Theme switching requires ttkbootstrap")
            return

        try:
            if self.current_theme == "light":
                self.style.theme_use("darkly")  # Dark theme
                self.current_theme = "dark"
                logger.info("Switched to dark theme")
                messagebox.showinfo("Theme", "🌙 Dark mode enabled")
            else:
                self.style.theme_use("cosmo")  # Light theme
                self.current_theme = "light"
                logger.info("Switched to light theme")
                messagebox.showinfo("Theme", "☀️ Light mode enabled")
            
            # Refresh all UI elements to apply new theme properly
            self.refresh_notes()
            self.refresh_reminders()
            self.refresh_dashboard()
            
        except Exception as e:
            logger.error(f"Theme toggle failed: {e}")
            messagebox.showerror("Error", f"Could not change theme: {e}")

    # ---------------- PDF Export ----------------
    def export_note_to_pdf(self):
        """Export current note to PDF"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.enums import TA_LEFT
        except ImportError:
            messagebox.showerror(
                "Missing Library",
                "PDF export requires reportlab. Install with:\npip install reportlab",
            )
            return

        title = self.entry_title.get().strip() or "Untitled Note"
        content = self.txt_content.get("1.0", tk.END).strip()

        if not content:
            messagebox.showwarning("Empty Note", "No content to export")
            return

        # Sanitize filename - remove invalid characters
        import re
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
        safe_title = safe_title[:100]  # Limit length

        # Ask for save location
        from tkinter import filedialog

        # Show loading cursor
        self.config(cursor="wait")
        self.update()

        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"{safe_title.replace(' ', '_')}.pdf",
        )

        if not filename:
            return

        try:
            # Create PDF
            doc = SimpleDocTemplate(filename, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()

            # Title
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                textColor="#2c3e50",
                spaceAfter=30,
            )
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.2 * inch))

            # Content
            content_style = ParagraphStyle(
                "CustomBody",
                parent=styles["BodyText"],
                fontSize=12,
                leading=16,
                alignment=TA_LEFT,
            )

            # Split content into paragraphs
            for para in content.split("\n\n"):
                if para.strip():
                    story.append(Paragraph(para.replace("\n", "<br/>"), content_style))
                    story.append(Spacer(1, 0.15 * inch))

            doc.build(story)
            logger.info(f"PDF exported: {filename}")
            messagebox.showinfo("Success", f"Note exported to:\n{filename}")
        except Exception as e:
            logger.error(f"PDF export failed: {e}")
            messagebox.showerror("Export Error", f"Failed to export PDF:\n{e}")
        finally:
            # Restore normal cursor
            self.config(cursor="")


# Simple summarizer (frequency-based, fallback if NLTK not available)
def simple_summarize(text, num_sent=3):
    try:
        from nltk.tokenize import sent_tokenize, word_tokenize
        from nltk.corpus import stopwords

        sents = sent_tokenize(text)
        words = word_tokenize(text.lower())
        stop = set(stopwords.words("english"))
        freq = {}
        for w in words:
            if w.isalpha() and w not in stop:
                freq[w] = freq.get(w, 0) + 1
        ranking = {}
        for i, s in enumerate(sents):
            score = sum(freq.get(w.lower(), 0) for w in s.split())
            ranking[i] = score
        ranked = sorted(ranking.items(), key=lambda x: x[1], reverse=True)
        selected = [sents[i] for i, _ in ranked[:num_sent]]
        return " ".join(selected)
    except Exception:
        # fallback naive summarizer
        pts = text.split(".")
        return ".".join(pts[: min(len(pts), num_sent)]) + (
            "." if len(pts) > num_sent else ""
        )


if __name__ == "__main__":
    logger.info("Starting application...")
    app = App()
    logger.info("Application running")
    app.mainloop()
    logger.info("Application closed")