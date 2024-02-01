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
from agent_matrix.msg.general_msg import GeneralMsg
from agent_matrix.agent.agent_basic import AgentBasic

class Agent(AgentBasic):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.activate = False



    def agent_task_cycle(self):
        print('hello world')
