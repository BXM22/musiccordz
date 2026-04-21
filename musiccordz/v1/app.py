from fastapi import FastAPI

from .routes.analysis import router as analysis_router
from .routes.chord import router as chord_router
from .routes.explain import router as explain_router
from .routes.interval import router as interval_router
from .routes.meta import router as meta_router
from .routes.note import router as note_router
from .routes.progression import router as progression_router
from .routes.scale import router as scale_router
from .routes.transform import router as transform_router

v1_app = FastAPI(title="musiccordz API", version="1.0.0")

v1_app.include_router(meta_router)
v1_app.include_router(note_router)
v1_app.include_router(interval_router)
v1_app.include_router(scale_router)
v1_app.include_router(chord_router)
v1_app.include_router(analysis_router)
v1_app.include_router(progression_router)
v1_app.include_router(transform_router)
v1_app.include_router(explain_router)

