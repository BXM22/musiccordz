import re

from fastapi import APIRouter, Body, HTTPException

from ...theory import NOTE_TO_SEMITONE, KeyMode, diatonic_triads, normalize_note, scale_notes

router = APIRouter(prefix="/chord", tags=["chord"])

_CHORD_RE = re.compile(
    r"^(?P<root>[A-Ga-g])(?P<accidental>#|b)?(?P<quality>maj|min|dim|aug|m)?(?P<ext>6|7|maj7|m7)?$"
)

_CHORD_FORMULAS: dict[str, tuple[list[int], list[str]]] = {
    "": ([0, 4, 7], ["1", "3", "5"]),
    "m": ([0, 3, 7], ["1", "b3", "5"]),
    "dim": ([0, 3, 6], ["1", "b3", "b5"]),
    "aug": ([0, 4, 8], ["1", "3", "#5"]),
    "6": ([0, 4, 7, 9], ["1", "3", "5", "6"]),
    "m6": ([0, 3, 7, 9], ["1", "b3", "5", "6"]),
    "7": ([0, 4, 7, 10], ["1", "3", "5", "b7"]),
    "m7": ([0, 3, 7, 10], ["1", "b3", "5", "b7"]),
    "maj7": ([0, 4, 7, 11], ["1", "3", "5", "7"]),
}


def _spell_pc(semitone: int) -> str:
    # canonical spelling uses sharps for now
    from ...theory import SEMITONE_TO_SHARP_NOTE

    return SEMITONE_TO_SHARP_NOTE[semitone % 12]


def _parse_chord_symbol(symbol: str) -> dict:
    s = symbol.strip()
    m = _CHORD_RE.match(s)
    if not m:
        raise ValueError('Unsupported chord symbol. Examples: "C", "Am", "G7", "Am7", "Cmaj7".')

    root = normalize_note(f"{m.group('root').upper()}{m.group('accidental') or ''}")
    quality = m.group("quality") or ""
    ext = m.group("ext") or ""

    if quality == "min":
        quality = "m"
    # extension can encode minor 7 even if quality already m
    if ext and quality and ext.startswith("m") and quality != "m":
        # normalize weird combos
        quality = "m"

    if ext == "m7":
        formula_key = "m7"
    elif ext == "maj7":
        formula_key = "maj7"
    elif ext == "7":
        formula_key = "m7" if quality == "m" else "7"
    elif ext == "6":
        formula_key = "m6" if quality == "m" else "6"
    else:
        formula_key = quality

    if formula_key not in _CHORD_FORMULAS:
        raise ValueError("Unsupported chord quality/extension.")

    return {"root": root, "formula_key": formula_key}


def chord_info(symbol: str) -> dict:
    parsed = _parse_chord_symbol(symbol)
    root = parsed["root"]
    formula_key = parsed["formula_key"]
    intervals, interval_names = _CHORD_FORMULAS[formula_key]
    root_semitone = NOTE_TO_SEMITONE[root]
    notes = [_spell_pc(root_semitone + d) for d in intervals]

    normalized = f"{root}{'' if formula_key in ('',) else formula_key}"
    if formula_key == "maj7":
        normalized = f"{root}maj7"
    if formula_key in {"m", "m7", "m6"}:
        # keep conventional minor symbol
        normalized = f"{root}{formula_key}"

    return {
        "chord": symbol,
        "normalized": normalized,
        "root": root,
        "notes": notes,
        "intervals": interval_names,
    }


def _pitch_classes_from_notes(notes: list[str]) -> set[int]:
    pcs: set[int] = set()
    for n in notes:
        n = n.strip()
        if not n:
            continue
        # allow octave notes like C4; strip octave
        m = re.match(r"^([A-Ga-g])(#|b)?", n)
        if not m:
            raise ValueError(f"Invalid note: {n}")
        pc = normalize_note(f"{m.group(1).upper()}{m.group(2) or ''}")
        pcs.add(NOTE_TO_SEMITONE[pc] % 12)
    if not pcs:
        raise ValueError("No notes provided.")
    return pcs


def detect_chords(notes: list[str]) -> list[dict]:
    pcs = _pitch_classes_from_notes(notes)
    results: list[dict] = []
    for root_name, root_semi in NOTE_TO_SEMITONE.items():
        for formula_key, (intervals, interval_names) in _CHORD_FORMULAS.items():
            chord_set = {(root_semi + d) % 12 for d in intervals}
            if pcs.issubset(chord_set):
                size_penalty = (len(chord_set) - len(pcs)) * 0.1
                confidence = max(0.0, 1.0 - size_penalty)
                symbol = f"{root_name}{formula_key}"
                if formula_key == "maj7":
                    symbol = f"{root_name}maj7"
                results.append(
                    {
                        "chord": symbol,
                        "notes": [_spell_pc(root_semi + d) for d in intervals],
                        "intervals": interval_names,
                        "confidence": round(confidence, 3),
                    }
                )
    results.sort(key=lambda r: r["confidence"], reverse=True)
    return results[:10]


@router.get("/{chord}")
def get_chord(chord: str):
    try:
        return chord_info(chord)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/analyze")
def analyze_chord(body: list[str] = Body(...)):
    try:
        possible = detect_chords(body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"input": body, "possible_chords": possible}


@router.get("/{chord}/scales")
def chord_scales(chord: str):
    try:
        info = chord_info(chord)
        pcs = _pitch_classes_from_notes(info["notes"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    compatible: list[dict] = []
    for mode in (KeyMode.major, KeyMode.minor):
        for root in ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]:
            try:
                scale_pcs = {NOTE_TO_SEMITONE[n] % 12 for n in scale_notes(root, mode)}
            except ValueError:
                continue
            if pcs.issubset(scale_pcs):
                compatible.append({"scale": f"{root} {mode.value}"})
    return {"chord": chord, "compatible_scales": compatible[:24]}

