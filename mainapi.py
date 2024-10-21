# pip install fastapi
# fastapi dev main.py

from asyncio import sleep
from fastapi import FastAPI, WebSocket
import random
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware

import json
import json

origins = [
    "*"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tags = ["a", "b", "c", "d"]
colors = ["red", "green", "blue", "yellow"]

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class ImageData:
    def __init__(self):
        self.id = random.randint(1, 100)
        ntags = random.randint(1, 3)
        self.tags = []
        for _ in range(ntags):
            self.tags.append(random.choice(tags))

class Rectangle:
    def __init__(self):
        self.leftTop = Point(0, 0)
        self.leftTop.x = random.randint(0, 100)
        self.leftTop.y = random.randint(0, 100)
        self.width = random.randint(self.leftTop.x, 100)
        self.height = random.randint(self.leftTop.y, 100)
        self.color = random.choice(colors)

class Image:
    def __init__(self, n):
        self.rectangles = [Rectangle() for _ in range(n)]
    
imglist = [ImageData() for _ in range(10)]

class ImageEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Image) or isinstance(o, ImageData) or isinstance(o, Rectangle) or isinstance(o, Point):
            return o.__dict__
        return super().default(o)

@app.get("/list")
def getimglist():
    return Response(content=json.dumps(imglist, cls=ImageEncoder), status_code=200, media_type="application/json")

@app.get("/tags")
async def gettags():
    return {"tags": tags}

@app.get("/image/{id}")
async def getimg(id: int):
    todo = random.randint(1, 4)
    if todo == 1:
        return JSONResponse(content={"error": "fake error 500"}, status_code=500)
    elif todo == 2:
        await sleep(10)
        content = json.dumps(Image(random.randint(1, 10)), cls=ImageEncoder)
        return Response(content=content, status_code=200, media_type="application/json")
    elif todo == 3:
        return Response(content="x" * 10 * 1000 * 1000, status_code=200, media_type="application/json")
    elif todo == 4:
        content = json.dumps(Image(random.randint(1, 10)), cls=ImageEncoder)
        return Response(content=content, status_code=200, media_type="application/json")

@app.get("/newimage")
async def createimg():
    imglist.append(ImageData())
    id = imglist[-1].id
    await allconns.broadcast(json.dumps({"id": id}))
    return {"message": "Image created " + str(id)}

class Connections:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        print(websocket)
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            print(connection)
            await connection.send_text(message)


allconns = Connections()

@app.websocket("/ws")
async def wsconnect(websocket: WebSocket):
    await allconns.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
    except:
        allconns.disconnect(websocket)