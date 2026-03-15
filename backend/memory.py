from typing import List


# Minimal in-memory history store for early development.
# Later this will be replaced with SQLite/Supabase persistence.

_HISTORY: List[dict] = []


def append_message(message: dict) -> None:
    _HISTORY.append(message)


def get_last_n(n: int = 10) -> List[dict]:
    return _HISTORY[-n:]


def clear_history() -> None:
    _HISTORY.clear()
