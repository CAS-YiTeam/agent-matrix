import os
import sys
import time
import platform
import asyncio
import websockets
import pickle
from queue import Queue
from fastapi import FastAPI, WebSocket
from websockets.sync.client import connect

class Agent(object):
    def __init__(self, matrix_kwargs) -> None:
        self.matrix_kwargs = matrix_kwargs
        self.com_websocket = self.connect_to_matrix()

    def connect_to_matrix(self):
        host = self.matrix_kwargs['host']
        port = str(self.matrix_kwargs['port'])
        print('connect')
        websocket_connection = connect(f"ws://{host}:{port}/ws_agent")
        print('send')
        websocket_connection.send("hello")
        print('done')

matrix_kwargs = {
    "host": "0.0.0.0",
    "port": 10101
}
ag = Agent(matrix_kwargs)