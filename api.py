# pip install fastapi
# fastapi dev main.py

from asyncio import sleep
from fastapi import FastAPI, WebSocket
import random
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
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


class ImageData:
    def __init__(self):
        self.id = random.randint(1, 100)
        ntags = random.randint(1, 3)
        self.tags = [random.choice(tags) for _ in range(ntags)]

# image_data = [ImageData() for _ in range(10)]

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Rectangle:
    def __init__(self):
        self.leftTop = Point(0, 0)
        self.leftTop.x = random.randint(0, 100)
        self.leftTop.y = random.randint(0, 100)
        self.width = random.randint(self.leftTop.x, 100)
        self.height = random.randint(self.leftTop.y, 100)
        self.color = random.choice(["red", "green", "blue", "pink"])

class Image:
    def __init__(self):
        self.imgdata = ImageData()
        nrect = random.randint(1, 10)
        self.rectangles = [Rectangle() for _ in range(nrect)]

allimgs = [Image() for _ in range(10)]

class ImageEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Image):
            return o.__dict__
        elif isinstance(o, Rectangle):
            return o.__dict__
        elif isinstance(o, Point):
            return o.__dict__
        return super().default(o)
    
class ImageDataEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ImageData):
            return o.__dict__
        return super().default(o)

@app.get("/list")
def getimglist():
    return Response(content=json.dumps([img.imgdata for img in allimgs], cls=ImageDataEncoder), status_code=200, media_type="application/json")

@app.get("/image/{id}")
async def get_image(id: int):
    action = random.randint(1, 4)
    if action == 1:
        content = json.dumps(Image(random.randint(1, 10)), cls=ImageEncoder)
        return Response(content=content, status_code=200, media_type="application/json")
    elif action == 2:
        return JSONResponse(content={"error": "Internal server error"}, status_code=500)
    elif action == 3:
        await sleep(10)
        content = json.dumps(Image(random.randint(1, 10)), cls=ImageEncoder)
        return Response(content=content, status_code=200, media_type="application/json")
    elif action == 4:
        return Response(content="a" * 1024 * 1024 * 10, status_code=200, media_type="application/json")
    

@app.get("/newimage")
async def create_image():
    allimgs.append(Image())
    id = allimgs[-1].imgdata.id
    await manager.broadcast(json.dumps({"id": id}))
    return {"message": "Image created"}

@app.get("/tags")
async def get_tags():
    return {"tags": tags}


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        print(websocket)
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            print(connection)
            await connection.send_text(message)


manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            await manager.broadcast(data)
    except:
        manager.disconnect(websocket)