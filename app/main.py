from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
    user_id : str
    lng : float
    lat : float
    timestamp : str

def updateData():
    cursor = connect.connectToDB()
    updated = connect.getAllInfo(cursor, "sports_places")
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
    return { 'data' : data.to_dict(orient="records") }

MAX_DISTANCE = 25
@app.post('/api/pressence')
def getNearest(usr : UserLocation, user = Depends(auth.require_user)):
    try:
        result = nearest(data, usr.lng, usr.lat)
        if result['dist_m'] <= MAX_DISTANCE:
            username = user['sub']
            up = int(connect.getinfo(connect.connectToDB(), "Points", username)["Points"].iloc[0]) + 1
            connect.updateData(connect.connectToDB(), "Points", up, username)
            print(f'{user['sub']} requested')
    except:
        return { 'status' : "Internal server error"}
    
    return { "status" : "success", 'data' : result }

def getUserPointsData(user = Depends(auth.require_user)):
    #TODO find the points of user via db[user.sub]
    points = int(connect.getinfo(connect.connectToDB(), "Points", user['sub'])['Points'].iloc[0])
    return { 'user' : user['sub'], 'points' : points }
    
@app.get('/api/points/me')
def getPoints(user_points = Depends(getUserPointsData)):
    return { 'user' : user_points['user'], 'points' : user_points['points'] }

class PurchaseModel(BaseModel):
    item_id : str
    price : int
    count : int
    timestamp : str

@app.post('/api/purchase')
def purchase(order : PurchaseModel, user_points = Depends(getUserPointsData)):
    if user_points['points'] >= order.price * order.count:
        #TODO handle purchase
        remain = user_points['points'] - (order.price * order.count)
        connect.updateData(connect.connectToDB(), "Points", remain, user_points['user'])
        return { 'message' : 'Purchase success' }
    return { 'message' : 'Not enough points' }

@app.post('/auth/signup')
def signUp(info : auth.UserInfo):
    #TODO check if the username already exists
    cursor = connect.connectToDB()
    check = connect.getinfo(cursor, "UserInfo", info.username)
    if check.empty:
        connect.insertUser(cursor, info.username, info.password)
        return { 'message' : 'Created successfully' }
    else:
        raise HTTPException(status_code = 400, detail = "Username already exists")

@app.post('/auth/login')
def login(req : auth.UserInfo):
    user_id = auth.verify_user(req.username, req.password)
    if not user_id:
        raise HTTPException(status_code = 401, detail = "Invalid credentials")
    print(f'{user_id} has logged in')
    return auth.make_access_token(sub = user_id)

