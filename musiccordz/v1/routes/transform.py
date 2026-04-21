import re

from fastapi import APIRouter, Body, HTTPException

from ...theory import NOTE_TO_SEMITONE, SEMITONE_TO_SHARP_NOTE, normalize_note

router = APIRouter(tags=["transform"])

_NOTE_PREFIX_RE = re.compile(r"^([A-Ga-g])(#|b)?")
_OCTAVE_RE = re.compile(r"^([A-Ga-g])(#|b)?(-?\d+)$")


def _parse_pc(note: str) -> str:
    m = _NOTE_PREFIX_RE.match(note.strip())
    if not m:
        raise ValueError(f"Invalid note: {note}")
    return normalize_note(f"{m.group(1).upper()}{m.group(2) or ''}")


def _transpose_note(note: str, semitones: int) -> str:
    s = note.strip()
    m_oct = _OCTAVE_RE.match(s)
    if m_oct:
        pc = normalize_note(f"{m_oct.group(1).upper()}{m_oct.group(2) or ''}")
        octave = int(m_oct.group(3))
        midi = (octave + 1) * 12 + NOTE_TO_SEMITONE[pc]
        midi2 = midi + semitones
        if midi2 < 0 or midi2 > 127:
            raise ValueError("Transpose moved note outside MIDI range 0..127.")
        octave2 = (midi2 // 12) - 1
        pc2 = SEMITONE_TO_SHARP_NOTE[midi2 % 12]
        return f"{pc2}{octave2}"

    pc = _parse_pc(s)
    semi = (NOTE_TO_SEMITONE[pc] + semitones) % 12
    return SEMITONE_TO_SHARP_NOTE[semi]


def _invert_notes(notes: list[str]) -> list[str]:
    if not notes:
        raise ValueError("No notes provided.")
    axis_pc = _parse_pc(notes[0])
    axis = NOTE_TO_SEMITONE[axis_pc] % 12
    out: list[str] = []
    for n in notes:
        pc = _parse_pc(n)
        x = NOTE_TO_SEMITONE[pc] % 12
        inv = (2 * axis - x) % 12
        out.append(SEMITONE_TO_SHARP_NOTE[inv])
    return out


@router.post("/transpose")
def transpose(body: dict = Body(...)):
    notes = body.get("notes")
    semitones = body.get("semitones")
    if not isinstance(notes, list) or not isinstance(semitones, int):
        raise HTTPException(status_code=400, detail='Body must be {"notes":[...], "semitones": int}.')
    try:
        return {"input": notes, "semitones": semitones, "output": [_transpose_note(n, semitones) for n in notes]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/transform")
def transform(body: dict = Body(...)):
    data = body.get("input")
    operations = body.get("operations")
    if not isinstance(data, list) or not isinstance(operations, list):
        raise HTTPException(status_code=400, detail='Body must be {"input":[...], "operations":[...] }.')

    out = list(data)
    try:
        for op in operations:
            if not isinstance(op, str):
                raise ValueError("Operation must be a string.")
            if op.startswith("transpose:"):
                n = int(op.split(":", 1)[1])
                out = [_transpose_note(x, n) for x in out]
            elif op == "invert":
                out = _invert_notes(out)
            elif op == "normalize":
                out = [SEMITONE_TO_SHARP_NOTE[NOTE_TO_SEMITONE[_parse_pc(x)] % 12] for x in out]
            else:
                raise ValueError(f"Unsupported operation: {op}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {"input": data, "operations": operations, "output": out}

