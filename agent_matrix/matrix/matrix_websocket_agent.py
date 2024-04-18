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
from agent_matrix.msg.ui_msg import UserInterfaceMsg
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
                    # logger.info(f'sending agent: {agent_id} \tcnt: {msg_cnt} \tcommand: {msg.command}')
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
                    # logger.info('receiving agent:', agent_id, '\tcnt:', msg_cnt, '\tcommand:', msg.command)
                    if msg.dst == 'matrix':
                        raise NotImplementedError()
                    else:
                        # deliver the message to the proxy agent
                        await message_queue_in.put(msg)
                        # notify the proxy agent to handle the message
                        agent_proxy.handle_command(msg)
            except Exception as e:
                traceback.print_exc()
                raise e
        message_queue_out, message_queue_in, agent_proxy = self.make_queue(agent_id, websocket, client_id)
        t_x = asyncio.create_task(wait_message_to_send(message_queue_out, agent_proxy))
        t_r = asyncio.create_task(receive_forever(message_queue_in, agent_proxy))
        await t_x
        await t_r
