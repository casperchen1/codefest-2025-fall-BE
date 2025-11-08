from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware import CORSMiddleware
import numpy as np
from pydantic import BaseModel
import pandas as pd
from dotenv import load_dotenv
import os
from app.dataBase import connect
from app.auth import auth

app = FastAPI()
load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # narrow this in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#API
class UserLocation(BaseModel):
    userid : str
    lng : float
    lat : float
    timestamp : str

def updateData():
    #TODO will replaced by db search
    #updated = pd.read_csv('../assets/sports_facility.csv')
    cursor = connect.connectToDB()
    updated = connect.getinfo(cursor, "sports_places")
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
    return { 'status' : 'operating', 'test' : os.getenv("USERNAME") }

@app.get('/api/dataset')
def getData():
     return { 'data' : data.to_dict(orient="records") }

MAX_DISTANCE = 25
@app.post('/api/pressence')
def getNearest(usr : UserLocation, user = Depends(auth.require_user)):
    try:
        result = nearest(data, usr.lng, usr.lat)
        if result['dist_m'] <= MAX_DISTANCE:
            #TODO add points to user.sub
            print("points added")
    except:
        return { 'status' : "Internal server error"}
    
    return { "status" : "success", 'data' : result }

@app.get('/api/points/me')
def getPoints(user = Depends(auth.require_user)):
    #TODO find the points of user via db[user.sub]
    return { 'user' : user }

@app.post('/auth/login')
def login(req : auth.UserInfo):
    user_id = auth.verify_user(req.username, req.password)
    if not user_id:
        raise HTTPException(status_code = 401, detail = "Invalid credentials")
    return auth.make_access_token(sub = user_id)

