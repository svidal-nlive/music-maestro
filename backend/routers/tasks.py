from fastapi import APIRouter, Depends
from workers import process_audio
from routers.auth import get_current_user

router = APIRouter(prefix="/task", tags=["task"])

@router.post("/start")
def start_task(filename: str, user: str = Depends(get_current_user)):
    task = process_audio.delay(filename)
    return {"task_id": task.id, "started_by": user}
