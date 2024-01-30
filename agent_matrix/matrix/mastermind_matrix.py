import os
import sys
import time
import platform
import asyncio
from queue import Queue
from fastapi import FastAPI, WebSocket

class AgentProxy(object):
    def __init__(self, websocket, data):
        self.websocket = websocket
        self.data = data

class SubMatrixProxy(object):
    pass

class MasterMindMatrix(object):
    def __init__(self, port, dedicated_server=False):
        self.port = port
        self.dedicated_server = dedicated_server
        self.init_asgi_communication(host_kwargs=None, host=None, port=None)
        self.launch_agentcraft()
        self.begin_event_loop()
        self.connected_agents = []
        self.connected_sub_matrix = []

    def init_asgi_communication(self, host_kwargs, host, port):
        pass

    def launch_agentcraft(self):
        pass

    async def long_task_01_wait_incoming_connection(self):
        # task 1 wait incoming agent connection
        async def launch_websocket_server():
            app = FastAPI()
            
            @app.websocket("/ws_agent")
            async def register_incoming_agents(websocket: WebSocket):
                await websocket.accept()
                while True:
                    data = await websocket.receive_text()
                    self.connected_agents.append(AgentProxy(websocket=websocket, data=data))
                    
            @app.websocket("/ws_sub_matrix")
            async def register_incoming_sub_matrix(websocket: WebSocket):
                await websocket.accept()
                while True:
                    data = await websocket.receive_text()
                    self.connected_sub_matrix.append(SubMatrixProxy(websocket=websocket, data=data))
                    
            import uvicorn
            uvicorn.run(app, host="0.0.0.0", port=self.port)
            
        await launch_websocket_server()


    async def long_task_03_exec_command_queue(self):
        # task 3 wait agent command, put them into task queue
        while True:
            time.sleep(1000)


    async def major_event_loop(self):
        long_task_01 = asyncio.create_task(self.long_task_01_wait_incoming_connection())
        long_task_02 = asyncio.create_task(self.long_task_03_exec_command_queue())
        await asyncio.gather(long_task_01, long_task_02)


    def begin_event_loop(self):
        asyncio.run(self.major_event_loop())


mmm = MasterMindMatrix(10101)
