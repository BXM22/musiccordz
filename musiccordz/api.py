from fastapi import FastAPI, HTTPException

from .theory import KeyMode, diatonic_triads, scale_object


app = FastAPI()


@app.get("/")
def home():
    return {"message": "API is running"}


@app.get("/scale/{tonic}/{mode}")
def get_scale(tonic: str, mode: KeyMode):
    try:
        return scale_object(tonic, mode)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/chords")
def get_chords(key: str, mode: KeyMode = KeyMode.major):
    try:
        chords = diatonic_triads(key, mode)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {
        "key": key,
        "mode": mode.value,
        "chords": chords,
    }

