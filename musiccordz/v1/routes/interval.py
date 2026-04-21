from fastapi import APIRouter, HTTPException

from ...theory import NOTE_TO_SEMITONE, normalize_note
from .note import _parse_note  # reuse parsing rules

router = APIRouter(tags=["interval"])

_INTERVAL_NAMES = {
    0: "unison",
    1: "minor 2nd",
    2: "major 2nd",
    3: "minor 3rd",
    4: "major 3rd",
    5: "perfect 4th",
    6: "tritone",
    7: "perfect 5th",
    8: "minor 6th",
    9: "major 6th",
    10: "minor 7th",
    11: "major 7th",
    12: "octave",
}


def _note_to_semitone_value(n: str) -> int:
    parsed = _parse_note(n)
    pc = normalize_note(parsed["pitch_class"])
    octave = parsed["octave"]
    if octave is None:
        return NOTE_TO_SEMITONE[pc]
    return (octave + 1) * 12 + NOTE_TO_SEMITONE[pc]


@router.get("/interval")
def interval(from_: str, to: str):  # `from` is reserved, FastAPI uses from_ query param
    try:
        a = _note_to_semitone_value(from_)
        b = _note_to_semitone_value(to)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    semitones = b - a
    semitones_abs = abs(semitones)
    semitones_mod12 = semitones_abs % 12
    name = _INTERVAL_NAMES.get(semitones_abs) or _INTERVAL_NAMES.get(semitones_mod12, "interval")

    return {
        "from": from_,
        "to": to,
        "semitones": semitones,
        "distance": name,
    }

