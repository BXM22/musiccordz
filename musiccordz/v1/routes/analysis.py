from fastapi import APIRouter, Body, HTTPException

from ...theory import KeyMode, NOTE_TO_SEMITONE, diatonic_triads, normalize_note
from .chord import detect_chords

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("/chord")
def analyze_chord(body: list[str] = Body(...)):
    try:
        possible = detect_chords(body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"input": body, "possible_chords": possible}


def _score_key(chords: list[str], tonic: str, mode: KeyMode) -> float:
    diatonic = set(diatonic_triads(tonic, mode))
    score = 0.0
    for c in chords:
        c = c.strip()
        if not c:
            continue
        if c in diatonic:
            score += 1.0
    return score / max(1, len([c for c in chords if c.strip()]))


@router.post("/key")
def analyze_key(body: list[str] = Body(...)):
    if not body:
        raise HTTPException(status_code=400, detail="Provide a list of chords.")

    candidates: list[dict] = []
    for tonic in ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]:
        for mode in (KeyMode.major, KeyMode.minor):
            try:
                score = _score_key(body, tonic, mode)
            except ValueError:
                continue
            candidates.append({"key": f"{tonic} {mode.value}", "confidence": round(score, 3)})

    candidates.sort(key=lambda x: x["confidence"], reverse=True)
    best = candidates[0] if candidates else {"key": None, "confidence": 0.0}
    return {"input": body, "key": best["key"], "confidence": best["confidence"], "candidates": candidates[:10]}


@router.post("/progression")
def analyze_progression(body: list[str] = Body(...)):
    if not body:
        raise HTTPException(status_code=400, detail="Provide a list of chords.")

    key_result = analyze_key(body)
    key = key_result["key"]
    if not key:
        return {"input": body, "key": None, "roman_numerals": [], "mood": None}

    tonic, mode_str = key.split()
    mode = KeyMode(mode_str)
    triads = diatonic_triads(tonic, mode)
    roman_major = ["I", "ii", "iii", "IV", "V", "vi", "vii°"]
    roman_minor = ["i", "ii°", "III", "iv", "v", "VI", "VII"]
    roman = roman_major if mode == KeyMode.major else roman_minor

    mapping = {triads[i]: roman[i] for i in range(7)}
    roman_out = [mapping.get(c.strip(), "?") for c in body]
    mood = "bright" if mode == KeyMode.major else "dark"

    return {"input": body, "key": key, "roman_numerals": roman_out, "mood": mood}

