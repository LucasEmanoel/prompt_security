from fastapi import FastAPI
from app.routers import sanitize

app = FastAPI(title="Sanitizer API")

app.include_router(sanitize.router)

@app.get("/")
def root():
    return {"message": "Sanitizer running"}