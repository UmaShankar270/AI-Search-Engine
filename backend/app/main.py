import logging
from contextlib import asynccontextmanager

from ai.facade import AIFacade
from ai.models.exceptions import AIModuleError
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routers.analyze import router as analyze_router
from app.routers.compare import router as compare_router
from app.routers.recommend import router as recommend_router
from app.routers.repo import router as repo_router
from app.routers.repo_details import router as repo_details_router
from app.routers.search import router as search_router

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Startup Initialization
    logger.info("Initializing AIFacade and pre-loading AI Models...")
    # Initialize the facade (automatically loads configuration)
    facade = AIFacade(
        embedding_dim=384,
        search_index_path="data/faiss_index.index",
        ranking_config_path="configs/ranking_weights.json"
    )
    # Warm up sentence-transformer models in memory
    facade.warmup_embeddings()
    app.state.ai_facade = facade
    logger.info("AIFacade successfully initialized and warmed up.")

    yield

    # 2. Shutdown Cleanup
    logger.info("Shutting down backend, unloading AI model resources...")
    if hasattr(app.state, "ai_facade"):
        app.state.ai_facade._embedding_generator._model.unload()
    logger.info("AI model resources unloaded successfully.")


app = FastAPI(
    title="AI Search Engine Backend",
    version="1.0.0",
    lifespan=lifespan
)


# Register global exception handler for AI Module errors
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


@app.get("/")
def root():
    return {
        "status": "success",
        "message": "Backend Running Successfully"
    }
