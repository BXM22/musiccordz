import math
import re

from fastapi import APIRouter, HTTPException

from ...theory import normalize_note

router = APIRouter(prefix="/note", tags=["note"])

_NOTE_RE = re.compile(r"^(?P<pc>[A-Ga-g])(?P<accidental>#|b)?(?P<octave>-?\d+)?$")
_PC_TO_SEMITONE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_SEMITONE_TO_SHARP_PC = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def _parse_note(note: str) -> dict:
    m = _NOTE_RE.match(note.strip())
    if not m:
        raise ValueError('Invalid note. Examples: "C4", "Bb3", "F#5".')
    pc = m.group("pc").upper()
    accidental = m.group("accidental") or ""
    octave_raw = m.group("octave")
    octave = int(octave_raw) if octave_raw is not None else None
    pitch_class = normalize_note(f"{pc}{accidental}")
    return {"pitch_class": pitch_class, "octave": octave}


def _note_to_midi(note: str) -> int:
    parsed = _parse_note(note)
    if parsed["octave"] is None:
        raise ValueError('Missing octave. Example: "C4".')

    pc = parsed["pitch_class"]
    octave: int = parsed["octave"]
    semitone = _PC_TO_SEMITONE[pc[0]] + (1 if pc.endswith("#") else 0) + (-1 if pc.endswith("b") else 0)
    semitone %= 12
    return (octave + 1) * 12 + semitone


def _midi_to_note(midi: int) -> str:
    if midi < 0 or midi > 127:
        raise ValueError("MIDI must be in range 0..127.")
    octave = (midi // 12) - 1
    pc = _SEMITONE_TO_SHARP_PC[midi % 12]
    return f"{pc}{octave}"


def _midi_to_frequency(midi: int) -> float:
    return 440.0 * (2 ** ((midi - 69) / 12))


@router.get("/midi/{number}")
def midi_to_note(number: int):
    try:
        note = _midi_to_note(number)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"midi": number, "note": note}


@router.get("/{note}/midi")
def note_to_midi(note: str):
    try:
        midi = _note_to_midi(note)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"note": note, "midi": midi}


@router.get("/{note}")
def note_info(note: str):
    try:
        midi = _note_to_midi(note)
        parsed = _parse_note(note)
        pc = parsed["pitch_class"]
        pitch_class = normalize_note(pc)
        freq = _midi_to_frequency(midi)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {
        "note": note,
        "frequency": round(freq, 6),
        "midi": midi,
        "pitch_class": pitch_class,
        "pitch_class_semitone": midi % 12,
    }

