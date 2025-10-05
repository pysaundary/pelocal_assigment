from pydantic import BaseModel ,EmailStr


class RegisterAndLoginUser(BaseModel):
    email : EmailStr
    password : str