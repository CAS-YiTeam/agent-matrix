import os
import sys
import time
import json
import platform
import pickle
import asyncio
import threading
import subprocess
from loguru import logger
from queue import Queue
from fastapi import FastAPI, WebSocket
from agent_matrix.agent.agent_proxy import AgentProxy
from agent_matrix.msg.general_msg import GeneralMsg


app = FastAPI()

@app.websocket("/ws_agent")
async def _register_incoming_agents(websocket: WebSocket):
    await websocket.accept()
    await websocket.close()

async def run():
    logger.info("uvicorn starts")
    import uvicorn
    config = uvicorn.Config(app, host='127.0.0.1', port=10101, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()
asyncio.run(run())