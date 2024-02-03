import os
import sys
import time
import uuid
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
from typing import List


class UserInterfaceBridge():
    def __init__(self) -> None:
        self.queue_arr_to_ui = List[Queue]
        enable_vhmap_debug = True
        if enable_vhmap_debug:
            from agent_matrix.matrix.vhmap_debug import VhmapDebugBridge
            self.vhmap = VhmapDebugBridge()
            self.queue_arr_to_ui.append(self.vhmap.queue_matrix_to_here)

    def notify_ui(self, msg: GeneralMsg):
        for q in self.queue_arr_to_ui:
            q.put(msg)
