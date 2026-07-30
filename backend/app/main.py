from fastapi import FastAPI
from app.routers.search import router as search_router

app = FastAPI(
    title="AI Search Engine Backend",
    version="1.0.0"
)

app.include_router(search_router)

@app.get("/")
def root():
    return {
        "status": "success",
        "message": "Backend Running Successfully"
    }