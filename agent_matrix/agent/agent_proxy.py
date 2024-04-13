import pickle
import asyncio
import threading
from loguru import logger
from fastapi import WebSocket
from agent_matrix.agent.interaction import InteractionManager
from agent_matrix.msg.general_msg import GeneralMsg
from typing import List
from typing_extensions import Self
from rich import print
from rich.panel import Panel

class BaseProxy(object):
    """
    一个Agent在母体中的代理对象
    这个类用来管理agent的连接信息
    包括websocket连接，client_id，message_queue等等
    """
    # from agent_matrix.matrix.matrix_mastermind import MasterMindMatrix
    def __init__(self,
                 matrix,
                 agent_id: str,
                 parent, # BaseProxy
                 websocket: WebSocket = None,
                 client_id: str = None,
                 message_queue_out: asyncio.Queue = None,
                 message_queue_in: asyncio.Queue = None):
        """
        初始化BaseProxy对象

        Parameters:
        - matrix: 母体对象
        - agent_id: 智能体的id
        - websocket: websocket连接对象
        - client_id: websocket连接的client_id
        - message_queue_out: 发送命令到真正的智能体进程的消息队列
        - message_queue_in: 从真正的智能体进程接收命令的消息队列
        """
        self.matrix = matrix
        self.direct_children: List[BaseProxy] = []
        self.parent: BaseProxy = parent
        self.connected_event = threading.Event()
        self.agent_id = agent_id
        self.proxy_id = '_proxy_' + agent_id
        self.websocket = websocket
        self.client_id = client_id
        self.message_queue_send_to_real_agent = message_queue_out
        self.message_queue_get_from_real_agent = message_queue_in
        self.agent_location = [0,0,0]
        self.event_triggers = {}
        self.interaction = InteractionManager(self)

    def update_connection_info(self,
                               websocket: WebSocket = None,
                               client_id: str = None,
                               message_queue_out: asyncio.Queue = None,
                               message_queue_in: asyncio.Queue = None):
        """
        更新连接信息

        Parameters:
        - websocket: websocket连接对象
        - client_id: websocket连接的client_id
        - message_queue_out: 发送命令到真正的智能体进程的消息队列
        - message_queue_in: 从真正的智能体进程接收命令的消息队列
        """
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
        """
        将命令发送到真正的智能体进程中

        Parameters:
        - msg: 要发送的命令
        """
        self.message_queue_send_to_real_agent.put_nowait(msg)

    def get_from_real_agent(self):
        """
        从真正的智能体进程中接收命令

        Returns:
        - msg: 接收到的命令
        """
        res = asyncio.run(self.message_queue_get_from_real_agent.get())
        msg: GeneralMsg = pickle.loads(res)
        return msg

    def wakeup_agent(self, msg):
        # 1. send msg to real agent
        # 2. wait 'on_agent_fin'
        msg.src = self.proxy_id
        msg.dst = self.agent_id
        msg.command = "on_agent_wakeup"
        self.send_to_real_agent(msg)

    def on_agent_fin(self, msg):
        self.wakeup_downstream_agent(msg)

    def wakeup_downstream_agent(self, msg):
        # find downstream agents
        downstream_agent_id_arr = list(self.interaction.get_downstream())
        if len(downstream_agent_id_arr) == 0:
            print(Panel(f"Agent 「{self.agent_id}」 --> 「 No More Downstream Agents! 」\n Final Message: \n {msg.print_string()}"))
        for downstream_agent_id in downstream_agent_id_arr:
            # send message to matrix
            downstream_agent = self.parent.search_children_by_id(downstream_agent_id)
            if (downstream_agent):
                print(Panel(f"Agent 「{self.agent_id}」 --> 「{downstream_agent.agent_id}」\n Delivering Message: \n {msg.print_string()}"))
                downstream_agent.wakeup_agent(msg)

    def register_trigger(self, command, event):
        self.event_triggers[command] = event

    def handle_command(self, msg: GeneralMsg):
        if msg.command in self.event_triggers.keys():
            self.event_triggers[msg.command].return_value = msg
            self.event_triggers[msg.command].set()
            return
        if msg.command == 'on_agent_fin':
            self.on_agent_fin(msg)
        else:
            raise ValueError(f"Unknown command {msg.command}")

    def send_msg_and_wait_reply(self, wait_command:str, msg: GeneralMsg):
        """ Send msg, then keep waiting until receiving expected reply.
        """
        self.send_to_real_agent(msg)
        self.temp_event = threading.Event()
        self.temp_event.return_value = None
        self.register_trigger(wait_command, self.temp_event)
        self.temp_event.wait()
        return self.temp_event.return_value

    def search_children_by_id(self, agent_id:str):
        for c in self.direct_children:
            if c.agent_id == agent_id:
                return c
        return None


class AgentProxy(BaseProxy):
    """This class handle direct api calls from the user.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # @user_fn
    def create_child_agent(self,
                           agent_id: str,
                           agent_class: str,
                           agent_kwargs: dict,
                           remote_matrix_kwargs: dict = None) -> Self:
        """ contact matrix to build new agent

        Args:
            agent_id (str): The ID of the new agent.
            agent_class (str): The class of the new agent.
            agent_kwargs (dict): The keyword arguments for creating the new agent.
            remote_matrix_kwargs (dict, optional): The keyword arguments for the remote matrix. Defaults to None.

        Returns:
            Self: The proxy of the child agent.

        """
        from agent_matrix.matrix.matrix_mastermind import MasterMindMatrix
        self.matrix: MasterMindMatrix
        parent = self
        child_agent_proxy = self.matrix.execute_create_agent(agent_id=agent_id,
                                                             agent_class=agent_class,
                                                             agent_kwargs=agent_kwargs,
                                                             remote_matrix_kwargs=remote_matrix_kwargs,
                                                             parent=parent)
        return child_agent_proxy

    # @user_fn
    def activate_agent(self):
        """Activates the agent.

        Raises:
            ValueError: If the reply message command is not "activate_agent.re".

        """
        msg = GeneralMsg(src=self.proxy_id, dst=self.agent_id, command="activate_agent", kwargs={}, need_reply=True)
        reply_msg = self.send_msg_and_wait_reply("activate_agent.re", msg)

    # @user_fn
    def activate_all_children(self):
        """Activates all the child agents.

        Raises:
            ValueError: If the reply message command is not "activate_agent.re".

        """
        for a in self.direct_children:
            msg = GeneralMsg(src=self.proxy_id, dst=a.agent_id, command="activate_agent", kwargs={}, need_reply=True)
            reply_msg = self.send_msg_and_wait_reply("activate_agent.re", msg)

    # @user_fn
    def get_children(self):
        """ Get all children of this agent (does not include itself).
        """
        children = []
        for agent in self.direct_children:
            children.append(agent)
            children.extend(agent.get_children())
        return children

    # @user_fn
    def create_edge_to(self, dst_agent_id:str):
        """ Make an agent its downstream agent.
        """
        # downstream_agent_proxy = self.matrix.find_agent_by_id(dst_agent)
        if isinstance(dst_agent_id, self.__class__):
            dst_agent_id = dst_agent_id.agent_id
        dst_agent_proxy =  self.parent.search_children_by_id(dst_agent_id)
        if dst_agent_proxy is None:
            raise ValueError(f"Cannot find agent {dst_agent_id}, or its parent is not the same with {self.agent_id}")
        self.interaction.create_edge(self.agent_id, dst_agent_id)
        return

    # @user_fn
    def wakeup(self, main_input):
        # 1. send msg to real agent
        # 2. wait 'on_agent_fin'
        msg =  GeneralMsg(
            src=self.proxy_id,
            dst=self.agent_id,
            command="on_agent_wakeup",
            kwargs={"main_input": main_input},
        )
        print(Panel(f"Agent 「{self.agent_id}」is waking up!\n Delivering Message: \n {msg.print_string()}"))
        self.send_to_real_agent(msg)

    # @user_fn
    def activate(self):
        # 1. send msg to real agent
        # 2. wait 'on_agent_fin'
        self.activate_agent()