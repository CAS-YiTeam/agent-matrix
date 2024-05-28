import time
import re
from loguru import logger
from agent_matrix.agent.agent import Agent
from agent_matrix.shared.config_loader import get_conf as agent_matrix_get_conf
logger.level("LLM", no=23)
logger.add("llm.log", level="LLM", rotation="10 MB", retention="10 days")


class ExtractionAgent(Agent):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.activate = False
        self.kwargs = kwargs
        self.sys_prompt = kwargs.get("sys_prompt", "")
        self.need_history = kwargs.get("need_history", True)
        self.prompt_examples = kwargs.get("prompt_examples", "")
        self.query_construction = kwargs.get("query_construction", "Do your job according to the instructions.") # default: tell lm to do its job according to the sys_prompt
        self.extraction_wrap = kwargs.get("extraction_wrap", ["```", "```"])    # find first encountered instance of this wrap
        self.no_match_exception = "No match found."

    def agent_task_cycle(self):
        # do nothing
        time.sleep(60.0)

    def on_children_fin(self, kwargs, msg):
        return kwargs

    def on_agent_wakeup(self, kwargs, msg):
        # 1. get history if there is any
        history = kwargs.get("history", [])

        # 2. build query
        main_input = kwargs["main_input"]
        query = self.query_construction.format(MAIN_INPUT_PLACEHOLDER=main_input)

        # 3. fetch system prompt
        sys_prompt = self.sys_prompt

        # 4. complete history
        history.append(main_input)
        history_for_llm_request = history
        if not self.need_history:
            history_for_llm_request = []

        # 5. send the request downstream
        downstream_input =  main_input
        pattern = re.compile(self.extraction_wrap[0] + r'(.*?)' + self.extraction_wrap[-1], re.DOTALL)

        try:
            # example: main_input = "hihi```john```."
            found_match = pattern.search(main_input).group(1)
        except:
            found_match = self.no_match_exception
            pass

        # downstream_input = """Agent 「{AGENT_ID}」:\n{AGENT_SPEECH}"""
        downstream_input = """{AGENT_SPEECH}"""
        downstream_input = downstream_input.format(AGENT_ID=self.agent_id, AGENT_SPEECH=found_match)
        downstream = {"main_input": downstream_input, "history": history}

        # return
        return downstream

