from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from typing import Union
import uvicorn
import threading

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

class FastapiWebCommunication():
    def __init__(self, host_matrix):
        self.host_matrix = host_matrix

    def init_asgi_communication(self, host_kwargs, host, port):
        app = FastAPI()
        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            data = await websocket.receive_bytes()
            await websocket.send_text(f"Message received: {data}")

        uvicorn.run(app, host="0.0.0.0", port=8000, ws_ping_interval=300, ws_ping_timeout=600)
