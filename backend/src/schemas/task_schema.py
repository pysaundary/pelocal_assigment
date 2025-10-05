from pydantic import BaseModel
from typing import Optional, Any, Dict

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[int] = 1
    is_done: Optional[bool] = False

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    is_done: Optional[bool] = None

class TaskRead(BaseModel):
    id: int
    payload: Dict[str, Any]
    created_by: int
    created_at: str