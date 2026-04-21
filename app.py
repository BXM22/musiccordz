from enum import Enum

from fastapi import FastAPI, HTTPException

app = FastAPI()


class KeyMode(str, Enum):
    major = "major"
    minor = "minor"


_NOTE_TO_SEMITONE = {
    "C": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
}
_SEMITONE_TO_SHARP_NOTE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
_SEMITONE_TO_FLAT_NOTE = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
_TYPICAL_FLAT_KEYS = {"F", "Bb", "Eb", "Ab", "Db", "Gb", "Cb"}

_MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
_NATURAL_MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]


def _normalize_note(note: str) -> str:
    n = note.strip()
    if not n:
        raise ValueError("Key cannot be empty.")

    n = n[0].upper() + n[1:]
    if n not in _NOTE_TO_SEMITONE:
        raise ValueError(
            'Invalid key. Use note names like "C", "F#", or "Bb".'
        )
    return n


def _diatonic_triads(key: str, mode: KeyMode) -> list[str]:
    raw_key = key.strip()
    root = _normalize_note(key)
    root_semitone = _NOTE_TO_SEMITONE[root]
    prefer_flats = ("b" in raw_key) or (root in _TYPICAL_FLAT_KEYS)
    spell = _SEMITONE_TO_FLAT_NOTE if prefer_flats else _SEMITONE_TO_SHARP_NOTE

    if mode == KeyMode.major:
        scale = _MAJOR_SCALE
        qualities = ["", "m", "m", "", "", "m", "dim"]
    else:
        scale = _NATURAL_MINOR_SCALE
        qualities = ["m", "dim", "", "m", "m", "", ""]

    triads: list[str] = []
    for degree, quality in zip(scale, qualities, strict=True):
        note = spell[(root_semitone + degree) % 12]
        triads.append(f"{note}{quality}")
    return triads


@app.get("/")
def home():
    return {"message": "API is running"}

@app.get("/chords")
def get_chords(key: str, mode: KeyMode = KeyMode.major):
    try:
        chords = _diatonic_triads(key, mode)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {
        "key": key,
        "mode": mode,
        "chords": chords,
    }