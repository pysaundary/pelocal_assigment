import bcrypt

async def hash_my_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')  # ✅ decode to string

async def match_password(password: str, hashed_password: str) -> bool:
    # ✅ encode both to bytes before checking
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))