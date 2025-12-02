#!/usr/bin/env python3
"""
Quick verification that the notes section is working properly
"""

print("🧪 Notes Section Verification")
print("=" * 60)
print()

# Check that the app file exists
import os
app_path = "/Users/ashviksinha/Library/CloudStorage/OneDrive-BENNETTUNIVERSITY/python/vsscode/newproject/main.py"
if os.path.exists(app_path):
    print("✅ main.py exists")
else:
    print("❌ main.py not found")
    exit(1)

# Check that notes data exists
data_path = "/Users/ashviksinha/Library/CloudStorage/OneDrive-BENNETTUNIVERSITY/python/vsscode/newproject/data/notes.csv"
if os.path.exists(data_path):
    print("✅ notes.csv exists")
    
    import pandas as pd
    df = pd.read_csv(data_path)
    print(f"✅ Found {len(df)} notes in database")
    
    # Show sample notes
    if not df.empty:
        print("\nSample notes:")
        for idx, row in df.head(3).iterrows():
            print(f"  - ID: {row['id']}, Title: {row['title']}")
else:
    print("⚠️  notes.csv not found (will be created on first run)")

print()
print("=" * 60)
print("🎯 MANUAL TESTING CHECKLIST:")
print("=" * 60)
print()
print("1. [ ] App starts without errors")
print("2. [ ] Notes list shows all notes on left side")
print("3. [ ] Click a note - it loads in the editor")
print("4. [ ] Type in search box - notes filter instantly")
print("5. [ ] Click 'Delete' button - confirmation appears")
print("6. [ ] Confirm delete - note disappears from list")
print("7. [ ] Click 'Remind' button - dialog appears")
print("8. [ ] Click 'Refresh List' - list updates")
print()
print("=" * 60)
print()
print("✅ If ALL checkboxes pass, the notes section is WORKING!")
print()
