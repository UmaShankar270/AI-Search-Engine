import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import os
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent.parent   # Go up to AI-Search-Engine
AI_SEARCH_DIR = PROJECT_ROOT / "ai-search"

# Load environment configurations
load_dotenv(BACKEND_DIR / ".env")

# Force Hugging Face offline mode to prevent Windows socket access violations in Python 3.14
os.environ["HF_HUB_OFFLINE"] = "1"

if str(AI_SEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(AI_SEARCH_DIR))


try:
    from ai.facade import AIFacade
    from ai.models.exceptions import AIModuleError
except Exception as exc:  # pragma: no cover - defensive import fallback
    class AIModuleError(Exception):
        """Fallback error used when the optional AI module is unavailable."""

    AIFacade = None
    logger = logging.getLogger(__name__)
    logger.warning("AI module import failed; continuing without AI initialization: %s", exc)

from app.database import engine
from app.database_models import Base

from app.routers.search import router as search_router
from app.routers.repo import router as repo_router
from app.routers.repo_details import router as repo_details_router
from app.routers.compare import router as compare_router
from app.routers.recommend import router as recommend_router
from app.routers.analyze import router as analyze_router

from app.routers.history import router as history_router
from app.routers.favorites import router as favorites_router
from app.routers.analytics import router as analytics_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if AIFacade is None:
        logger.info("AI module unavailable; skipping AI facade initialization")
        app.state.ai_facade = None
    else:
        logger.info("Initializing AIFacade and pre-loading AI Models...")

        facade = AIFacade(
            embedding_dim=384,
            search_index_path="data/faiss_index.index",
            ranking_config_path="configs/ranking_weights.json"
        )

        try:
            facade.warmup_embeddings()
            app.state.ai_facade = facade
            logger.info("AIFacade successfully initialized and warmed up.")
        except Exception as exc:
            logger.warning("AI warmup failed; continuing without AI facade: %s", exc)
            app.state.ai_facade = None

    yield

    logger.info("Shutting down backend, unloading AI model resources...")

    facade = getattr(app.state, "ai_facade", None)
    embedding_generator = getattr(facade, "_embedding_generator", None)
    model = getattr(embedding_generator, "_model", None)
    if model is not None and hasattr(model, "unload"):
        model.unload()

    logger.info("AI model resources unloaded successfully."
    
    
)



Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Search Engine Backend",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AIModuleError)
async def ai_module_exception_handler(request: Request, exc: AIModuleError):
    logger.error("AI Module Error encountered: %s", str(exc))

    return JSONResponse(
        status_code=400,
        content={
            "status": "error",
            "message": f"AI Processing Error: {str(exc)}"
        }
    )


app.include_router(search_router)
app.include_router(repo_router)
app.include_router(repo_details_router)
app.include_router(compare_router)
app.include_router(recommend_router)
app.include_router(analyze_router)

app.include_router(history_router)
app.include_router(favorites_router)
app.include_router(analytics_router)


@app.get("/")
def root(request: Request):
    ai_facade = getattr(request.app.state, "ai_facade", None)
    return {
        "status": "success",
        "message": "Backend Running Successfully",
        "ai_facade_loaded": ai_facade is not None,
        "ai_facade_type": str(type(ai_facade)) if ai_facade else None
    }