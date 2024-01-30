import os
import sys
import time
import platform
import asyncio
from loguru import logger
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
        self.connected_agents = []
        self.connected_sub_matrix = []
        self.launch_agentcraft()
        self.begin_event_loop()

    def launch_agentcraft(self):
        logger.info("launch agentcraft")
        pass

    async def long_task_01_wait_incoming_connection(self):
        # task 1 wait incoming agent connection
        logger.info("task 1 wait incoming agent connection")
        async def launch_websocket_server():
            app = FastAPI()
            @app.get("/cc")
            async def get():
                return "HTMLResponse(html)"
            
            @app.websocket("/ws_agent")
            async def register_incoming_agents(websocket: WebSocket):
                await websocket.accept()
                data = await websocket.receive_text()
                self.connected_agents.append(AgentProxy(websocket=websocket, data=data))
                    
            @app.websocket("/ws_sub_matrix")
            async def register_incoming_sub_matrix(websocket: WebSocket):
                await websocket.accept()
                data = await websocket.receive_text()
                self.connected_sub_matrix.append(SubMatrixProxy(websocket=websocket, data=data))
                    
            logger.info("uvicorn starts")
            import uvicorn
            config = uvicorn.Config(app, port=self.port, log_level="info")
            server = uvicorn.Server(config)
            await server.serve()

        await launch_websocket_server()
        logger.info("uvicorn terminated")


    async def long_task_03_exec_command_queue(self):
        # task 3 wait agent command, put them into task queue
        while True:
            await asyncio.sleep(1000)


    async def major_event_loop(self):
        long_task_01 = asyncio.create_task(self.long_task_01_wait_incoming_connection())
        long_task_02 = asyncio.create_task(self.long_task_03_exec_command_queue())
        await long_task_01
        await long_task_02


    def begin_event_loop(self):
        logger.info("begin event loop")
        asyncio.run(self.major_event_loop())


mmm = MasterMindMatrix(10101)
