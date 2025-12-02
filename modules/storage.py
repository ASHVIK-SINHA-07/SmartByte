import os, json, pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
NOTES_CSV = os.path.join(DATA_DIR, "notes.csv")
STATS_JSON = os.path.join(DATA_DIR, "stats.json")


def ensure_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(NOTES_CSV):
        pd.DataFrame(columns=["id", "datetime", "title", "text", "tags", "xp"]).to_csv(
            NOTES_CSV, index=False
        )
    if not os.path.exists(STATS_JSON):
        with open(STATS_JSON, "w") as f:
            json.dump({"total_xp": 0, "notes_created": 0}, f)


def save_note(title, text, tags="", xp=0):
    ensure_files()
    df = pd.read_csv(NOTES_CSV)
    nid = 1 if df.empty else int(df["id"].max()) + 1
    new = {
        "id": nid,
        "datetime": pd.Timestamp.now().isoformat(),
        "title": title,
        "text": text,
        "tags": tags,
        "xp": xp,
    }
    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
    df.to_csv(NOTES_CSV, index=False)
    stats = load_stats()
    stats["total_xp"] += xp
    stats["notes_created"] += 1
    save_stats(stats)
    return nid


def update_note(note_id, title, text, tags="", xp=0):
    """Update an existing note. Returns True if successful, False if note not found."""
    ensure_files()
    df = pd.read_csv(NOTES_CSV)
    
    if df.empty or note_id not in df["id"].values:
        return False
    
    # Update the note
    df.loc[df["id"] == note_id, "title"] = title
    df.loc[df["id"] == note_id, "text"] = text
    df.loc[df["id"] == note_id, "tags"] = tags
    df.loc[df["id"] == note_id, "datetime"] = pd.Timestamp.now().isoformat()
    # Don't update XP for edits - keeps original XP
    
    df.to_csv(NOTES_CSV, index=False)
    return True


def list_notes(limit=50):
    ensure_files()
    df = pd.read_csv(NOTES_CSV)
    if df.empty:
        return []

    # Fix NaN values in tags column
    if "tags" in df.columns:
        df["tags"] = df["tags"].fillna("")

    # Fix NaN values in other string columns
    for col in ["title", "text"]:
        if col in df.columns:
            df[col] = df[col].fillna("")

    df = df.sort_values("datetime", ascending=False).head(limit)
    return df.to_dict(orient="records")


def load_stats():
    with open(STATS_JSON, "r") as f:
        return json.load(f)


def save_stats(obj):
    ensure_files()
    with open(STATS_JSON, "w") as f:
        json.dump(obj, f, indent=2)


def delete_note(note_id):
    """Delete a note by id (int or string). Returns True if deleted, False otherwise.
    Updates stats.total_xp (subtracts note xp if present) and notes_created.
    """
    ensure_files()
    try:
        import pandas as pd
    except Exception:
        # pandas is required for storage operations; if unavailable, fail gracefully
        return False

    # load existing notes
    df = pd.read_csv(NOTES_CSV)
    if df.empty:
        return False

    # normalize id
    try:
        nid = int(note_id)
    except Exception:
        return False

    if nid not in df["id"].values:
        return False

    # preserve xp value to update stats
    try:
        row = df[df["id"] == nid].iloc[0]
        xp = int(row.get("xp", 0) or 0)
    except Exception:
        xp = 0

    # remove the note and save
    df = df[df["id"] != nid]
    df.to_csv(NOTES_CSV, index=False)

    # update stats
    stats = load_stats()
    stats["total_xp"] = max(0, stats.get("total_xp", 0) - xp)
    stats["notes_created"] = max(0, stats.get("notes_created", 0) - 1)
    save_stats(stats)

    return True
