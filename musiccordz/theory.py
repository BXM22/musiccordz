from __future__ import annotations

from enum import Enum


class KeyMode(str, Enum):
    major = "major"
    minor = "minor"


NOTE_TO_SEMITONE: dict[str, int] = {
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

SEMITONE_TO_SHARP_NOTE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
SEMITONE_TO_FLAT_NOTE = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
TYPICAL_FLAT_KEYS = {"F", "Bb", "Eb", "Ab", "Db", "Gb", "Cb"}

MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
NATURAL_MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]


def normalize_note(note: str) -> str:
    n = note.strip()
    if not n:
        raise ValueError("Key cannot be empty.")

    n = n[0].upper() + n[1:]
    if n not in NOTE_TO_SEMITONE:
        raise ValueError('Invalid key. Use note names like "C", "F#", or "Bb".')
    return n


def prefer_flats(raw_key: str, normalized_key: str) -> bool:
    return ("b" in raw_key.strip()) or (normalized_key in TYPICAL_FLAT_KEYS)


def speller(prefer_flats_flag: bool) -> list[str]:
    return SEMITONE_TO_FLAT_NOTE if prefer_flats_flag else SEMITONE_TO_SHARP_NOTE


def scale_degrees(mode: KeyMode) -> list[int]:
    return MAJOR_SCALE if mode == KeyMode.major else NATURAL_MINOR_SCALE


def scale_notes(key: str, mode: KeyMode) -> list[str]:
    raw_key = key.strip()
    root = normalize_note(key)
    root_semitone = NOTE_TO_SEMITONE[root]
    spell = speller(prefer_flats(raw_key, root))
    return [spell[(root_semitone + d) % 12] for d in scale_degrees(mode)]


def degrees_map(notes: list[str]) -> dict[str, str]:
    return {str(i + 1): note for i, note in enumerate(notes)}


def relative_key_name(key: str, mode: KeyMode) -> dict[str, str]:
    notes = scale_notes(key, mode)
    if mode == KeyMode.major:
        return {"minor": f"{notes[5]} minor"}
    return {"major": f"{notes[2]} major"}


def diatonic_triads(key: str, mode: KeyMode) -> list[str]:
    notes = scale_notes(key, mode)
    if mode == KeyMode.major:
        qualities = ["", "m", "m", "", "", "m", "dim"]
    else:
        qualities = ["m", "dim", "", "m", "m", "", ""]
    return [f"{note}{quality}" for note, quality in zip(notes, qualities, strict=True)]


def scale_object(tonic: str, mode: KeyMode) -> dict[str, object]:
    notes = scale_notes(tonic, mode)
    tonic_norm = normalize_note(tonic)
    name = f"{tonic_norm} {mode.value.capitalize()}"

    obj: dict[str, object] = {
        "name": name,
        "notes": notes,
        "degrees": degrees_map(notes),
        "chords": {"diatonic": diatonic_triads(tonic, mode)},
    }

    relative = relative_key_name(tonic, mode)
    if mode == KeyMode.major:
        obj["relative_minor"] = relative["minor"]
    else:
        obj["relative_major"] = relative["major"]

    return obj

