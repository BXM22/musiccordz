from fastapi import APIRouter, HTTPException

from ...theory import KeyMode, diatonic_triads, degrees_map, scale_notes

router = APIRouter(prefix="/scale", tags=["scale"])

_SUPPORTED_SCALE_TYPES = {"major": KeyMode.major, "minor": KeyMode.minor}


def _scale_intervals(mode: KeyMode) -> list[int]:
    return [0, 2, 4, 5, 7, 9, 11] if mode == KeyMode.major else [0, 2, 3, 5, 7, 8, 10]


def _scale_payload(root: str, mode: KeyMode) -> dict:
    notes = scale_notes(root, mode)
    degrees = degrees_map(notes)
    intervals = _scale_intervals(mode)
    payload: dict = {
        "name": f"{root.strip().capitalize()} {mode.value.capitalize()}",
        "notes": notes,
        "intervals": intervals,
        "degrees": degrees,
        "chords": {"diatonic": diatonic_triads(root, mode)},
    }
    if mode == KeyMode.major:
        payload["relative_minor"] = f"{notes[5]} minor"
    else:
        payload["relative_major"] = f"{notes[2]} major"
    return payload


@router.get("")
def list_scale_types():
    return {"scale_types": sorted(_SUPPORTED_SCALE_TYPES.keys())}


@router.get("/{root}/{type}")
def get_scale(root: str, type: str):
    t = type.strip().lower()
    if t not in _SUPPORTED_SCALE_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported scale type: {type}")
    try:
        return _scale_payload(root, _SUPPORTED_SCALE_TYPES[t])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/{root}/{type}/chords")
def get_scale_chords(root: str, type: str):
    t = type.strip().lower()
    if t not in _SUPPORTED_SCALE_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported scale type: {type}")
    try:
        mode = _SUPPORTED_SCALE_TYPES[t]
        return {"root": root, "type": t, "chords": {"diatonic": diatonic_triads(root, mode)}}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

