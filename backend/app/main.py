from fastapi import FastAPI
from app.routers.search import router as search_router
from app.routers.repo import router as repo_router
from app.routers.repo_details import router as repo_details_router
from app.routers.compare import router as compare_router
from app.routers.recommend import router as recommend_router
from app.routers.analyze import router as analyze_router


app = FastAPI(
    title="AI Search Engine Backend",
    version="1.0.0"
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