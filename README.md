# musiccordz

## API

- `GET /` → health check
- `GET /scale/{tonic}/{mode}` → scale object (notes, degrees, relative key, diatonic triads)
  - Example: `GET /scale/C/major`
- `GET /chords?key=C&mode=major` → diatonic triads for the requested key + mode (`major` or `minor`)

## Deployed examples (Render)

- Health:
  - `curl "https://musiccordz-1.onrender.com/"`
- Scale object:
  - `curl "https://musiccordz-1.onrender.com/scale/C/major"`
  - `curl "https://musiccordz-1.onrender.com/scale/A/minor"`
- Diatonic chords:
  - `curl "https://musiccordz-1.onrender.com/chords?key=Bb&mode=major"`