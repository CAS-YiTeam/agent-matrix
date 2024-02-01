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


_websocket_connection = connect(f"ws://127.0.0.1:10101/ws_agent")
_websocket_connection