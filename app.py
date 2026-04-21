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


def _prefer_flats(raw_key: str, normalized_key: str) -> bool:
    return ("b" in raw_key.strip()) or (normalized_key in _TYPICAL_FLAT_KEYS)


def _speller(prefer_flats: bool) -> list[str]:
    return _SEMITONE_TO_FLAT_NOTE if prefer_flats else _SEMITONE_TO_SHARP_NOTE


def _scale_degrees(mode: KeyMode) -> list[int]:
    return _MAJOR_SCALE if mode == KeyMode.major else _NATURAL_MINOR_SCALE


def _scale_notes(key: str, mode: KeyMode) -> list[str]:
    raw_key = key.strip()
    root = _normalize_note(key)
    root_semitone = _NOTE_TO_SEMITONE[root]
    spell = _speller(_prefer_flats(raw_key, root))
    return [spell[(root_semitone + d) % 12] for d in _scale_degrees(mode)]


def _degrees_map(notes: list[str]) -> dict[str, str]:
    return {str(i + 1): note for i, note in enumerate(notes)}


def _relative_key_name(key: str, mode: KeyMode) -> dict[str, str]:
    notes = _scale_notes(key, mode)
    if mode == KeyMode.major:
        return {"minor": f"{notes[5]} minor"}
    return {"major": f"{notes[2]} major"}


def _diatonic_triads(key: str, mode: KeyMode) -> list[str]:
    notes = _scale_notes(key, mode)
    if mode == KeyMode.major:
        qualities = ["", "m", "m", "", "", "m", "dim"]
    else:
        qualities = ["m", "dim", "", "m", "m", "", ""]
    return [f"{note}{quality}" for note, quality in zip(notes, qualities, strict=True)]


def _scale_object(tonic: str, mode: KeyMode) -> dict:
    notes = _scale_notes(tonic, mode)
    name = f"{_normalize_note(tonic)} {mode.value.capitalize()}"
    return {
        "name": name,
        "tonic": _normalize_note(tonic),
        "mode": mode.value,
        "notes": notes,
        "degrees": _degrees_map(notes),
        "relative": _relative_key_name(tonic, mode),
        "chords": {"diatonic_triads": _diatonic_triads(tonic, mode)},
    }


@app.get("/")
def home():
    return {"message": "API is running"}


@app.get("/scale/{tonic}/{mode}")
def get_scale(tonic: str, mode: KeyMode):
    try:
        return _scale_object(tonic, mode)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/chords")
def get_chords(key: str, mode: KeyMode = KeyMode.major):
    try:
        chords = _diatonic_triads(key, mode)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {
        "key": key,
        "mode": mode.value,
        "chords": chords,
    }