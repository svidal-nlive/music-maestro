# backend/main.py
from fastapi import FastAPI
from routers import auth, files, tasks
from workers import celery_app

app = FastAPI()

app.include_router(auth.router)
app.include_router(files.router)
app.include_router(tasks.router)

@app.get("/")
def root():
    return {"message": "Music Maestro API Running!"}
