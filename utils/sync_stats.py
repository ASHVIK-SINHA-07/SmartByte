#!/usr/bin/env python3
"""
Sync Stats - Recalculate stats.json from actual notes.csv data
Use this when stats get out of sync with the database
"""

import pandas as pd
import json
import os

# Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
NOTES_CSV = os.path.join(DATA_DIR, "notes.csv")
STATS_JSON = os.path.join(DATA_DIR, "stats.json")


def sync_stats():
    """Recalculate stats from notes.csv and update stats.json"""
    
    print("🔄 Syncing stats from database...")
    print()
    
    # Load current notes
    try:
        df = pd.read_csv(NOTES_CSV)
    except Exception as e:
        print(f"❌ Error reading notes.csv: {e}")
        return
    
    # Calculate real stats
    if df.empty:
        total_xp = 0
        notes_count = 0
        print("📊 Database is empty")
    else:
        # Count notes
        notes_count = len(df)
        
        # Sum XP (handle NaN)
        if "xp" in df.columns:
            df["xp"] = df["xp"].fillna(0)
            total_xp = int(df["xp"].sum())
        else:
            total_xp = 0
        
        print(f"📊 Found {notes_count} notes in database")
        print(f"⭐ Total XP: {total_xp}")
    
    print()
    
    # Load current stats file
    try:
        with open(STATS_JSON, "r") as f:
            old_stats = json.load(f)
        print("📋 Current stats.json:")
        print(f"   Notes: {old_stats.get('notes_created', 0)}")
        print(f"   XP: {old_stats.get('total_xp', 0)}")
    except Exception:
        old_stats = {}
        print("📋 No stats.json found")
    
    print()
    
    # Create new stats
    new_stats = {
        "total_xp": total_xp,
        "notes_created": notes_count
    }
    
    # Preserve badges if they exist
    if "badges" in old_stats:
        new_stats["badges"] = old_stats["badges"]
    
    # Save updated stats
    try:
        with open(STATS_JSON, "w") as f:
            json.dump(new_stats, f, indent=2)
        print("✅ Stats synced successfully!")
        print()
        print("📋 New stats.json:")
        print(f"   Notes: {new_stats['notes_created']}")
        print(f"   XP: {new_stats['total_xp']}")
    except Exception as e:
        print(f"❌ Error saving stats: {e}")
        return
    
    # Show note details if any exist
    if not df.empty and notes_count <= 10:
        print()
        print("📝 Current notes:")
        for idx, row in df.iterrows():
            title = row.get("title", "(untitled)")[:30]
            xp = row.get("xp", 0)
            print(f"   [{row['id']}] {title} ({xp} XP)")


if __name__ == "__main__":
    sync_stats()
