import os
import sys
import time
import base64
import cloudpickle as pickle
import asyncio
import threading
import subprocess
from loguru import logger
from agent_matrix.agent.agent_proxy import AgentProxy
from agent_matrix.matrix.matrix_websocket import MasterMindWebSocketServer
from agent_matrix.shared.serialize import clean_up_unpickleble
from agent_matrix.shared.config_loader import get_conf as agent_matrix_get_conf
from rich.panel import Panel
from rich.text import Text
from rich import print
from rich.columns import Columns
PANEL_WIDTH = agent_matrix_get_conf("PANEL_WIDTH")

class MasterMindMatrix(MasterMindWebSocketServer):

    def __init__(self, host, port, dedicated_server=False):
        super().__init__()
        self.host = host
        self.port = port
        self.dedicated_server = dedicated_server
        self.direct_children = []
        self.agent_tree = None
        self.launch_agentcraft()

    def launch_agentcraft(self):
        logger.info("launch agentcraft")
        pass

    # async def long_task_03_exec_command_queue(self):
    #     # task 3 wait agent command, put them into task queue
    #     while True:
    #         await asyncio.sleep(1000)

    async def major_event_loop(self):
        long_task_01 = asyncio.create_task(self.long_task_01_wait_incoming_connection())
        # long_task_02 = asyncio.create_task(self.long_task_03_exec_command_queue())
        await long_task_01
        # await long_task_02

    def asyncio_event_loop(self):
        logger.info("begin event loop")
        asyncio.run(self.major_event_loop())

    def begin_event_loop_non_blocking(self):
        logger.info("begin event loop in new thread (non-blocking)")
        threading.Thread(target=self.asyncio_event_loop, daemon=True).start()
        return self

    def register_parent(self, parent: AgentProxy, agent_proxy: AgentProxy):
        # TODO
        if parent is None:
            self.direct_children.append(agent_proxy)
        else:
            parent.direct_children.append(agent_proxy)

    def create_agent(self,
                     agent_id: str,
                     agent_class: str,
                     agent_kwargs: dict,
                     remote_matrix_kwargs: dict = None,
                     parent: AgentProxy = None)->AgentProxy:
        """ 用阻塞的方式，创建一个智能体，并等待它连接到母体
        """
        logger.info(f"create agent {agent_id}")
        agent_launcher_abspath = os.path.join(
            os.path.dirname(__file__), '..', 'agent_launcher.py')
        agent_launcher_abspath = os.path.abspath(agent_launcher_abspath)
        assert os.path.exists(
            agent_launcher_abspath), f"agent_launcher not found: {agent_launcher_abspath}"

        if remote_matrix_kwargs is not None:
            # 连接非本地母体
            host = remote_matrix_kwargs["host"]
            port = remote_matrix_kwargs["port"]
            # TODO
            raise NotImplementedError()
        else:
            # 连接本地母体
            host = self.host
            port = self.port

            # 创建一个Agent在母体中的代理对象
            if parent is None:
                parent = self
            agent_proxy = AgentProxy(matrix=self, agent_id=agent_id, parent=parent, agent_kwargs=agent_kwargs)
            if agent_id in self.websocket_connections:
                logger.error(
                    f"agent_id `{agent_id}` already exists in self.websocket_connections")
                raise RuntimeError("Duplicate agent_id! " + f"agent_id `{agent_id}` already exists in self.websocket_connections")

            self.websocket_connections[agent_id] = agent_proxy
            self.register_parent(parent=parent, agent_proxy=agent_proxy)
            agent_kwargs = clean_up_unpickleble(agent_kwargs)
            # 启动一个子进程，用于启动一个智能体
            subprocess.Popen(
                args=(
                    sys.executable,
                    agent_launcher_abspath,
                    "--agent-id", agent_id,
                    "--agent-class", base64.b64encode(pickle.dumps(agent_class)),
                    "--matrix-host", str(host),
                    "--matrix-port", str(port),
                    "--agent-kwargs", base64.b64encode(pickle.dumps(agent_kwargs)), # if something goes wrong here, try non-debug / non-jupyter mode | 如果这里出现报错，且使用了Pydantic模型, 请尝试: 1.把自定义的Pydantic模型放到别的py源文件中，然后import试试
                )
            )

            # 🕜 接下来，我们需要等待智能体启动完成，并连接母体的websocket
            for i in reversed(range(30)):
                if i % 5 == 0:
                    logger.info(f"wait agent {agent_id} to connect to matrix, timeout in {i} seconds")
                agent_proxy.connected_event.wait(timeout=1)
                if agent_proxy.connected_event.is_set():
                    break

            if agent_proxy.connected_event.is_set():
                # 成功！
                logger.info(f"agent {agent_id} connected to matrix")
                self.build_tree(target="")
                # Render the tree
                print(Panel(Columns([Text("New Agent Up"), self.agent_tree]), width=PANEL_WIDTH))
                return agent_proxy
            else:
                logger.error(f"agent {agent_id} failed to connect to matrix within the timeout limit")
                return None

    def execute_create_agent(self, *args, **kwargs):
        """和create_agent一样
        """
        return self.create_agent(*args, **kwargs)

    def create_child_agent(self, *args, **kwargs):
        """创建自己的子智能体
        """
        kwargs['parent'] = self
        return self.create_agent(*args, **kwargs)

    def create_child_agent_sequential(self, agent_sequence:list):
        children = []
        for a_kwargs in agent_sequence:
            a_kwargs['parent'] = self
            new_a = self.create_agent(**a_kwargs)
            if children: children[-1].create_edge_to(new_a)
            children.append(new_a)
        return children

    def search_children_by_id(self, agent_id:str, blocking:bool=False):
        for c in self.get_all_agents_in_matrix():
            if c.agent_id == agent_id:
                return c
        # does not find
        if blocking:
            while True:
                for c in self.get_all_agents_in_matrix():
                    if c.agent_id == agent_id:
                        return c
                time.sleep(3)
        return None

    def get_all_agents_in_matrix(self, tree=None):
        all_agents = []
        for agent in self.direct_children:
            if tree is not None:
                if tree.target == agent.agent_id:
                    tree_branch = tree.add("[red]" + agent.agent_id + "[/red]")
                else:
                    tree_branch = tree.add(agent.agent_id)
                tree_branch.target = tree.target
            else:
                tree_branch = None
            all_agents.append(agent)
            all_agents.extend(agent.get_children(tree_branch))
        return all_agents

    def build_tree(self, target):
        from rich.tree import Tree
        # Create a Tree instance
        tree = Tree("Matrix")
        tree.target = target
        self.get_all_agents_in_matrix(tree)
        self.agent_tree = tree
        return self.agent_tree
