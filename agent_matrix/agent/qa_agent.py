import time
from loguru import logger
from agent_matrix.agent.agent import Agent
from shared.config_loader import get_conf as agent_matrix_get_conf
logger.level("LLM", no=23)
logger.add("llm.log", level="LLM", rotation="10 MB", retention="10 days")


class RequestLlmSubClass():
    def __init__(self) -> None:
        self.has_initialized = False

    def generate_llm_request(self, query, history, sys_prompt):
        if not self.has_initialized:
            import void_terminal as vt
            required_conf_array = ["API_KEY", "LLM_MODEL", "API_URL_REDIRECT"]
            for key in required_conf_array:
                if key not in vt.get_conf():
                    vt.set_conf(key=key, value=agent_matrix_get_conf(key))
        import void_terminal as vt
        from void_terminal.request_llms.bridge_all import predict_no_ui_long_connection
        chat_kwargs = vt.get_chat_default_kwargs()
        chat_kwargs['inputs'] = query
        chat_kwargs['history'] = history
        chat_kwargs['sys_prompt'] = sys_prompt
        result = predict_no_ui_long_connection(**chat_kwargs)
        print("")   # print an empty line to separate the output
        return result

class BasicQaAgent(Agent):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.activate = False
        self.kwargs = kwargs
        self.sys_prompt = kwargs.get("sys_prompt", "")
        self.need_history = kwargs.get("need_history", True)
        self.prompt_examples = kwargs.get("prompt_examples", "")
        self.query_construction = kwargs.get("query_construction", "Do your job according to the instructions.") # default: tell lm to do its job according to the sys_prompt
        self.llm_request = RequestLlmSubClass()

    def agent_task_cycle(self):
        time.sleep(60.0)

    def on_children_fin(self, kwargs):
        return kwargs

    def on_agent_wakeup(self, kwargs):
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

        # 5. make the request
        _raw_downstream_input = self.llm_request.generate_llm_request(query=query, history=history_for_llm_request, sys_prompt=sys_prompt)
        logger.log(
            "LLM",
            f""">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"""
            f"""\n\n***query: ***\n\n{query}"""
            f"""\n\n***sys_prompt: ***\n\n{sys_prompt}"""
            f"""\n\n***history: ***\n\n{history_for_llm_request}"""
            f"""\n\n***raw_output: ***\n\n{_raw_downstream_input}\n"""
            f"""<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"""
        )

        # 6. send the request downstream
        downstream_input = """Agent 「{AGENT_ID}」:\n{AGENT_SPEECH}"""
        downstream_input = downstream_input.format(AGENT_ID=self.agent_id, AGENT_SPEECH=_raw_downstream_input)
        downstream = {"main_input": downstream_input, "history": history}

        # We do NOT append the downstream_input to the history,
        # it is the responsibility of the downstream agent to do so!
        # history.append(downstream_input)

        # return
        return downstream

