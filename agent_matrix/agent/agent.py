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
try:
    from websockets.sync.client import connect
except ImportError:
    raise ImportError("Import websockets failed, upgrade websockets by running: pip install websockets --upgrade")

from agent_matrix.msg.general_msg import GeneralMsg
from agent_matrix.agent.agent_basic import AgentBasic



class Agent(AgentBasic):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.activate = False

    def agent_task_cycle(self):
        print('Hi, you have to implement this function (Agent.agent_task_cycle) in your subclass.')
        time.sleep(2.0)
        raise NotImplementedError

    def on_agent_wakeup(self, kwargs):
        print('Hi, you have to implement this function (Agent.on_agent_wakeup) in your subclass.')
        raise NotImplementedError

class EchoAgent(Agent):
    def agent_task_cycle(self):
        return

    def on_agent_wakeup(self, kwargs):
        return kwargs
