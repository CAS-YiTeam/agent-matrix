import os
import sys
import time
import uuid
import json
import platform
import pickle
import asyncio
import threading
import traceback
from loguru import logger
from queue import Queue
from fastapi import FastAPI, WebSocket
from agent_matrix.agent.agent_proxy import AgentProxy
from agent_matrix.agentcraft.agentcraft_proxy import AgentCraftProxy
from agent_matrix.msg.general_msg import GeneralMsg
from agent_matrix.msg.general_msg import UserInterfaceMsg
# from agent_matrix.matrix.matrix_userinterface_bridge import UserInterfaceBridge
from typing import List


class PythonMethod_AsyncConnectionMaintainer:
    """
    Class responsible for maintaining an asynchronous connection with an agent.

    Args:
        agent_id (str): The ID of the agent.
        websocket (WebSocket): The WebSocket connection.
        client_id (str): The ID of the client.

    Attributes:
        None

    Methods:
        maintain_agent_connection_forever: Maintains the agent connection indefinitely.

    """
    """
    A class that provides methods to create message queues and update connection information for agents and agentcraft interfaces.
    """

    def make_queue(self, agent_id, websocket, client_id):
        """
        Creates a message queue for the specified agent and updates the connection information.

        Args:
            agent_id (str): The ID of the agent.
            websocket: The websocket connection object.
            client_id: The ID of the client.

        Returns:
            tuple: A tuple containing the message queue for outgoing messages, the message queue for incoming messages, and the agent proxy object.
        """
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
        return message_queue_out, message_queue_in, agent_proxy

    async def maintain_agent_connection_forever(self, agent_id: str, websocket: WebSocket, client_id: str):
        async def wait_message_to_send(message_queue_out: asyncio.Queue, agent_proxy: AgentProxy):
            # 🚀 proxy agent -> matrix -> real agent
            msg_cnt = 0
            try:
                while True:
                    # 🕜 wait message from the proxy agent
                    msg: GeneralMsg = await message_queue_out.get()
                    msg_cnt += 1
                    logger.info('sending agent:', agent_id, '\tcnt:', msg_cnt, '\tcommand:', msg.command)
                    if msg.dst == 'matrix':
                        raise NotImplementedError()
                    else:
                        # send the message to the real agent
                        await websocket.send_bytes(pickle.dumps(msg))
            except Exception as e:
                traceback.print_exc()
                raise e


        async def receive_forever(message_queue_in: asyncio.Queue, agent_proxy: AgentProxy):
            # 🚀 real agent -> matrix -> proxy agent
            # 🚀 real agent -> matrix
            msg_cnt = 0
            try:
                while True:
                    # 🕜 wait websocket message from the real agent
                    msg: GeneralMsg = pickle.loads(await websocket.receive_bytes())
                    msg_cnt += 1
                    logger.info('receiving agent:', agent_id, '\tcnt:', msg_cnt, '\tcommand:', msg.command)
                    if msg.dst == 'matrix':
                        raise NotImplementedError()
                    else:
                        # deliver the message to the proxy agent
                        await message_queue_in.put(msg)
            except Exception as e:
                traceback.print_exc()
                raise e
        message_queue_out, message_queue_in, agent_proxy = self.make_queue(agent_id, websocket, client_id)
        t_x = asyncio.create_task(wait_message_to_send(message_queue_out, agent_proxy))
        t_r = asyncio.create_task(receive_forever(message_queue_in, agent_proxy))
        await t_x
        await t_r

from agent_matrix.agentcraft.agentcraft_fn import PythonMethod_AgentcraftHandler
class PythonMethod_AsyncConnectionMaintainer_AgentcraftInterface(PythonMethod_AgentcraftHandler):

    def make_queue_agentcraft_interface(self, agentcraft_interface, websocket, client_id):
        """
        Creates a message queue for the specified agentcraft interface and updates the connection information.

        Args:
            agentcraft_interface (str): The name of the agentcraft interface.
            websocket: The websocket connection object.
            client_id: The ID of the client.

        Returns:
            tuple: A tuple containing the message queue for outgoing messages, the message queue for incoming messages, and the agentcraft proxy object.
        """
        message_queue_out = asyncio.Queue()
        message_queue_in = asyncio.Queue()
        assert agentcraft_interface in self.agentcraft_interface_websocket_connections, f"agentcraft_interface {agentcraft_interface} not found in self.agentcraft_interface_websocket_connections"
        agentcraft_proxy: AgentCraftProxy = self.agentcraft_interface_websocket_connections[agentcraft_interface]
        agentcraft_proxy.update_connection_info(
            websocket=websocket,
            client_id=client_id,
            message_queue_out=message_queue_out,
            message_queue_in=message_queue_in
        )
        return message_queue_out, message_queue_in, agentcraft_proxy

    async def maintain_agentcraft_interface_connection_forever(self, agentcraft_interface_id: str, websocket: WebSocket, client_id: str):
        async def wait_message_to_send(message_queue_out: asyncio.Queue, agentcraft_proxy: AgentCraftProxy):
            # 🚀 proxy unreal engine client -> matrix -> real agentcraft unreal engine client
            msg_cnt = 0
            try:
                while True:
                    # 🕜 wait message from the proxy unreal engine client
                    msg: UserInterfaceMsg = await message_queue_out.get()
                    msg_cnt += 1
                    logger.info('sending agentcraft:', agentcraft_interface_id, '\tcnt:', msg_cnt, '\tcommand:', msg.command)
                    if msg.dst == 'matrix':
                        raise NotImplementedError()
                    else:
                        # send the message to the real agentcraft unreal engine client
                        await websocket.send_bytes(msg.json())
            except Exception as e:
                traceback.print_exc()
                raise e

        async def receive_forever(message_queue_in: asyncio.Queue, message_queue_out: asyncio.Queue, agentcraft_proxy: AgentCraftProxy):
            # 🚀 real agentcraft unreal engine client -> matrix -> proxy unreal engine client
            # 🚀 real agentcraft unreal engine client -> matrix
            msg_cnt:int = 0
            try:
                while True:
                    # 🕜 wait websocket message from the real agentcraft unreal engine client
                    msg: UserInterfaceMsg = UserInterfaceMsg.parse_raw(await websocket.receive_text())
                    msg_cnt += 1
                    logger.info(f'receiving agentcraft: {agentcraft_interface_id}, cnt: {msg_cnt}, command: {msg.command}')
                    if msg.dst == 'matrix':
                        # handle msg from agentcraft unreal engine client
                        await self.matrix_process_msg_from_agentcraft(msg, message_queue_out, agentcraft_proxy)
                    else:
                        # deliver the message to the proxy unreal engine client
                        await message_queue_in.put(msg)
            except Exception as e:
                traceback.print_exc()
                raise e
        message_queue_out, message_queue_in, agentcraft_proxy = self.make_queue_agentcraft_interface(agentcraft_interface_id, websocket, client_id)
        t_x = asyncio.create_task(wait_message_to_send(message_queue_out, agentcraft_proxy))
        t_r = asyncio.create_task(receive_forever(message_queue_in, message_queue_out, agentcraft_proxy))
        await t_x
        await t_r


class MasterMindWebSocketServer(PythonMethod_AsyncConnectionMaintainer, PythonMethod_AsyncConnectionMaintainer_AgentcraftInterface):

    def __init__(self) -> None:
        self.websocket_connections = {}
        self.agentcraft_interface_websocket_connections = {}
        pass

    async def long_task_01_wait_incoming_connection(self):
        # task 1 wait incoming agent connection
        logger.info("task 1 wait incoming agent connection")

        async def launch_websocket_server():
            app = FastAPI()

            @app.websocket("/ws_agent")
            async def _register_incoming_agents(websocket: WebSocket):
                """Register incoming (real) agent connections

                Args:
                    websocket (WebSocket): WebSocket

                Raises:
                    ValueError: ValueError
                """
                await websocket.accept()
                msg: GeneralMsg = pickle.loads(await websocket.receive_bytes())
                if msg.dst != "matrix" or msg.command != "connect_to_matrix":
                    raise ValueError()
                agent_id = msg.kwargs['agent_id']
                if agent_id in self.websocket_connections:
                    logger.warning(f"agent_id {agent_id}, connection established")
                    client_id = uuid.uuid4().hex
                    await self.maintain_agent_connection_forever(agent_id, websocket, client_id)
                else:
                    logger.warning(f"agent_id {agent_id} un-known, connection aborted")
                    await websocket.close()

            @app.websocket("/ws_agentcraft_interface")
            async def _register_incoming_agentcraft_interface(websocket: WebSocket):
                """Register incoming unreal engine connections

                Args:
                    websocket (WebSocket): WebSocket

                Raises:
                    ValueError: ValueError
                """
                await websocket.accept()
                msg: UserInterfaceMsg = UserInterfaceMsg.parse_raw(await websocket.receive_text())
                if msg.dst != "matrix" or msg.command != "connect_to_matrix":
                    raise ValueError()
                agentcraft_interface_id = msg.src
                if agentcraft_interface_id in self.agentcraft_interface_websocket_connections:
                    logger.error(f"agentcraft_interface_id {agentcraft_interface_id} duplicated connection, connection aborted.")
                    await websocket.close()
                else:
                    logger.info(f"agentcraft_interface_id {agentcraft_interface_id} connection initialize.")
                    client_id = uuid.uuid4().hex
                    self.agentcraft_interface_websocket_connections[agentcraft_interface_id] = AgentCraftProxy(
                        matrix=self,
                        agentcraft_interface_id=agentcraft_interface_id,
                        websocket=websocket,
                        client_id=client_id,
                    )
                    # send the message to the real agentcraft unreal engine client
                    msg.command = "connect_to_matrix.re"
                    msg.dst, msg.src = msg.src, msg.dst
                    msg.kwargs = client_id
                    await websocket.send_bytes(msg.json())
                    await self.maintain_agentcraft_interface_connection_forever(agentcraft_interface_id, websocket, client_id)

            logger.info("uvicorn starts")
            import uvicorn
            config = uvicorn.Config(app, host=self.host, port=self.port, log_level="info")
            server = uvicorn.Server(config)
            await server.serve()

        await launch_websocket_server()
        logger.info("uvicorn terminated")
