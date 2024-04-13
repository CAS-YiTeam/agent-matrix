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
try:
    from websockets.sync.client import connect
except ImportError:
    raise ImportError("Import websockets failed, upgrade websockets by running: pip install websockets --upgrade")

from agent_matrix.msg.general_msg import GeneralMsg
from agent_matrix.agent.agent_basic import AgentBasic



class Agent(AgentBasic):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.activate = False

    def agent_task_cycle(self):
        print('Hi, you have to implement this function (Agent.agent_task_cycle) in your subclass.')
        time.sleep(1.0)

    def on_agent_wakeup(self, kwargs):
        print('Hi, you have to implement this function (Agent.on_agent_wakeup) in your subclass.')
        time.sleep(1.0)

class BasicQaAgent(Agent):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.activate = False
        self.kwargs = kwargs
        self.sys_prompt = kwargs.get("sys_prompt", "")
        import void_terminal as vt

        vt.set_conf(key="API_KEY", value="sk-123456789xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx123456789")
        vt.set_conf(key="LLM_MODEL", value="vllm-/home/hmp/llm/cache/Qwen1___5-32B-Chat(max_token=4096)")
        vt.set_conf(key="API_URL_REDIRECT", value="{'https://api.openai.com/v1/chat/completions': 'http://localhost:8000/v1/chat/completions'}")

    def agent_task_cycle(self):
        print('hello world')

    def on_agent_wakeup(self, kwargs):
        downstream_input = self.call_llm(kwargs["main_input"], [], self.sys_prompt)
        downstream = {"main_input": downstream_input}
        return downstream

    def call_llm(self, query, history, sys_prompt):
        import void_terminal as vt
        from void_terminal.request_llms.bridge_all import predict_no_ui_long_connection
        # default_chat_kwargs = {
        #     "inputs": "Hello there, are you ready?",
        #     "llm_kwargs": llm_kwargs,
        #     "history": [],
        #     "sys_prompt": "You are AI assistant",
        #     "observe_window": None,
        #     "console_slience": False,
        # }

        chat_kwargs = vt.get_chat_default_kwargs()
        chat_kwargs['inputs'] = query
        chat_kwargs['history'] = history
        chat_kwargs['sys_prompt'] = sys_prompt
        result = predict_no_ui_long_connection(**chat_kwargs)
        return result