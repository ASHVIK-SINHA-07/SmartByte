# Updated delete_selected_note method - copy this over the old one

def delete_selected_note(self):
    """Delete the currently selected note from the listbox"""
    selection = self.notes_listbox.curselection()
    if not selection:
        messagebox.showwarning("Select Note", "Please select a note to delete")
        return
    
    # Get the selected index
    idx = selection[0]
    
    # Check if it's a valid note
    if not self.filtered_notes or idx >= len(self.filtered_notes):
        messagebox.showwarning("Select Note", "No valid note selected")
        return
    
    # Get the note to delete
    note = self.filtered_notes[idx]
    nid = note.get("id")
    
    logger.info(f"Deleting note ID: {nid}, Title: {note.get('title', 'Untitled')}")
    
    # CRITICAL: Clear the editor fields BEFORE showing the confirmation dialog
    self.entry_title.delete(0, tk.END)
    self.txt_content.delete("1.0", tk.END)
    self.entry_tags.delete(0, tk.END)
    
    # Reset modification flag to prevent autosave
    self.is_modified = False
    if hasattr(self, "autosave_indicator"):
        self.autosave_indicator.show_saved()
    
    logger.info("Editor cleared before deletion")

    # Confirm deletion
    ok = messagebox.askyesno(
        "Delete Note", 
        f"Delete '{note.get('title', 'Untitled')}'?"
    )
    if not ok:
        # Reload the note if user cancels
        self.entry_title.insert(0, note.get("title", ""))
        self.txt_content.insert(tk.END, note.get("text", ""))
        self.entry_tags.insert(0, note.get("tags", ""))
        return

    try:
        removed = storage.delete_note(nid)
    except Exception as e:
        logger.error(f"Exception during delete: {e}")
        messagebox.showerror("Error", f"Failed to delete: {e}")
        return

    if removed:
        self.status_var.set("✓ Note deleted")
        self.after(2500, lambda: self.status_var.set(""))
        self.refresh_notes()
        self.refresh_dashboard()
    else:
        messagebox.showerror("Error", "Could not delete note")
