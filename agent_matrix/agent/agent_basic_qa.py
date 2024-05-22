import time
import copy
from loguru import logger
from agent_matrix.agent.agent import Agent
from agent_matrix.shared.config_loader import get_conf as agent_matrix_get_conf
from agent_matrix.shared.cache_fn_io import file_cache
from agent_matrix.msg.general_msg import print_msg_string, GeneralMsg
from rich.panel import Panel
from rich import print
try: logger.level("LLM", no=23)
except: pass
logger.add("llm.log", level="LLM", rotation="10 MB", retention="10 days")
PANEL_WIDTH = agent_matrix_get_conf("PANEL_WIDTH")


class RequestLlmSubClass():

    def __init__(self, temperature) -> None:
        self.has_initialized = False
        self.temperature = temperature

    @staticmethod
    def llm_request(query, history, sys_prompt, temperature):
        import void_terminal as vt
        from void_terminal.request_llms.bridge_all import predict_no_ui_long_connection
        chat_kwargs = vt.get_chat_default_kwargs()
        chat_kwargs['inputs'] = query
        chat_kwargs['history'] = history
        chat_kwargs['sys_prompt'] = sys_prompt
        chat_kwargs['llm_kwargs']['temperature'] = temperature
        result = predict_no_ui_long_connection(**chat_kwargs)
        return result

    @staticmethod
    @file_cache(cache_dir="llm_cache")
    def cached_request(query, history, sys_prompt, temperature):
        return RequestLlmSubClass.llm_request(query, history, sys_prompt, temperature)

    def generate_llm_request(self, query, history, sys_prompt, use_debug_cache=False):
        if not self.has_initialized:
            import void_terminal as vt
            required_conf_array = ["API_KEY", "LLM_MODEL", "API_URL_REDIRECT"]
            for key in required_conf_array:
                if key not in vt.get_conf():
                    vt.set_conf(key=key, value=agent_matrix_get_conf(key))
        if use_debug_cache:
            result = self.cached_request(query, history, sys_prompt, self.temperature)
        else:
            result = RequestLlmSubClass.llm_request(query, history, sys_prompt, self.temperature)
        print("")   # print an empty line to separate the output
        return result

class BasicQaAgent(Agent):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.activate = False
        self.kwargs = kwargs
        self.sys_prompt = kwargs.get("sys_prompt", "")
        self.need_history = kwargs.get("need_history", True)
        self.max_history_depth = kwargs.get("max_history_depth", 8)
        self.prompt_examples = kwargs.get("prompt_examples", "")
        self.use_debug_cache = kwargs.get("use_debug_cache", False)
        self.query_construction = kwargs.get("query_construction", "Do your job according to the instructions.") # default: tell lm to do its job according to the sys_prompt
        self.llm_request = RequestLlmSubClass(kwargs.get("temperature", 0.5))
        self.mode = 'history_query'

    def agent_task_cycle(self):
        # do nothing
        time.sleep(60.0)
        return

    def on_children_fin(self, kwargs:dict, msg: GeneralMsg):
        return kwargs

    def on_agent_wakeup(self, kwargs:dict, msg: GeneralMsg):
        # 1. get history if there is any
        print_kwargs = copy.deepcopy(kwargs)
        history = kwargs.get("history", [])
        history_for_llm_request = []
        history_for_llm_request.extend(history)
        downstream_history = []
        downstream_history.extend(history)

        # 2. build query
        main_input = kwargs["main_input"]
        if "{MAIN_INPUT_PLACEHOLDER}" in self.query_construction:
            query = self.query_construction.format(MAIN_INPUT_PLACEHOLDER=main_input)
            if len(history_for_llm_request) >= 1 and (main_input in history_for_llm_request[-1]):
                # remove the last history if it is the same as the current input
                history_for_llm_request.pop(-1)
        else:
            query = self.query_construction

        # 3. fetch system prompt
        sys_prompt = self.sys_prompt

        # 4. complete history
        if not self.need_history:
            history_for_llm_request = []
            assert "{MAIN_INPUT_PLACEHOLDER}" in self.query_construction, "If you do not need history, you must have a `MAIN_INPUT_PLACEHOLDER` in the `query_construction` argument."
        else:
            if len(history_for_llm_request) > self.max_history_depth:
                history_for_llm_request = history_for_llm_request[-self.max_history_depth:]

        # 5. make the request
        if self.mode == 'history_query':
            raw_output = self.llm_request.generate_llm_request(query=query, history=history_for_llm_request, sys_prompt=sys_prompt, use_debug_cache=self.use_debug_cache)
        elif self.mode == 'only_query':
            join_query_and_history = "\n".join(history_for_llm_request) + "\n\n" + query
            raw_output = self.llm_request.generate_llm_request(query=join_query_and_history, history=[], sys_prompt=sys_prompt, use_debug_cache=self.use_debug_cache)
        self.agent_status = raw_output
        print_kwargs["upstream_input"] = print_kwargs.pop("main_input")
        print_kwargs.update(
            {
                "query": query,
                "history": history_for_llm_request,
                "sys_prompt": sys_prompt,
                "raw_output": raw_output,
            }
        )
        print(Panel(f"{print_msg_string(print_kwargs, msg)}", width=PANEL_WIDTH))
        print(Panel(f"{print_msg_string(print_kwargs, msg, auto_clip=False)}", width=PANEL_WIDTH), file=open("llm.log", "a", encoding='utf-8'))

        # 6. send the request downstream
        if len(downstream_history) == 0 or (main_input not in downstream_history[-1]):
            downstream_history.append(main_input)
        downstream_input = """Step {NUM_STEP}, Agent 「{AGENT_ID}」:\n{AGENT_SPEECH}"""
        downstream_input = downstream_input.format(AGENT_ID=self.agent_id, AGENT_SPEECH=raw_output, NUM_STEP=msg.num_step)
        downstream_history.append(downstream_input)
        downstream = {"main_input": raw_output, "history": downstream_history}

        # return
        return downstream

