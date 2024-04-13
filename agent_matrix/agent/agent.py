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
        time.sleep(60.0)

    def on_agent_wakeup(self, kwargs):
        print('Hi, you have to implement this function (Agent.on_agent_wakeup) in your subclass.')
        time.sleep(60.0)

class BasicQaAgent(Agent):

    class RequestLlmSubClass():
        def __init__(self) -> None:
            self.has_initialized = False

        def generate_llm_request(self, query, history, sys_prompt):
            if not self.has_initialized:
                import void_terminal as vt
                vt.set_conf(key="API_KEY", value="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                vt.set_conf(key="LLM_MODEL", value="vllm-/home/hmp/llm/cache/Qwen1___5-32B-Chat(max_token=4096)")
                vt.set_conf(key="API_URL_REDIRECT", value='{"https://api.openai.com/v1/chat/completions": "http://172.18.116.161:8000/v1/chat/completions"}')
            import void_terminal as vt
            from void_terminal.request_llms.bridge_all import predict_no_ui_long_connection
            chat_kwargs = vt.get_chat_default_kwargs()
            chat_kwargs['inputs'] = query
            chat_kwargs['history'] = history
            chat_kwargs['sys_prompt'] = sys_prompt
            result = predict_no_ui_long_connection(**chat_kwargs)
            print("")   # print an empty line to separate the output
            return result

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.activate = False
        self.kwargs = kwargs
        self.sys_prompt = kwargs.get("sys_prompt", "")
        self.llm_request = self.RequestLlmSubClass()

    def agent_task_cycle(self):
        time.sleep(60.0)

    def on_agent_wakeup(self, kwargs):
        downstream_input = self.llm_request.generate_llm_request(query=kwargs["main_input"], history=[], sys_prompt=self.sys_prompt)
        downstream = {"main_input": downstream_input}
        return downstream

    def call_llm(self, query, history, sys_prompt):
        return