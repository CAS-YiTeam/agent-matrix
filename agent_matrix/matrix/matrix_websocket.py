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
from agent_matrix.msg.ui_msg import UserInterfaceMsg
# from agent_matrix.matrix.matrix_userinterface_bridge import UserInterfaceBridge
from typing import List
from agent_matrix.matrix.matrix_websocket_agent import PythonMethod_AsyncConnectionMaintainer
from agent_matrix.matrix.matrix_websocket_agentcraft import PythonMethod_AsyncConnectionMaintainer_AgentcraftInterface

class FutureEvent(threading.Event):
    def __init__(self) -> None:
        super().__init__()
        self.return_value = None

    def terminate(self, return_value):
        self.return_value = return_value
        self.set()

    def wait_and_get_result(self):
        self.wait()
        return self.return_value

class MasterMindWebSocketServer(PythonMethod_AsyncConnectionMaintainer, PythonMethod_AsyncConnectionMaintainer_AgentcraftInterface):

    def __init__(self) -> None:
        self.websocket_connections = {}
        self.agentcraft_interface_websocket_connections = {}
        self._event_hub = {}
        pass

    def create_event(self, event_name: str):
        self._event_hub[event_name] = FutureEvent()
        return self._event_hub[event_name]

    def terminate_event(self, event_name: str, msg:GeneralMsg):
        self._event_hub[event_name].terminate(return_value = msg)
        return

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

            # logger.info("uvicorn starts")
            import uvicorn
            config = uvicorn.Config(app, host=self.host, port=self.port, log_level="error")
            server = uvicorn.Server(config)
            await server.serve()

        await launch_websocket_server()
        logger.info("uvicorn terminated")
