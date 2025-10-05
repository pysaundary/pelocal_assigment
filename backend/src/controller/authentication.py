import traceback
import aiosqlite
from fastapi import APIRouter,Depends
from fastapi.responses import JSONResponse
from src.utilities.the_object_collector import TheObjectCollector
from src.schemas.user_schema import RegisterAndLoginUser
from src.database.sqllite.connector import get_async_db_conn
from src.utilities.text_utilities import email_exists,generate_slug_with_id,create_username_from_email
from src.utilities.password_loop_hole import hash_my_password,match_password
from src.utilities.jwt_playground import JwtTokenUtility

auth_apis = APIRouter(
    prefix= "/auth"
)

@auth_apis.post("/register_user/",status_code= 200)
async def register_user(data : RegisterAndLoginUser,db = Depends(get_async_db_conn)):
    logger = get_logger()
    try:
        check_is_user_exists = await email_exists(data.email,db)
        if check_is_user_exists:
            return JSONResponse({
                "status":False,
                "message":f"User with {data.email} is existed do you want to know his password (only 20 rupees upi)" 
            },400)
        else:
            username =await create_username_from_email(data.email,db)
            slug  =await generate_slug_with_id(username,db)
            password =await hash_my_password(data.password)
            profile_json = "{}"
            sql = """
            INSERT INTO users (email, username, slug, password, profile)
            VALUES (?, ?, ?, ?, json(?))
            """
            cursor = await db.execute(sql, (data.email, username, slug, password, profile_json))
            await db.commit()
            user_id = cursor.lastrowid
            cur2 = await db.execute(
        "SELECT id, email, username, slug FROM users WHERE id = ? LIMIT 1",
        (user_id,),
    )
        row = await cur2.fetchone()
        await cur2.close()
        jwt = JwtTokenUtility()
        token =await jwt.create_activation_token(user_id,data.email)
        return {
            "status": True,
            "message": "User registered",
            "data": {
                "id": row[0],
                "email": row[1],
                "username": row[2],
                "slug": row[3],
                "token":token
            },
        }
    except Exception as e:
        logger.error(f"failed due to {e}")
        logger.error(traceback.format_exc())

@auth_apis.post("/login/", status_code=200)
async def login(data: RegisterAndLoginUser, db: aiosqlite.Connection = Depends(get_async_db_conn)):
    logger = get_logger()
    try:
        # existence check
        cur = await db.execute("SELECT 1 FROM users WHERE email = ? LIMIT 1", (data.email,))
        exists = await cur.fetchone()
        await cur.close()
        if not exists:
            return JSONResponse({"status": False, "message": f"User with {data.email} is not existed"}, 400)

        # fetch row
        sql = "SELECT id, email, username, slug, password, profile FROM users WHERE email = ? LIMIT 1"
        cur = await db.execute(sql, (data.email,))
        row = await cur.fetchone()
        await cur.close()
        logger.info(dict(row))  # row_factory=Row gives dict-like access [web:69][web:113]
        if not match_password(data.password,row["password"]):
            return JSONResponse({"status": False, "message": f"email or password is not correct"}, 400)
        jwt = JwtTokenUtility()
        token =await jwt.create_activation_token(row["id"],data.email)
        return {
            "status": True,
            "message": "User registered",
            "data": {
                "id": row[0],
                "email": row[1],
                "username": row[2],
                "slug": row[3],
                "token":token
            },
        }
    except Exception as e:
        logger.error(f"failed due to {e}")
        return JSONResponse({"status": False, "message": "Internal error"}, 500)


"""___________________UTILITIES________________________"""

def get_logger():
    collector = TheObjectCollector()
    return collector.getKey("api_logger")
