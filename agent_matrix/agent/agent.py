import os
import sys
import time
import platform
import asyncio
import websockets
import pickle
import threading
from queue import Queue
from fastapi import FastAPI, WebSocket
from websockets.sync.client import connect
from agent_matrix.agent_proxy import ProxyHandle


class Agent(object):

    def __init__(self, **kwargs) -> None:
        self.is_proxy = kwargs["is_proxy"]
        self.agent_id = kwargs["agent_id"]
        self.matrix_host = kwargs["matrix_host"]
        self.matrix_port = kwargs["matrix_port"]
        self.websocket_connection = None

    def __del__(self):
        try:
            self.websocket_connection.close()
        except:
            pass

    def run_non_blocking(self):
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

    def run(self):
        # 尝试连接，连接成功后会返回
        self.com_websocket = self.connect_to_matrix()
        self.major_task()

    def major_task(self):
        print('enter major task')

    def connect_to_matrix(self):
        host = self.matrix_host
        port = str(self.matrix_port)
        self.websocket_connection = connect(f"ws://{host}:{port}/ws_agent")
        self.websocket_connection.send(
            pickle.dumps({"agent_id": self.agent_id}))
