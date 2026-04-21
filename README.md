# musiccordz

## API

- `GET /` → health check
- `GET /scale/{tonic}/{mode}` → scale object (notes, degrees, relative key, diatonic triads)
  - Example: `GET /scale/C/major`
- `GET /chords?key=C&mode=major` → diatonic triads for the requested key + mode (`major` or `minor`)

## API v1 (canonical)

Base path: `/api/v1`

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