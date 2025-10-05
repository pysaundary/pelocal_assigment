# simple_auth.py
from fastapi import Request, HTTPException
from functools import wraps
from typing import Callable
import aiosqlite
from src.utilities.jwt_playground import JwtTokenUtility
from src.database.sqllite.connector import get_async_db_conn

def require_user():
    """

    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            # 1) Token extraction
            auth = request.headers.get("Authorization")
            if not auth or not auth.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Missing or invalid token")
            token = auth.split(" ", 1)[1].strip()

            # 2) Verify token, extract user_id
            try:
                payload = await JwtTokenUtility().verify_token(token, type="auth")
                user_id = payload.get("user_id")
                if not user_id:
                    raise HTTPException(status_code=401, detail="Invalid token payload")
            except HTTPException:
                raise
            except Exception:
                raise HTTPException(status_code=401, detail="Token expired or invalid")

            agen = get_async_db_conn()         
            conn: aiosqlite.Connection = await agen.__anext__()  
            try:
                # 4) Existence check
                cur = await conn.execute("SELECT 1 FROM users WHERE id = ? LIMIT 1", (user_id,))
                row = await cur.fetchone()
                await cur.close()
                if row is None:
                    raise HTTPException(status_code=401, detail="User not found")

                # 5) Pass user_id to downstream
                request.state.user_id = user_id

                # 6) Call the actual handler
                return await func(*args, request=request, **kwargs)

            finally:
                # 7) Close generator to release connection
                try:
                    await agen.__anext__()  # triggers generator exit -> closes conn
                except StopAsyncIteration:
                    pass

        return wrapper
    return decorator
