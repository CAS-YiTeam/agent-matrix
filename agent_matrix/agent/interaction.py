import os
import sys
import time
import platform
import asyncio
import threading
from loguru import logger
from queue import Queue
from agent_matrix.agent.agent import Agent

class InteractionBuilder(object):
    def __init__(self) -> None:
        pass

    def create_edge(self, src_agent, dst_agent, edge_color):
        pass
