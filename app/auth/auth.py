from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os, jwt, uuid
from datetime import datetime, timedelta, timezone

#Authentication
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")  
JWT_ALG = "HS256"                                   
ACCESS_TTL_MIN = 15

security = HTTPBearer()

class UserInfo(BaseModel):
    username : str
    password : str
    
def verify_user(username : str, password : str): 
    #TODO verify usernname with password hash
    if username == os.getenv("USERNAME") and password == os.getenv("USER_PASSWORD"):
        return "admin"
    return None

def require_user(creds : HTTPAuthorizationCredentials = Depends(security)):
    token = creds.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms = [JWT_ALG])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code = 401, detail = "Invalid or expired token")
    
def make_access_token(sub : str):
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes = ACCESS_TTL_MIN)
    payload = {
        "sub" : sub,
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm = JWT_ALG)
    return { "access_token" : token, "token_type" : "Bearer", "expires_in": ACCESS_TTL_MIN * 60 }