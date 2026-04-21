from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "API is running"}

@app.get("/chords")
def get_chords(key: str):
    return {
        "key": key,
        "chords": ["C", "Dm", "Em", "F", "G", "Am", "Bdim"]
    }