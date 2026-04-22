# musiccordz

## API

- `GET /` → health check
- `GET /scale/{tonic}/{mode}` → scale object (notes, degrees, relative key, diatonic triads)
  - Example: `GET /scale/C/major`
- `GET /chords?key=C&mode=major` → diatonic triads for the requested key + mode (`major` or `minor`)

## API v1 (canonical)

Base path: `/api/v1`

- **Authentication**: none (no API key / OAuth in v1)
- **OpenAPI**: `GET /api/v1/openapi.json` (useful for `/docs` / client generation)

- **Health/meta**
  - `GET /api/v1/health`
  - `GET /api/v1/meta`
- **Notes**
  - `GET /api/v1/note/C4`
  - `GET /api/v1/note/C4/midi`
  - `GET /api/v1/note/midi/60`
- **Intervals**
  - `GET /api/v1/interval?from=C&to=E`
- **Scales**
  - `GET /api/v1/scale/C/major`
  - `GET /api/v1/scale`
  - `GET /api/v1/scale/C/major/chords`
- **Chords**
  - `GET /api/v1/chord/Am7`
  - `POST /api/v1/chord/analyze`
- **Analysis**
  - `POST /api/v1/analyze/chord`
  - `POST /api/v1/analyze/key`
  - `POST /api/v1/analyze/progression`
- **Progressions**
  - `GET /api/v1/progression?key=C%20major&style=pop`
  - `POST /api/v1/progression/analyze`
- **Transforms**
  - `POST /api/v1/transpose`
  - `POST /api/v1/transform`
- **Explain**
  - `GET /api/v1/explain/chord/Am7`
  - `GET /api/v1/explain/scale/C/major`

## API documentation (v1)

### Health / Meta

#### `GET /api/v1/health`

Response:

```json
{ "status": "ok", "version": "0.1.0" }
```

#### `GET /api/v1/meta`

Response (shape may expand over time):

```json
{
  "version": "0.1.0",
  "limits": { "max_notes": 128, "max_operations": 32 },
  "supported_scales": ["major", "minor"],
  "supported_chords_examples": ["C", "Am", "G7", "Am7", "Cmaj7", "Ddim", "Faug"]
}
```

### Notes

Notes endpoints expect octave notes like `C4`, `Bb3`, `F#5`.

#### `GET /api/v1/note/{note}`

Example:

```bash
curl "http://127.0.0.1:8000/api/v1/note/C4"
```

Response:

```json
{
  "note": "C4",
  "frequency": 261.625565,
  "midi": 60,
  "pitch_class": "C",
  "pitch_class_semitone": 0
}
```

#### `GET /api/v1/note/{note}/midi`

Response:

```json
{ "note": "C4", "midi": 60 }
```

#### `GET /api/v1/note/midi/{number}`

Response:

```json
{ "midi": 60, "note": "C4" }
```

### Intervals

#### `GET /api/v1/interval?from=...&to=...`

- **Query params**
  - `from`: required (pitch class like `C` or octave note like `C4`)
  - `to`: required (pitch class like `E` or octave note like `E4`)

Example:

```bash
curl "http://127.0.0.1:8000/api/v1/interval?from=C&to=E"
```

Response:

```json
{ "from": "C", "to": "E", "semitones": 4, "distance": "major 3rd" }
```

### Scales

Scale endpoints expect pitch classes (`C`, `Bb`, `F#`).

#### `GET /api/v1/scale`

Response:

```json
{ "scale_types": ["major", "minor"] }
```

#### `GET /api/v1/scale/{root}/{type}`

Example:

```bash
curl "http://127.0.0.1:8000/api/v1/scale/C/major"
```

Response:

```json
{
  "name": "C Major",
  "notes": ["C", "D", "E", "F", "G", "A", "B"],
  "intervals": [0, 2, 4, 5, 7, 9, 11],
  "degrees": { "1": "C", "2": "D", "3": "E", "4": "F", "5": "G", "6": "A", "7": "B" },
  "chords": { "diatonic": ["C", "Dm", "Em", "F", "G", "Am", "Bdim"] },
  "relative_minor": "A minor"
}
```

#### `GET /api/v1/scale/{root}/{type}/chords`

Response:

```json
{ "root": "C", "type": "major", "chords": { "diatonic": ["C", "Dm", "Em", "F", "G", "Am", "Bdim"] } }
```

### Chords

Chord endpoints accept symbols like `C`, `Am`, `G7`, `Am7`, `Cmaj7`.

#### `GET /api/v1/chord/{chord}`

Example:

```bash
curl "http://127.0.0.1:8000/api/v1/chord/Am7"
```

Response:

```json
{ "chord": "Am7", "normalized": "Am7", "root": "A", "notes": ["A", "C", "E", "G"], "intervals": ["1", "b3", "5", "b7"] }
```

#### `POST /api/v1/chord/analyze`

Request body: JSON array of notes (pitch classes or octave notes).

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chord/analyze" \\
  -H "content-type: application/json" \\
  -d '["C","E","G"]'
```

Response (truncated):

```json
{
  "input": ["C", "E", "G"],
  "possible_chords": [
    { "chord": "C", "confidence": 1.0 }
  ]
}
```

#### `GET /api/v1/chord/{chord}/scales`

Returns scales that contain the chord’s pitch classes.

### Analysis

#### `POST /api/v1/analyze/chord`

Same behavior as `/api/v1/chord/analyze` (alias).

#### `POST /api/v1/analyze/key`

Input: list of chord symbols.

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analyze/key" \\
  -H "content-type: application/json" \\
  -d '["C","G","Am","F"]'
```

Response (truncated):

```json
{ "key": "C major", "confidence": 1.0 }
```

#### `POST /api/v1/analyze/progression`

Input: list of chord symbols. Output includes key + roman numerals (diatonic only in v1).

### Progressions

#### `GET /api/v1/progression?key=...&style=pop`

- `key`: required (e.g. `C major`, `A minor`)\n+- `style`: optional (v1 supports `pop` only)

#### `POST /api/v1/progression/analyze`

Input: list of chord symbols (alias of progression analysis).

### Transforms

#### `POST /api/v1/transpose`

Body:

```json
{ "notes": ["C4", "E4", "G4"], "semitones": 2 }
```

#### `POST /api/v1/transform`

Body:

```json
{ "input": ["C", "E", "G"], "operations": ["transpose:+2"] }
```

### Explain

- `GET /api/v1/explain/chord/{chord}`
- `GET /api/v1/explain/scale/{root}/{type}`

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m uvicorn app:app --reload
```

Then try:

```bash
curl "http://127.0.0.1:8000/api/v1/health"
curl "http://127.0.0.1:8000/api/v1/scale/C/major"
curl "http://127.0.0.1:8000/api/v1/chord/Am7"
```

## Deployed examples (Render)

- Health:
  - `curl "https://musiccordz-1.onrender.com/"`
- Scale object:
  - `curl "https://musiccordz-1.onrender.com/scale/C/major"`
  - `curl "https://musiccordz-1.onrender.com/scale/A/minor"`
- Diatonic chords:
  - `curl "https://musiccordz-1.onrender.com/chords?key=Bb&mode=major"`

### v1 curl examples (Render)

- OpenAPI:
  - `curl "https://musiccordz-1.onrender.com/api/v1/openapi.json"`
- Scale:
  - `curl "https://musiccordz-1.onrender.com/api/v1/scale/C/major"`
- Chord:
  - `curl "https://musiccordz-1.onrender.com/api/v1/chord/Am7"`