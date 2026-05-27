import json
import os
import logging

from config import PROGRESS_FILE

log = logging.getLogger(__name__)


def save_progress(data, completed_categories):
    state = {
        "books": data,
        "completed_categories": completed_categories,
    }
    with open(PROGRESS_FILE, "w") as f:
        json.dump(state, f)
    log.info(f"Progress saved ({len(completed_categories)} categories, {len(data)} books)")


def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        return [], []
    with open(PROGRESS_FILE) as f:
        state = json.load(f)
    books = state.get("books", [])
    completed = state.get("completed_categories", [])
    log.info(f"Resuming from checkpoint ({len(completed)} categories, {len(books)} books)")
    return books, completed


def clear_progress():
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
