# codefest-2025-fall-BE
The backend server for codefest-fall.

# APIs
## /api/health (GET)
**purpose:**
check the status of the server

**Authorization:** false

**repsonse example:**
```json
{
    "status": "operating",
    "test": "DEMO"
}
```

## /api/dataset (GET)
**purpose:**
return all of the sports facility

**Authorization:** false

**response example:**
```json
{
    "data": [
        {
            "id": 1316,
            "行政區": "士林區",
            "場地": "天母運動場區",
            "類別": "籃球場",
            "緯度": 25.1137,
            "經度": 121.5345
        },
        {
            "id": 1317,
            "行政區": "士林區",
            "場地": "天母運動場區",
            "類別": "籃球場",
            "緯度": 25.1137,
            "經度": 121.5347
        },
        ...
}
```

## /api/pressence (POST)
**purpose:**
send the user location to the server, and return the nearest facility around.
increase the points of the user if he's within the `MAX_DISTANCE`
inRange is true if the user is can obtain points

**body:**
```json
{
  "user_id": "string",
  "lng": 0,
  "lat": 0,
  "timestamp": "string"
}
```

**Authorization:** true

**response example:**
```json
{
    "status": "success",
    "inRange" : true
    "data": {
        "name": "大湖山莊成功社區",
        "type": "籃球場",
        "lng": 121.605,
        "lat": 25.0862,
        "dist_m": 22.238985329254962
    }
}
```

## /api/points/me (GET)
**purpose:**
get the points of the user

**Autherization:** true

**response example:**
```json
{
    "user": "test",
    "points": 0
}
```

## /api/purchase (POST)
**purpose:**
send purchase request to the server

**body:**
```json
{
    "item_id" : "water",
    "price" : 1,
    "count" : 1,
    "timestamp" : "2025/11/08"
}
```

**Autherization:** true

**response example:**
```json
{
    "message" : "Purchase success"
}
```

## /auth/signup (POST)
**purpose:**
create an account, throw errors if the username already exists

**body:**
```json
{
    "username" : "test",
    "password" : "abc123"
}
```

**Autherization:** false

**response example:**
```json
{
    "message" : "Created successfully"
}
```

## /auth/login (POST)
**purpose:**
returns the JWT payload if successfully logged in

**body:**
```json
{
    "username" : "test",
    "password" : "abc123"
}
```

**Autherization:** false

**response example:**
```json
{
    "access_token": "<JWT token>"
    "token_type": "Bearer",
    "expires_in": 900
}
```


