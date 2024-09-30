import pickle
import asyncio
import threading
import uuid
import copy
from loguru import logger
from fastapi import WebSocket
from agent_matrix.agent.interaction import InteractionManager
from agent_matrix.msg.general_msg import GeneralMsg, SpecialDownstreamSet, SpecialDownstream
from typing import List
from typing_extensions import Self
from rich import print
from rich.panel import Panel
from agent_matrix.shared.config_loader import get_conf as agent_matrix_get_conf
PANEL_WIDTH = agent_matrix_get_conf("PANEL_WIDTH")


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
                 message_queue_in: asyncio.Queue = None,
                 agent_kwargs: dict = None):
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
        self.agent_location = [0,0,0]
        self.agent_ue_class = "CharacterAgent"
        self.agent_status = ""
        self.agent_animation = "Standing"
        self.agent_activity = "inactive"
        self.agent_request = ""

        self.proxy_id = '_proxy_' + agent_id
        self.websocket = websocket
        self.agent_kwargs = agent_kwargs
        self.join_upstream = self.agent_kwargs.get("join_upstream", False)
        self.upstream_pending_register = {}
        self.client_id = client_id
        self.message_queue_send_to_real_agent = message_queue_out
        self.message_queue_get_from_real_agent = message_queue_in
        self.event_triggers = {}
        self.interaction = InteractionManager(self)
        self.allow_level_up = True
        self.wakeup_lock = threading.Lock()
        return

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        # 清理资源或处理异常
        pass

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
        return

    def send_to_real_agent(self, msg):
        """
        将命令发送到真正的智能体进程中

        Parameters:
        - msg: 要发送的命令
        """
        self.message_queue_send_to_real_agent.put_nowait(msg)
        return

    def get_from_real_agent(self):
        """
        从真正的智能体进程中接收命令

        Returns:
        - msg: 接收到的命令
        """
        res = asyncio.run(self.message_queue_get_from_real_agent.get())
        msg: GeneralMsg = pickle.loads(res)
        return msg

    def register_trigger(self, command, event):
        self.event_triggers[command] = event
        return

    def handle_command(self, msg: GeneralMsg):
        """
        Handle message from the real agent
        """
        if msg.command in self.event_triggers.keys():
            self.event_triggers[msg.command].return_value = msg
            self.event_triggers[msg.command].set()
            return
        if msg.command == 'on_update_status':
            setattr(self, msg.kwargs["property_name"], msg.kwargs["property_value"])
        elif msg.command == 'on_request_status':
            self.send_to_real_agent(self.generate_status_reply(msg))
        elif msg.command == 'on_agent_fin':
            self.___on_agent_finish___(msg)
        else:
            raise ValueError(f"Unknown command {msg.command}")
        return

    def generate_status_reply(self, msg):
        if msg.kwargs["property_name"] == "direct_children":
            from agent_matrix.msg.agent_msg import generate_agent_dict
            property_value = []
            for agent in self.direct_children:
                agent_dict = generate_agent_dict(agent)
                property_value.append(agent_dict)
        else:
            property_value = getattr(self, msg.kwargs["property_name"])
        msg = GeneralMsg(src=self.proxy_id, dst=self.agent_id, command="on_request_status.re",
                         kwargs={
                             "future_id": msg.kwargs["future_id"],
                             "property_name": msg.kwargs["property_name"],
                             "property_value": property_value
                         })
        return msg

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

    def get_children(self, tree=None):
        """ Get all children of this agent (does not include itself).
        """
        children = []
        for agent in self.direct_children:
            children.append(agent)
            if tree is not None:
                if tree.target == agent.agent_id:
                    tree_branch = tree.add("[red]" + agent.agent_id + "[/red]")
                else:
                    tree_branch = tree.add(agent.agent_id)
                tree_branch.target = tree.target
            else:
                tree_branch = None
            children.extend(agent.get_children(tree_branch))
        return children


class AgentProxyLogicFlow(BaseProxy):

    def _wakeup_downstream_agent_regular(self, msg):
        downstream_agent_id_arr = list(self.interaction.get_downstream())
        # has any downstream agent ?
        if len(downstream_agent_id_arr) == 0:
            # there is no downstream agent
            if (self.parent is self.matrix) or (self.allow_level_up is False):
                # this is the root agent, do not need to return to parent
                self._terminate_exe(msg)
            else:
                self._wakeup_parent(msg)
        else:
            # there is downstream agent
            for downstream_agent_id in downstream_agent_id_arr:
                self._wakeup_brother_agent(msg, downstream_agent_id)
        return

    def _terminate_exe(self, msg:GeneralMsg):
        msg.src = self.agent_id
        msg.level_shift = '→'
        msg.dst = 'No More Downstream Agents!'
        print(Panel(f"Agent 「{msg.src}」 --> 「{msg.dst}」\n Final Message: \n {msg.print_string()}", width=PANEL_WIDTH))
        print(Panel(self.matrix.build_tree(target=msg.dst), width=PANEL_WIDTH))
        self.matrix.terminate_event(msg.flow_uid, msg)
        return

    def wakeup_children(self, msg):
        # pick children
        if msg.children_select_override:
            selected_child = self.parent.search_children_by_id(msg.children_select_override)
        else:
            selected_child = self.direct_children[0]
        # raise error if no children selected
        if selected_child is None:
            raise ValueError(f"Cannot find downstream agent {msg.children_select_override}")
        # mark level as shift down
        msg.level_shift = '↓'
        # wake up its children
        msg.src = self.agent_id
        msg.dst = selected_child.agent_id
        # print(Panel(f"Agent 「{msg.src}」 --> Child ↓↓ 「{msg.dst}」\n Delivering Message: \n {msg.print_string()}"))
        print(Panel(self.matrix.build_tree(target=msg.dst), width=PANEL_WIDTH))
        selected_child.___on_agent_wakeup___(msg)
        return

    def _wakeup_parent(self, msg):
        if (self.parent is self.matrix) or (self.allow_level_up is False):
            # this is the root agent, do not need to return to parent
            self._terminate_exe(msg)
            return
        # deliver message to parent, let parent handle it
        msg.src = self.agent_id
        msg.dst = self.parent.agent_id
        msg.level_shift = '↑'
        # print(Panel(f"Agent 「{msg.src}」 --> Parent ↑↑ 「{msg.dst}」\n Delivering Message: \n {msg.print_string()}"))
        print(Panel(self.matrix.build_tree(target=msg.dst), width=PANEL_WIDTH))
        self.parent.___on_agent_wakeup___(msg)
        return

    def _wakeup_brother_agent(self, msg, downstream_agent_id):
        downstream_agent = self.parent.search_children_by_id(downstream_agent_id)
        if (downstream_agent):
            # send message to downstream agent
            msg.src = self.agent_id
            msg.dst = downstream_agent_id
            msg.level_shift = '→'
            # print(Panel(f"Agent 「{msg.src}」 --> 「{msg.dst}」\n Delivering Message: \n {msg.print_string()}"))
            print(Panel(self.matrix.build_tree(target=msg.dst), width=PANEL_WIDTH))
            downstream_agent.___on_agent_wakeup___(msg)
        return

    def wakeup_downstream_agent(self, msg: GeneralMsg):
        # find downstream agents
        downstream_override = msg.downstream_override
        downstream_split_override = msg.downstream_split_override

        if downstream_override:
            # special case: dynamically override downstream
            if downstream_override == SpecialDownstreamSet.auto_downstream:
                self._wakeup_downstream_agent_regular(msg)
            elif downstream_override == SpecialDownstreamSet.return_to_parent:
                self._wakeup_parent(msg)
            else:
                self._wakeup_brother_agent(msg, downstream_override)

        elif downstream_split_override:
            # special case: dynamically split & override downstream
            downstream_see_you_again_uid_arr = []
            for _kwargs, _downstream_override in zip(msg.kwargs, msg.downstream_split_override):
                downstream_see_you_again_uid = msg.flow_uid + uuid.uuid4().hex
                downstream_see_you_again_uid_arr.append(downstream_see_you_again_uid)

            for _kwargs, _downstream_override, downstream_see_you_again_uid in zip(msg.kwargs, msg.downstream_split_override, downstream_see_you_again_uid_arr):
                msg_split: GeneralMsg = copy.deepcopy(msg)
                msg_split.downstream_see_you_again_uid.append(downstream_see_you_again_uid)
                msg_split.downstream_see_you_again_waitlist.append(downstream_see_you_again_uid_arr)
                msg_split.kwargs = _kwargs
                msg_split.downstream_override = _downstream_override
                msg_split.downstream_split_override = None
                self.wakeup_downstream_agent(msg_split)

        else:
            # normal case
            self._wakeup_downstream_agent_regular(msg)

        return

    def ___on_agent_wakeup___(self, msg: GeneralMsg):
        """ AT HERE, THE AGENT BEGIN TO WORK !
                    ⏰⏰⏰⏰⏰
        """

        # join flow (that is splited before by `downstream_split_override`)
        if self.join_upstream:
            with self.wakeup_lock:
                _continue = self.join_upstream_condition(msg)
                if not _continue: return

        self.agent_activity = "wakeup"
        msg.src = self.proxy_id
        msg.dst = self.agent_id
        msg.command = "on_agent_wakeup"
        self.send_to_real_agent(msg)
        return

    def join_upstream_condition(self, msg: GeneralMsg)->bool:
        # is this the first?
        if msg.flow_uid not in self.upstream_pending_register:
            self.upstream_pending_register[msg.flow_uid] = []
        # add to register
        downstream_see_you_again_uid = msg.downstream_see_you_again_uid[-1]
        self.upstream_pending_register[msg.flow_uid].append([downstream_see_you_again_uid, msg])
        # all pending uids
        all_pending_uids = []
        for see_you_again_uid, _ in self.upstream_pending_register[msg.flow_uid]:
            all_pending_uids.append(see_you_again_uid)
        # print debug
        n_arrive = len(self.upstream_pending_register[msg.flow_uid])
        n_total = len(msg.downstream_see_you_again_waitlist[-1])
        logger.debug(f'join upstream for {msg.flow_uid}, waiting for {n_arrive} / {n_total}.')
        # is everything in wait list satisfied?
        for see_you_again_uid in msg.downstream_see_you_again_waitlist[-1]:
            if see_you_again_uid not in all_pending_uids:
                # if not satisfied, return and wait
                return False
        # if the for loop is passed, we are clear to go
        msg.downstream_see_you_again_msg_arr: List[GeneralMsg] = []     # type: ignore
        msg.downstream_see_you_again_msg_arr = [msg for _, msg in self.upstream_pending_register[msg.flow_uid]]
        # msg.downstream_see_you_again_waitlist: List[List[str]]          # type: ignore
        msg.downstream_see_you_again_waitlist.pop(-1)
        # msg.downstream_see_you_again_uid: List[str] = []                # type: ignore
        msg.downstream_see_you_again_uid.pop(-1)
        self.upstream_pending_register.pop(msg.flow_uid)
        return True

    def ___on_agent_finish___(self, msg):
        """ AT HERE, THE AGENT FINISH WORK !
                    🎉🎉🎉🎉🎉
        """
        self.agent_activity = "sleeping"
        if len(self.direct_children) == 0:
            # no children, simple case, now turn to follow downstream agents (or its own parent)
            self.wakeup_downstream_agent(msg)
            return

        # already called children, now turn to follow downstream agents (or its own parent)
        if msg.call_children_again:
            msg.call_children_again = False
            self.wakeup_children(msg)
            return

        if msg.level_shift == '↑':
            self.wakeup_downstream_agent(msg)
            return

        # has children, need to wake up children
        # now, assert
        assert (msg.level_shift == '→' or msg.level_shift == '↓')
        self.wakeup_children(msg)
        # do not need to turn to follow downstream agents, this agent is not done yet !
        return




class AgentProxy(AgentProxyLogicFlow):
    """This class handle direct api calls from the user.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)



    # @user_fn
    def create_child_agent(self,
                           agent_id: str,
                           agent_class: str,
                           agent_kwargs: dict,
                           remote_matrix_kwargs: dict = None,
                           blocking:bool = True) -> Self:
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
        if blocking:
            child_agent_proxy = self.matrix.execute_create_agent(agent_id=agent_id,
                                                                agent_class=agent_class,
                                                                agent_kwargs=agent_kwargs,
                                                                remote_matrix_kwargs=remote_matrix_kwargs,
                                                                parent=parent)
            return child_agent_proxy
        else:
            # async call, create new thread to do this, do not wait
            import threading
            t = threading.Thread(target=self.matrix.execute_create_agent,
                                    args=(agent_id, agent_class, agent_kwargs, remote_matrix_kwargs, parent))
            t.start()
            return None


    # @user_fn
    def create_child_agent_sequential(self, agent_sequence:list):
        children = []
        for a_kwargs in agent_sequence:
            new_a = self.create_agent(**a_kwargs)
            if children: children[-1].create_edge_to(new_a)
            children.append(new_a)
        return children

    # @user_fn
    def create_agent(self, *args, **kwargs) -> Self:
        return self.create_child_agent(*args, **kwargs)

    # @user_fn
    def create_downstream_agent(self, *args, **kwargs) -> Self:
        import copy
        # search downstream agents in kwargs
        if kwargs.get("agent_kwargs", {}).get("downstream_options", None) is not None:
            downstream_options = kwargs["agent_kwargs"]["downstream_options"]
        elif kwargs.get("agent_kwargs", {}).get("downstream_options", None) is not None:
            downstream_options = kwargs["agent_kwargs"]["downstream_agents"]
        else:
            downstream_options = []
        downstream_options = copy.copy(downstream_options)

        # create new agent
        new_agent = self.parent.create_child_agent(*args, **kwargs)

        # create edge to downstream agents
        for d in downstream_options:
            if not isinstance(d, SpecialDownstream):
                new_agent.create_edge_to(d)

        # create edge to new agent
        self.create_edge_to(new_agent.agent_id)
        return new_agent

    # @user_fn
    def activate_agent(self):
        """Activates the agent.

        Raises:
            ValueError: If the reply message command is not "activate_agent.re".

        """
        msg = GeneralMsg(src=self.proxy_id, dst=self.agent_id, command="activate_agent", kwargs={}, need_reply=True)
        reply_msg = self.send_msg_and_wait_reply("activate_agent.re", msg)
        self.agent_activity = "active"

    # @user_fn
    def activate_all_children(self):
        """Activates all the child agents.

        Raises:
            ValueError: If the reply message command is not "activate_agent.re".

        """
        for a in self.direct_children:
            a.activate_agent()
            # msg = GeneralMsg(src=self.proxy_id, dst=a.agent_id, command="activate_agent", kwargs={}, need_reply=True)
            # reply_msg = self.send_msg_and_wait_reply("activate_agent.re", msg)
            # a.agent_activity = "active"


    # @user_fn
    def create_edge_to(self, dst_agent_id:str):
        """ Make an agent its downstream agent.
        """
        if isinstance(dst_agent_id, list):
            for d in dst_agent_id:
                if not isinstance(d, str): d = d.agent_id
                # if d != auto_downstream: self.create_edge_to(d)
            return
        if isinstance(dst_agent_id, self.__class__):
            dst_agent_id = dst_agent_id.agent_id
        if not isinstance(dst_agent_id, str):
            raise ValueError(f"dst_agent_id must be a string, but got {dst_agent_id}")
        # downstream_agent_proxy = self.matrix.find_agent_by_id(dst_agent)
        if isinstance(dst_agent_id, self.__class__):
            dst_agent_id = dst_agent_id.agent_id
        dst_agent_proxy =  self.parent.search_children_by_id(dst_agent_id)
        if dst_agent_proxy is None:
            raise ValueError(f"Cannot find agent {dst_agent_id}, or its parent is not the same with {self.agent_id}")
        self.interaction.create_edge(self.agent_id, dst_agent_id)
        return

    # @user_fn
    def set_downstream_agent(self, dst_agent_id:str):
        self.create_edge_to(dst_agent_id)

    # @user_fn
    def activate(self):
        # 1. send msg to real agent
        # 2. wait '___on_agent_finish___'
        if self.agent_activity == "active": return
        self.activate_agent()

    # @user_fn
    def wakeup(self, main_input):
        flow_uid = uuid.uuid4().hex
        msg = GeneralMsg(
            flow_uid=flow_uid,
            src=self.proxy_id,
            dst=self.agent_id,
            command="on_agent_wakeup",
            kwargs={
                "main_input": main_input,
                "history": [main_input,],
            },
        )
        wait_result_handler = self.matrix.create_event(flow_uid)
        msg.src = 'user'
        msg.dst = self.agent_id
        # print(Panel(f"Agent 「{self.agent_id}」is waking up! \n Delivering Message: \n {msg.print_string()}"))
        print(Panel(self.matrix.build_tree(target=msg.dst), width=PANEL_WIDTH))
        self.___on_agent_wakeup___(msg)
        return wait_result_handler

    # @user_fn
    def test_agent(self, main_input):
        self.wakeup(main_input)