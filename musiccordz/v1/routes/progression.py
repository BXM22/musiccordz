from fastapi import APIRouter, Body, HTTPException

from ...theory import KeyMode, diatonic_triads
from .analysis import analyze_progression

router = APIRouter(prefix="/progression", tags=["progression"])


@router.get("")
def generate_progressions(key: str, style: str = "pop"):
    style = style.strip().lower()
    if style != "pop":
        raise HTTPException(status_code=400, detail="Only style=pop is supported in v1.")

    parts = key.strip().split()
    tonic = parts[0]
    mode = KeyMode.major
    if len(parts) > 1:
        mode = KeyMode(parts[1].lower())

    try:
        triads = diatonic_triads(tonic, mode)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    # pop staples
    I, ii, iii, IV, V, vi, vii = triads
    progressions = [
        [I, V, vi, IV],
        [I, vi, IV, V],
        [vi, IV, I, V],
        [I, IV, V, I],
    ]
    return {"key": f"{tonic} {mode.value}", "style": style, "progressions": progressions}


@router.post("/analyze")
def analyze_progressions(body: list[str] = Body(...)):
    try:
        return analyze_progression(body)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

