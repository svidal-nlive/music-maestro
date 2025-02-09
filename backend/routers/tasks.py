from fastapi import FastAPI, BackgroundTasks, HTTPException, APIRouter
from celery.result import AsyncResult
from workers import process_audio, celery_app
# Make sure to import redis_client if it's used:
# from somewhere import redis_client

router = APIRouter()

@router.post("/task/start")
def start_task(filename: str):
    task = process_audio.delay(filename)
    return {"task_id": task.id, "started_by": "string"}

@router.get("/task/status/{task_id}")
def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    return {"task_id": task_id, "status": task_result.status}
