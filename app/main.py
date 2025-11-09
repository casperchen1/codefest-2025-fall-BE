from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import numpy as np
from pydantic import BaseModel
import pandas as pd
from dotenv import load_dotenv
from app.dataBase import connect
from app.auth import auth
from time import time
import asyncio
import os

app = FastAPI()
load_dotenv()

app.mount("/assets", StaticFiles(directory="assets"), name="assets")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv('AUDIENCE')],        # narrow this in prod
    allow_credentials = True,
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
    try:
        updated = connect.getAllUserInfo(cursor, "sports_places")
        return updated
    finally:
        cursor.close()

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

MAX_DISTANCE = 30
MAX_CACHE_RANGE = 20
USER_CACHE = {} #{ 'user_id' : { 'lng' :, 'lat' :, 'data' :, 'ts' :, 'inRange': } }

async def clean_cache():
    while True:
        now = time()
        expired = [uid for uid, info in USER_CACHE.items() if now - info["ts"] > 60]
        for uid in expired:
            print(f'cached cleaned for {uid}')
            del USER_CACHE[uid]
        await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(clean_cache())

def use_cache_if_near(user_id, lng, lat):
    last = USER_CACHE.get(user_id)
    if not last:
        return None
    moved = haversine(lng, lat, last['lng'], last['lat'])
    if moved > MAX_CACHE_RANGE:
        return None
    return last

@app.post('/api/pressence')
def getNearest(usr : UserLocation, user = Depends(auth.require_user)):
    cursor = connect.connectToDB()

    inRange = False
    result = {}
    try:
        last = USER_CACHE.get(user['sub'])
        if last:
            print("cache success")
            inRange = last['inRange']
            result = last['data']
        else:
            result = nearest(data, usr.lng, usr.lat)
            inRange = result['dist_m'] <= MAX_DISTANCE
            USER_CACHE[user['sub']] = { 'lng' : usr.lng, 'lat' : usr.lat, 'data' : result, 'inRange' : inRange, 'ts' : time() }
        if inRange:
            username = user['sub']
            up = int(connect.getUserInfo(cursor, "Points", username)["Points"].iloc[0]) + 1
            connect.updateData(cursor, "Points", up, username)
            print(f'{user['sub']} requested')
    
        return { 'status' : "success", 'inRange' : inRange, 'data' : result }
    except:
        raise HTTPException(status_code = 500, detail = "Internal server error")
    finally:
        cursor.close()

def getUserPointsData(user = Depends(auth.require_user)):
    #TODO find the points of user via db[user.sub]
    cursor = connect.connectToDB()
    try:
        points = int(connect.getUserInfo(cursor, "Points", user['sub'])['Points'].iloc[0])
        return { 'user' : user['sub'], 'points' : points }
    except:
        raise HTTPException(status_code = 500, detail = "Internal server error")
    finally:
        cursor.close()
    
@app.get('/api/points/me')
def getPoints(user_points = Depends(getUserPointsData)):
    return { 'user' : user_points['user'], 'points' : user_points['points'] }

@app.get('/api/merch')
def getAllMerch():
    cursor = connect.connectToDB()
    try:
        results = connect.getAllUserInfo(cursor, "Products")
        return { 'data' : results.to_dict(orient="records") }
    except:
        raise HTTPException(status_code = 500, detail = 'Internal Server Error')
    finally:
        cursor.close()

class PurchaseModel(BaseModel):
    item_id : int
    count : int
    timestamp : str

@app.post('/api/purchase')
def purchase(order : PurchaseModel, user_points = Depends(getUserPointsData)):
    cursor = connect.connectToDB()
    try:
        price = connect.getMerchByID(cursor, order.item_id)['price'].iloc[0]
        if user_points['points'] >= (price * order.count):
            remain = user_points['points'] - (price * order.count)
            connect.updateData(cursor, "Points", remain, user_points['user'])
            return { 'message' : 'Purchase success' }
        else:
            raise HTTPException(status_code = 403, detail = "Not enough points")
    except HTTPException as e:
        if e.status_code == 403:
            raise e
        else:
            raise HTTPException(status_code = 500, detail = "Internal server error")
    finally:
        cursor.close()

@app.get('/api/getallscores')
def getAllScores():
    cursor = connect.connectToDB()
    try:
        cursor.execute("SELECT * FROM Points ORDER BY Points DESC")
        results = cursor.fetchall()
        return { 'data' : results }
    except:
        raise HTTPException(status_code = 500, detail = 'Internal Server Error')
    finally:
        cursor.close()

@app.post('/auth/signup')
def signUp(info : auth.UserInfo):
    #TODO check if the username already exists
    cursor = connect.connectToDB()
    try:
        check = connect.getUserInfo(cursor, "UserInfo", info.username)
        if check.empty:
            connect.insertUser(cursor, info.username, info.password)
            print(f"new user {info.username} is created")
            return { 'message' : 'Created successfully' }
        raise HTTPException(status_code = 400, detail = "Username already exists")
    except HTTPException as e:
        if e.status_code == 400:
            raise e
        raise HTTPException(status_code = 500, detail = "Internal server error")
    finally:
        cursor.close()

@app.post('/auth/login')
def login(req : auth.UserInfo):
    user_id = auth.verify_user(req.username, req.password)
    if not user_id:
        raise HTTPException(status_code = 401, detail = "Invalid credentials")
    print(f'{user_id} has logged in')
    return auth.make_access_token(sub = user_id)

