import asyncio
import threading
from loguru import logger
from fastapi import WebSocket


class BaseProxy(object):
    """这个类用来管理agent的连接信息，包括websocket连接，client_id，message_queue等等

    Args:
        object (_type_): _description_
    """

    def __init__(self,
                 matrix,
                 agent_id: str,
                 websocket: WebSocket = None,
                 client_id: str = None,
                 message_queue_out: asyncio.Queue = None,
                 message_queue_in: asyncio.Queue = None):
        self.matrix = matrix
        self.connected_event = threading.Event()
        self.agent_id = agent_id
        self.websocket = websocket
        self.client_id = client_id
        self.message_queue_out = message_queue_out
        self.message_queue_in = message_queue_in

    def update_connection_info(self,
                               websocket: WebSocket = None,
                               client_id: str = None,
                               message_queue_out: asyncio.Queue = None,
                               message_queue_in: asyncio.Queue = None):
        if websocket is not None:
            self.websocket = websocket
        if client_id is not None:
            self.client_id = client_id
        if message_queue_out is not None:
            self.message_queue_out = message_queue_out
        if message_queue_in is not None:
            self.message_queue_in = message_queue_in
        self.connected_event.set()


class AgentProxy(BaseProxy):
    """这个类用来管理agent的连接信息，包括websocket连接，client_id，message_queue等等
    """

    def __init__(self, agent_id: str, **kwargs):
        super().__init__(agent_id, **kwargs)

    def create_agent(self,
                     agent_id: str,
                     agent_class: str,
                     agent_kwargs: dict,
                     remote_matrix_kwargs: dict = None,
                     parent=None):
        # 与母体协调，创建新智能体，并建立与新智能体的连接
        from agent_matrix.matrix.mastermind_matrix import MasterMindMatrix
        self.matrix: MasterMindMatrix
        self.matrix.create_agent_final(agent_id=agent_id,
                                       agent_class=agent_class,
                                       agent_kwargs=agent_kwargs,
                                       remote_matrix_kwargs=remote_matrix_kwargs,
                                       parent=parent)
