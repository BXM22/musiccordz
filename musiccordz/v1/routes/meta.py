from fastapi import APIRouter

from ... import __version__

router = APIRouter()

_SUPPORTED_SCALES = ["major", "minor"]
_SUPPORTED_CHORDS = [
    "C",
    "Am",
    "G7",
    "Am7",
    "Cmaj7",
    "Ddim",
    "Faug",
]


@router.get("/health")
def health():
    return {"status": "ok", "version": __version__}


@router.get("/meta")
def meta():
    return {
        "version": __version__,
        "limits": {"max_notes": 128, "max_operations": 32},
        "supported_scales": _SUPPORTED_SCALES,
        "supported_chords_examples": _SUPPORTED_CHORDS,
    }

