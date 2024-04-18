import pickle
import asyncio
import threading
from loguru import logger
from fastapi import WebSocket
from agent_matrix.msg.ui_msg import UserInterfaceMsg
from typing import List
from typing_extensions import Self


class AgentCraftProxy(object):
    """
    一个UE客户端在母体中的代理对象
    这个类用来管理UE客户端的连接信息
    """

    def __init__(self,
                 matrix,
                 agentcraft_interface_id: str,
                 websocket: WebSocket = None,
                 client_id: str = None,
                 message_queue_out: asyncio.Queue = None,
                 message_queue_in: asyncio.Queue = None):
        # 与母体协调，创建新智能体，并建立与新智能体的连接
        self.matrix = matrix
        # 当websocket连接成功后，会设置这个event
        self.connected_event = threading.Event()
        # 智能体的id
        self.agentcraft_interface_id = agentcraft_interface_id
        self.proxy_id = '_proxy_' + agentcraft_interface_id
        # websocket连接
        self.websocket = websocket
        # websocket连接的client_id
        self.client_id = client_id
        # 将命令发送到真正的智能体进程中
        self.message_queue_send_to_unreal_engine = message_queue_out
        # 从真正的智能体进程中接收命令
        self.message_queue_get_from_unreal_engine = message_queue_in

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
            self.message_queue_send_to_unreal_engine = message_queue_out
        if message_queue_in is not None:
            self.message_queue_get_from_unreal_engine = message_queue_in
        self.connected_event.set()

    def send_to_unreal_engine(self, msg):
        self.message_queue_send_to_unreal_engine.put_nowait(msg)

    def get_from_unreal_engine(self):
        res = asyncio.run(self.message_queue_get_from_unreal_engine.get())
        msg: UserInterfaceMsg = pickle.loads(res)
        return msg
