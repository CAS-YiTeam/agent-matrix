import os
import sys
import time
import platform
import asyncio
import websockets
import pickle
import threading
from queue import Queue
from fastapi import FastAPI, WebSocket
from websockets.sync.client import connect
from agent_matrix.msg.general_msg import GeneralMsg
from threading import Event


class AgentBasic(object):

    def __init__(self, **kwargs) -> None:
        self.is_proxy = kwargs["is_proxy"]
        self.agent_id = kwargs["agent_id"]
        self.proxy_id = '_proxy_' + self.agent_id
        self.matrix_host = kwargs["matrix_host"]
        self.matrix_port = kwargs["matrix_port"]
        self._websocket_connection = None
        self._activation_event = Event()

    def __del__(self):
        try:
            self._websocket_connection.close()
        except:
            pass

    def _connect_to_matrix(self):
        # do not call this function directly
        host = self.matrix_host
        port = str(self.matrix_port)
        self._websocket_connection = connect(f"ws://{host}:{port}/ws_agent")
        msg = GeneralMsg(src=self.agent_id, dst="matrix", command="connect_to_matrix", kwargs={"agent_id": self.agent_id})
        self._send_msg(msg)

    def _send_msg(self, msg):
        # do not call this function directly
        self._websocket_connection.send(pickle.dumps(msg))

    def _recv_msg(self):
        # do not call this function directly
        msg: GeneralMsg = pickle.loads(self._websocket_connection.recv())
        return msg

    def _begin_acquire_command(self):
        # do not call this function directly
        while True:
            # block and wait for command
            msg = self._recv_msg()
            # handle command
            self._handle_command(msg)
            # reply if needed
            if msg.need_reply:
                msg.dst, msg.src = msg.src, msg.dst
                msg.command += '.re'
                msg.need_reply = False
                self._send_msg(msg)

    def _handle_command(self, msg: GeneralMsg):
        # do not call this function directly
        if msg.command == "activate_agent":
            self.activate_agent()
        elif msg.command == "deactivate_agent":
            self.deactivate_agent()
        elif msg.command == "on_agent_wakeup":
            # deal with the message from upstream
            downstream = self.on_agent_wakeup(msg.kwargs)
            # deliver message to downstream (don't worry, agent proxy will deal with it, e.g. chosing the right downstream agent)
            self.on_agent_fin(downstream, msg)
        else:
            raise NotImplementedError

    def on_agent_wakeup(self, kwargs):
        raise NotImplementedError

    def on_agent_fin(self, downstream, msg):
        msg.src = self.agent_id
        msg.dst = self.proxy_id
        msg.command = "on_agent_fin"
        msg.kwargs = downstream
        # keep level shift unchanged
        msg.level_shift = msg.level_shift
        self._send_msg(msg)

    def activate_agent(self):
        self._activation_event.set()

    def deactivate_agent(self):
        self._activation_event.clear()

    def agent_task_cycle(self):
        raise NotImplementedError

    def run_non_blocking(self):
        # start a new thread to run the agent task cycle
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

    def run(self):
        self.com_websocket = self._connect_to_matrix()
        threading.Thread(target=self._begin_acquire_command, daemon=True).start()
        while True:
            if self._activation_event.is_set():
                self.agent_task_cycle()
            else:
                self._activation_event.wait()
