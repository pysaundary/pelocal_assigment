# task_routes.py
from fastapi import APIRouter, Depends, Request, HTTPException, Query 
from typing import Optional
import aiosqlite
import json

from src.database.sqllite.connector import get_async_db_conn 
from src.utilities.decorators import require_user      
from src.schemas.task_schema import TaskCreate, TaskUpdate, TaskRead

task_router = APIRouter(prefix="/tasks", tags=["tasks"])

@task_router.post("/", response_model=TaskRead)
@require_user()
async def create_task(
    request: Request,
    data: TaskCreate,
    db: aiosqlite.Connection = Depends(get_async_db_conn),
):
    created_by = request.state.user_id
    payload = {
        "title": data.title,
        "description": data.description,
        "priority": data.priority,
        "is_done": data.is_done,
    }
    sql = """
        INSERT INTO tasks (payload, created_by)
        VALUES (json(?), ?)
    """
    cur = await db.execute(sql, (json.dumps(payload), created_by))
    await db.commit()
    new_id = cur.lastrowid

    cur = await db.execute(
        "SELECT id, payload, created_by, created_at FROM tasks WHERE id = ? LIMIT 1",
        (new_id,),
    )
    row = await cur.fetchone()
    await cur.close()
    return TaskRead(
        id=row["id"],
        payload=json.loads(row["payload"]),
        created_by=row["created_by"],
        created_at=row["created_at"],
    )

@task_router.get("/{task_id}", response_model=TaskRead)
@require_user()
async def get_task(
    request: Request,
    task_id: int,
    db: aiosqlite.Connection = Depends(get_async_db_conn),
):
    cur = await db.execute(
        "SELECT id, payload, created_by, created_at FROM tasks WHERE id = ? LIMIT 1",
        (task_id,),
    )
    row = await cur.fetchone()
    await cur.close()
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskRead(
        id=row["id"],
        payload=json.loads(row["payload"]),
        created_by=row["created_by"],
        created_at=row["created_at"],
    )

@task_router.get("/", response_model=list[TaskRead])
@require_user()
async def list_tasks(
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    priority: Optional[int] = Query(None, ge=0),
    is_done: Optional[bool] = Query(None),
    db: aiosqlite.Connection = Depends(get_async_db_conn),
):
    user_id = request.state.user_id

    sql = """
        SELECT id, payload, created_by, created_at
        FROM tasks
    """
    where = ["created_by = ?"]
    params: list[object] = [user_id]

    if priority is not None:
        where.append("CAST(json_extract(payload, '$.priority') AS INTEGER) = ?")
        params.append(priority)

    if is_done is not None:
        where.append("CAST(json_extract(payload, '$.is_done') AS INTEGER) = ?")
        params.append(1 if is_done else 0)

    sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cur = await db.execute(sql, tuple(params))
    rows = await cur.fetchall()
    await cur.close()

    return [
        TaskRead(
            id=row["id"],
            payload=json.loads(row["payload"]),
            created_by=row["created_by"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


@task_router.patch("/{task_id}", response_model=TaskRead)
@require_user()
async def update_task(
    request: Request,
    task_id: int,
    data: TaskUpdate,
    db: aiosqlite.Connection = Depends(get_async_db_conn),
):
    # fetch current
    cur = await db.execute(
        "SELECT payload, created_by, created_at FROM tasks WHERE id = ? LIMIT 1",
        (task_id,),
    )
    row = await cur.fetchone()
    await cur.close()
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")

    current = json.loads(row["payload"])
    updates = {k: v for k, v in data.dict(exclude_unset=True).items()}
    current.update(updates)

    await db.execute(
        "UPDATE tasks SET payload = json(?) WHERE id = ?",
        (json.dumps(current), task_id),
    )
    await db.commit()

    # return updated
    cur = await db.execute(
        "SELECT id, payload, created_by, created_at FROM tasks WHERE id = ? LIMIT 1",
        (task_id,),
    )
    row2 = await cur.fetchone()
    await cur.close()
    return TaskRead(
        id=row2["id"],
        payload=json.loads(row2["payload"]),
        created_by=row2["created_by"],
        created_at=row2["created_at"],
    )

# 5) Delete by id
@task_router.delete("/{task_id}", response_model=dict)
@require_user()
async def delete_task(
    request: Request,
    task_id: int,
    db: aiosqlite.Connection = Depends(get_async_db_conn),
):
    cur = await db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    await db.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": True, "message": "Deleted"}
