from fastapi import FastAPI

from app.config import settings
from app.routes import llm

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(llm.router, prefix="/api/v1", tags=["llm"])

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to the LLM Service API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
