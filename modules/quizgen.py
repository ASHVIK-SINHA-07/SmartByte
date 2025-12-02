# modules/quizgen.py
"""
Quiz generator for Smart Study Assistant.

Public API:
- generate_quiz(max_q=5) -> list of {"question": ..., "answer": ...}
- extract_keywords(text, n=3) -> list of keywords
"""

import random

# try to use nltk when available, but fall back to a safe tokenizer
try:
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    NLTK_AVAILABLE = True
except Exception:
    NLTK_AVAILABLE = False

# small fallback tokenizer/stoplist
FALLBACK_STOP = {
    "the","and","is","in","it","of","to","a","an","that","this","for","on","with","as","are","was","were"
}

def _tokenize_words(text):
    """Return list of lowercase alpha words."""
    if NLTK_AVAILABLE:
        try:
            return [w.lower() for w in word_tokenize(text) if w.isalpha()]
        except Exception:
            # fallback to simple split
            pass
    # simple fallback
    return [w.lower() for w in text.split() if w.isalpha()]

def extract_keywords(text, n=3):
    """
    Return up to `n` keywords from `text` using frequency heuristic.
    This is intentionally simple and robust if NLTK is not available.
    """
    words = _tokenize_words(text.lower())
    if NLTK_AVAILABLE:
        try:
            stop = set(stopwords.words("english"))
        except Exception:
            stop = FALLBACK_STOP
    else:
        stop = FALLBACK_STOP

    freq = {}
    for w in words:
        if w in stop:
            continue
        freq[w] = freq.get(w, 0) + 1

    # sort by frequency then alphabetically for determinism
    items = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
    return [k for k, _ in items][:n]

def _make_question_from_text(note_text, keyword):
    """
    Make a simple cloze-style question by replacing the first occurrence of keyword.
    """
    if not keyword:
        return None
    # replace only the first occurrence (case-insensitive)
    import re
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    question = pattern.sub("_____", note_text, count=1)
    return question

def generate_quiz(max_q=5):
    """
    Build up to max_q questions from notes stored via storage.list_notes().
    Returns a list of dicts: [{"question": "...", "answer": "..."}, ...]
    """
    try:
        from . import storage
    except Exception as e:
        # If storage can't be imported, return empty list
        print("quizgen: couldn't import storage:", e)
        return []

    notes = storage.list_notes(limit=200)
    if not notes:
        return []

    random.shuffle(notes)
    questions = []
    for note in notes:
        text = note.get("text", "") or ""
        if len(text.strip()) < 10:
            continue
        keys = extract_keywords(text, n=2)
        if not keys:
            continue
        keyword = keys[0]
        q_text = _make_question_from_text(text, keyword)
        if not q_text:
            continue
        questions.append({"question": q_text.strip(), "answer": keyword.strip()})
        if len(questions) >= max_q:
            break
    return questions