#!/usr/bin/env python3
"""
Database Cleanup Utility - Remove duplicate notes and fix counts
"""

import pandas as pd
import os

# Use relative path from script location
script_dir = os.path.dirname(os.path.abspath(__file__))
notes_csv = os.path.join(script_dir, "data", "notes.csv")

print("🧹 Smart Study Assistant - Database Cleanup")
print("=" * 60)
print()

if not os.path.exists(notes_csv):
    print("❌ notes.csv not found!")
    exit(1)

# Load notes
df = pd.read_csv(notes_csv)
print(f"📊 Current database: {len(df)} notes")
print()

# Show duplicates
print("🔍 Checking for duplicates...")
duplicates = df[df.duplicated(subset=['title', 'text'], keep='first')]
if not duplicates.empty:
    print(f"⚠️  Found {len(duplicates)} duplicate notes:")
    for idx, row in duplicates.iterrows():
        print(f"   - ID {row['id']}: '{row['title']}' (duplicate)")
    print()
else:
    print("✅ No duplicates found")
    print()

# Show all notes
print("📄 Current notes in database:")
for idx, row in df.iterrows():
    title = row['title'] if pd.notna(row['title']) else "Untitled"
    print(f"   {row['id']:2d}. {title}")
print()

# Ask user what to do
print("=" * 60)
print("Options:")
print("1. Remove duplicate notes (keep oldest)")
print("2. Remove ALL notes and start fresh")
print("3. Exit without changes")
print()

choice = input("Enter choice (1/2/3): ").strip()

if choice == "1":
    print()
    print("🧹 Removing duplicates...")
    # Keep first occurrence (oldest)
    df_clean = df.drop_duplicates(subset=['title', 'text'], keep='first')
    removed = len(df) - len(df_clean)
    
    if removed > 0:
        # Backup original
        backup_file = notes_csv + ".backup"
        df.to_csv(backup_file, index=False)
        print(f"✅ Backup created: {backup_file}")
        
        # Save cleaned data
        df_clean.to_csv(notes_csv, index=False)
        print(f"✅ Removed {removed} duplicate notes")
        print(f"✅ Database now has {len(df_clean)} unique notes")
    else:
        print("✅ No duplicates to remove")

elif choice == "2":
    print()
    confirm = input("⚠️  Are you sure? This will DELETE ALL NOTES! (yes/no): ").strip().lower()
    if confirm == "yes":
        # Backup original
        backup_file = notes_csv + ".backup"
        df.to_csv(backup_file, index=False)
        print(f"✅ Backup created: {backup_file}")
        
        # Create empty dataframe with headers
        df_empty = pd.DataFrame(columns=['id', 'datetime', 'title', 'text', 'tags', 'xp'])
        df_empty.to_csv(notes_csv, index=False)
        print("✅ All notes removed - database cleared")
    else:
        print("❌ Cancelled - no changes made")

else:
    print()
    print("❌ No changes made")

print()
print("=" * 60)
print("✅ Done! Restart the app to see changes.")
print("=" * 60)
