from jose.jwt import encode,decode
from src.utilities.the_object_collector import TheObjectCollector
from datetime import datetime,timedelta
class JwtTokenUtility:
    def __init__(self):
        self.collector = TheObjectCollector()

    async def create_token(self,payload :dict )->str:
        app_config = self.collector.getKey("config")
        secret = app_config.get("secret_key")
        algo = app_config.get("algo")
        payload["exp"]  = datetime.now()+timedelta(days=20)
        return encode(payload,secret,algorithm=algo)
    
    async def verify_token(self,token:str,type : str = "auth")->dict:
        app_config = self.collector.getKey("config")
        secret = app_config.get("secret_key")
        algo = app_config.get("algo")
        if not secret or not algo:
            raise ValueError("failed to decode")
        return decode(token,secret,algorithms=algo)
    
    async def create_activation_token(self,user_id,user_email):
        app_config = self.collector.getKey("config")
        secret = app_config.get("secret_key")
        algo = app_config.get("algo")
        return encode({"user_id":user_id,"user_email":user_email,"exp":datetime.now()+timedelta(days=100)},secret,algorithm=algo)