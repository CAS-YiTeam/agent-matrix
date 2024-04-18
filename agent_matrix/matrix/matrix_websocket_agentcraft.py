import pickle
import asyncio
import threading
import traceback
from loguru import logger
from queue import Queue
from fastapi import FastAPI, WebSocket
from agent_matrix.agentcraft.agentcraft_proxy import AgentCraftProxy
from agent_matrix.msg.general_msg import GeneralMsg
from agent_matrix.msg.ui_msg import UserInterfaceMsg
from typing import List

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
                    # logger.info('sending agentcraft:', agentcraft_interface_id, '\tcnt:', msg_cnt, '\tcommand:', msg.command)
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
                    # logger.info(f'receiving agentcraft: {agentcraft_interface_id}, cnt: {msg_cnt}, command: {msg.command}')
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

