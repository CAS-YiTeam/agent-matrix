import time
from agent_matrix.agent.agent import Agent

class BasicQaAgent(Agent):
    # #
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
    # #
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.activate = False
        self.kwargs = kwargs
        self.sys_prompt = kwargs.get("sys_prompt", "")
        self.query_construction = kwargs.get("query_construction", "Do your job according to the instructions.") # default: tell lm to do its job according to the sys_prompt
        self.llm_request = self.RequestLlmSubClass()

    def agent_task_cycle(self):
        time.sleep(60.0)

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

        # 5. make the request
        _raw_downstream_input = self.llm_request.generate_llm_request(query=query, history=history, sys_prompt=sys_prompt)

        # 6. send the request downstream
        downstream_input = """「{AGENT_ID}」:\n{AGENT_SPEECH}"""
        downstream_input = downstream_input.format(AGENT_ID=self.agent_id, AGENT_SPEECH=_raw_downstream_input)
        downstream = {"main_input": downstream_input, "history": history}

        # We do NOT append the downstream_input to the history,
        # it is the responsibility of the downstream agent to do so!
        # history.append(downstream_input)

        # return
        return downstream

    def call_llm(self, query, history, sys_prompt):
        return