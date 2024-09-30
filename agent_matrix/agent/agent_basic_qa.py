import time
import copy
from loguru import logger
from agent_matrix.agent.agent import Agent
from agent_matrix.shared.config_loader import get_conf as agent_matrix_get_conf
from agent_matrix.shared.llm_bridge import RequestLlmSubClass
from agent_matrix.msg.general_msg import print_msg_string, GeneralMsg
from rich.panel import Panel
from rich import print
try: logger.level("LLM", no=23)
except: pass
logger.add("llm.log", level="LLM", rotation="10 MB", retention="10 days")
PANEL_WIDTH = agent_matrix_get_conf("PANEL_WIDTH")
DEBUG_MOD = agent_matrix_get_conf("DEBUG_MOD")

class BasicQaAgent(Agent):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.activate = False
        self.kwargs = kwargs
        self.sys_prompt = kwargs.get("sys_prompt", "")
        self.need_history = kwargs.get("need_history", True)
        self.max_history_depth = kwargs.get("max_history_depth", 8)
        self.prompt_examples = kwargs.get("prompt_examples", "")
        self.query_construction = kwargs.get("query_construction", "Do your job according to the instructions.") # default: tell lm to do its job according to the sys_prompt
        self.llm_request = RequestLlmSubClass(kwargs.get("temperature", 0.5))
        self.start_callback = kwargs.get("start_callback", None)
        self.finish_callback = kwargs.get("finish_callback", None)
        self.mode = 'history_query'

    def agent_task_cycle(self):
        # do nothing
        time.sleep(2.0)
        return

    def on_children_fin(self, kwargs:dict, msg: GeneralMsg):
        return kwargs

    def on_agent_wakeup(self, kwargs:dict, msg: GeneralMsg):
        if self.start_callback is not None:
            kwargs, msg = self.start_callback(kwargs, msg)

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
            raw_output = self.llm_request.generate_llm_request(query=query, history=history_for_llm_request, sys_prompt=sys_prompt)
        elif self.mode == 'only_query':
            join_query_and_history = "\n".join(history_for_llm_request) + "\n\n" + query
            raw_output = self.llm_request.generate_llm_request(query=join_query_and_history, history=[], sys_prompt=sys_prompt)

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
        from agent_matrix.shared.conversation import downstream_input_template, generate_step
        # downstream_input_template = """「Step {NUM_STEP}, Agent {AGENT_ID}」:\n{AGENT_SPEECH}"""
        num_step = generate_step(downstream_history)
        downstream_input = downstream_input_template.format(AGENT_ID=self.agent_id, AGENT_SPEECH=raw_output, NUM_STEP=num_step)
        downstream_history.append(downstream_input)
        downstream = {"main_input": raw_output, "history": downstream_history}

        if self.finish_callback is not None:
            downstream = self.finish_callback(downstream, kwargs, msg)
        if DEBUG_MOD: input('Press Enter to continue...')
        # return
        return downstream

