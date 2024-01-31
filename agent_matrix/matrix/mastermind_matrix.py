import os
import sys
import time
import json
import platform
import pickle
import asyncio
import threading
import subprocess
from loguru import logger
from queue import Queue
from fastapi import FastAPI, WebSocket
from agent_matrix.agent_proxy import AgentProxy


class MasterMindWebSocketServer():

    def __init__(self) -> None:
        self.websocket_connections = {}
        pass

    async def maintain_agent_connection_forever(self, agent_id: str, websocket: WebSocket, client_id: str):
        # send
        async def wait_message_to_send(message_queue_out: asyncio.Queue, agent_proxy: AgentProxy):
            msg_cnt = 0
            while True:
                kwargs = await message_queue_out.get()
                msg_cnt += 1
                logger.info('sending client:', client_id, '\tcnt:',
                            msg_cnt, '\tcontent:', kwargs)
                await websocket.send(kwargs)

        # receive
        async def receive_forever(message_queue_in: asyncio.Queue, agent_proxy: AgentProxy):
            msg_cnt = 0
            while True:
                kwargs = await websocket.receive_text()
                msg_cnt += 1
                logger.info('receiving client:', client_id,
                            '\tcnt:', msg_cnt, '\tcontent:', kwargs)
                await message_queue_in.put(kwargs)

        message_queue_out = asyncio.Queue()
        message_queue_in = asyncio.Queue()
        assert agent_id in self.websocket_connections, f"agent_id {agent_id} not found in self.websocket_connections"
        agent_proxy: AgentProxy = self.websocket_connections[agent_id]
        agent_proxy.update_connection_info(
            websocket=websocket,
            client_id=client_id,
            message_queue_out=message_queue_out,
            message_queue_in=message_queue_in
        )
        t_x = asyncio.create_task(
            wait_message_to_send(message_queue_out, agent_proxy))
        t_r = asyncio.create_task(
            receive_forever(message_queue_in, agent_proxy))
        await t_x
        await t_r

    async def long_task_01_wait_incoming_connection(self):
        # task 1 wait incoming agent connection
        logger.info("task 1 wait incoming agent connection")

        async def launch_websocket_server():
            app = FastAPI()

            @app.websocket("/ws_agent")
            async def _register_incoming_agents(websocket: WebSocket, client_id: str):
                await websocket.accept()
                kwargs = await websocket.receive_text()
                kwargs = pickle.loads(kwargs)
                agent_id = kwargs['agent_id']
                if agent_id in self.websocket_connections:
                    logger.warning(
                        f"agent_id {agent_id}, connection established")
                    await self.maintain_agent_connection_forever(agent_id, websocket, client_id)
                else:
                    logger.warning(
                        f"agent_id {agent_id} un-known, connection aborted")
                    await websocket.close()

            @app.websocket("/ws_sub_matrix")
            async def _register_incoming_sub_matrix(websocket: WebSocket):
                await websocket.accept()
                data = await websocket.receive_text()
                raise NotImplementedError()
                self.connected_sub_matrix.append(
                    SubMatrixProxy(websocket=websocket, data=data))

            logger.info("uvicorn starts")
            import uvicorn
            config = uvicorn.Config(
                app, host=self.host, port=self.port, log_level="info")
            server = uvicorn.Server(config)
            await server.serve()

        await launch_websocket_server()
        logger.info("uvicorn terminated")


class MasterMindMatrix(MasterMindWebSocketServer):

    def __init__(self, host, port, dedicated_server=False):
        self.host = host
        self.port = port
        self.dedicated_server = dedicated_server
        self.direct_children = []
        self.launch_agentcraft()

    def launch_agentcraft(self):
        logger.info("launch agentcraft")
        pass

    async def long_task_03_exec_command_queue(self):
        # task 3 wait agent command, put them into task queue
        while True:
            await asyncio.sleep(1000)

    async def major_event_loop(self):
        long_task_01 = asyncio.create_task(
            self.long_task_01_wait_incoming_connection())
        long_task_02 = asyncio.create_task(
            self.long_task_03_exec_command_queue())
        await long_task_01
        await long_task_02

    def begin_event_loop(self):
        logger.info("begin event loop")
        asyncio.run(self.major_event_loop())

    def begin_event_loop_non_blocking(self):
        logger.info("begin event loop in new thread (non-blocking)")
        threading.Thread(target=self.begin_event_loop, daemon=True).start()

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
                     parent: AgentProxy = None):
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

            # 创建一个Websocket连接代理
            agent_proxy = AgentProxy(matrix=self, agent_id=agent_id)
            if agent_id in self.websocket_connections:
                logger.error(
                    f"agent_id {agent_id} already exists in self.websocket_connections")
                raise RuntimeError()

            self.websocket_connections[agent_id] = agent_proxy
            self.register_parent(parent=parent, agent_proxy=agent_proxy)
            # 启动一个子进程，用于启动一个智能体
            subprocess.Popen(
                args=(
                    sys.executable, agent_launcher_abspath,
                    "--agent-id", agent_id,
                    "--agent-class", agent_class,
                    "--matrix-host", host,
                    "--matrix-port", port,
                    "--agent-kwargs", json.dumps(agent_kwargs),
                )
            )

            # 接下来，我们需要等待智能体启动完成，并连接母体的websocket
            for i in reversed(range(30)):
                logger.info(
                    f"wait agent {agent_id} to connect to matrix, timeout in {i} seconds")
                agent_proxy.connected_event.wait(timeout=1)
                if agent_proxy.connected_event.is_set():
                    break

            if agent_proxy.connected_event.is_set():
                # 成功！
                logger.info(f"agent {agent_id} connected to matrix")
                return agent_proxy
            else:
                logger.error(
                    f"agent {agent_id} failed to connect to matrix within the timeout limit")
                return None

    def execute_create_agent(self, **kwargs):
        """和create_agent一样
        """
        self.create_agent(**kwargs)

    def create_child_agent(self, **kwargs):
        """创建自己的子智能体
        """
        kwargs['parent'] = self
        self.create_agent(**kwargs)
