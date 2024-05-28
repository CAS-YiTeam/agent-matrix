from agent_matrix.shared.cache_fn_io import file_cache
from agent_matrix.shared.config_loader import get_conf as agent_matrix_get_conf


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