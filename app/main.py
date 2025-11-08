from fastapi import FastAPI, responses, HTTPException
import numpy as np
from pydantic import BaseModel
import pandas as pd
from dotenv import load_dotenv
import os, jwt, uuid
from datetime import datetime, timedelta, timezone

app = FastAPI()
load_dotenv()

#API
class UserLocation(BaseModel):
    userid : str
    lng : float
    lat : float
    timestamp : str

def updateData():
    #TODO will replaced by db search
    updated = pd.read_csv('../assets/sports_facility.csv')
    return updated

def haversine(lng1, lat1, lng2, lat2):
    R = 6371000.0  # meters

    # convert inputs to numpy arrays for broadcasting
    lng1 = np.asarray(lng1, dtype=float)
    lat1 = np.asarray(lat1, dtype=float)
    lng2 = np.asarray(lng2, dtype=float)
    lat2 = np.asarray(lat2, dtype=float)

    # convert all to radians
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlmb = np.radians(lng2 - lng1)

    a = np.sin(dphi / 2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlmb / 2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

def nearest(facilities_df, user_lng, user_lat):
    lngs = pd.to_numeric(facilities_df["經度"]).to_numpy()
    lats = pd.to_numeric(facilities_df["緯度"]).to_numpy()

    d = haversine(user_lng, user_lat, lngs, lats)
    i = int(np.argmin(d))
    row = facilities_df.iloc[i]
    return {"name": row["場地"], 
            "type": row["類別"], 
            "lng" : row["經度"], 
            "lat" : row["緯度"] , 
            "dist_m": float(d[i])}

data = updateData()

@app.get('/api/health')
def getStatus():
    return { 'status' : 'operating' }

@app.get('/api/dataset')
def getData():
    return { 'data' : data }


@app.post('/api/pressence')
def getNearest(usr : UserLocation):
    try:
        result = nearest(data, usr.lng, usr.lat)
    except:
        return { 'status' : "Internal server error"}
    
    return { "status" : "success", 'data' : result }

#Authentication
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")  
JWT_ALG = "HS256"                                   
ACCESS_TTL_MIN = 15

class UserInfo(BaseModel):
    username : str
    password : str

def verify_user(username : str, password : str): 
    #TODO verify usernname with password hash
    if username == os.getenv("USERNAME") and password == os.getenv("USER_PASSWORD"):
        return "admin"
    return None

def make_access_token(sub : str):
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes = ACCESS_TTL_MIN)
    payload = {
        "sub" : sub,
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm = JWT_ALG)
    return { "access_token" : token, "token_type" : "Bearer", "expires_in": ACCESS_TTL_MIN * 60 }

@app.post('/auth/login')
def login(req : UserInfo):
    user_id = verify_user(req.username, req.password)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return make_access_token(sub = user_id)

