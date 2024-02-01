import pickle
import asyncio
import threading
from loguru import logger
from fastapi import WebSocket
from agent_matrix.agent.interaction import InteractionBuilder
from agent_matrix.msg.general_msg import GeneralMsg
from typing import List
from typing_extensions import Self

class BaseProxy(object):
    """
    一个Agent在母体中的代理对象
    这个类用来管理agent的连接信息
    包括websocket连接，client_id，message_queue等等
    """

    def __init__(self,
                 matrix,
                 agent_id: str,
                 websocket: WebSocket = None,
                 client_id: str = None,
                 message_queue_out: asyncio.Queue = None,
                 message_queue_in: asyncio.Queue = None):
        # 与母体协调，创建新智能体，并建立与新智能体的连接
        self.matrix = matrix
        # 如果智能体嵌套了内层的智能体，那么这个列表中就会有内层智能体的代理
        self.direct_children: List[BaseProxy] = []
        # 当websocket连接成功后，会设置这个event
        self.connected_event = threading.Event()
        # 智能体的id
        self.agent_id = agent_id
        self.proxy_id = '_proxy_' + agent_id
        # websocket连接
        self.websocket = websocket
        # websocket连接的client_id
        self.client_id = client_id
        # 将命令发送到真正的智能体进程中
        self.message_queue_send_to_real_agent = message_queue_out
        # 从真正的智能体进程中接收命令
        self.message_queue_get_from_real_agent = message_queue_in

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
            self.message_queue_send_to_real_agent = message_queue_out
        if message_queue_in is not None:
            self.message_queue_get_from_real_agent = message_queue_in
        self.connected_event.set()

    def send_to_real_agent(self, msg):
        self.message_queue_send_to_real_agent.put_nowait(msg)

    def get_from_real_agent(self):
        res = asyncio.run(self.message_queue_get_from_real_agent.get())
        msg: GeneralMsg = pickle.loads(res)
        return msg


class AgentProxy(BaseProxy):
    """这个类用来管理agent的连接信息，包括websocket连接，client_id，message_queue等等
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.interaction_builder = InteractionBuilder(self)

    def create_child_agent(self,
                           agent_id: str,
                           agent_class: str,
                           agent_kwargs: dict,
                           remote_matrix_kwargs: dict = None) -> Self:
        """ 与母体协调，创建新智能体，并建立与新智能体的连接
        """
        from agent_matrix.matrix.mastermind_matrix import MasterMindMatrix
        self.matrix: MasterMindMatrix
        parent = self
        child_agent_proxy = self.matrix.execute_create_agent(agent_id=agent_id,
                                                             agent_class=agent_class,
                                                             agent_kwargs=agent_kwargs,
                                                             remote_matrix_kwargs=remote_matrix_kwargs,
                                                             parent=parent)
        return child_agent_proxy

    def activate_agent(self):
        msg = GeneralMsg(src=self.proxy_id, dst=self.agent_id, command="activate_agent", kwargs={}, need_reply=True)
        self.send_to_real_agent(msg)
        reply_msg = self.get_from_real_agent()
        if reply_msg.command != "activate_agent.re":
            raise ValueError()

    def activate_all_children(self):
        for a in self.direct_children:
            msg = GeneralMsg(src=self.proxy_id, dst=a.agent_id, command="activate_agent", kwargs={}, need_reply=True)
            self.send_to_real_agent(msg)
            reply_msg = self.get_from_real_agent()
            if reply_msg.command != "activate_agent.re":
                raise ValueError()