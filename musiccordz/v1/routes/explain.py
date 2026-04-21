from fastapi import APIRouter, HTTPException

from ...theory import KeyMode, scale_notes
from .chord import chord_info

router = APIRouter(prefix="/explain", tags=["explain"])


@router.get("/chord/{chord}")
def explain_chord(chord: str):
    try:
        info = chord_info(chord)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {
        "chord": info["normalized"],
        "notes": info["notes"],
        "intervals": info["intervals"],
        "explanation": f'{info["normalized"]} is built from {", ".join(info["intervals"])} above {info["root"]}.',
    }


@router.get("/scale/{root}/{type}")
def explain_scale(root: str, type: str):
    t = type.strip().lower()
    if t not in {"major", "minor"}:
        raise HTTPException(status_code=400, detail="Supported scale types: major, minor")
    mode = KeyMode.major if t == "major" else KeyMode.minor
    try:
        notes = scale_notes(root, mode)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {
        "scale": f"{root} {t}",
        "notes": notes,
        "explanation": f"{root} {t} contains 7 notes used for melody and diatonic harmony.",
    }

