from agent_matrix.msg.general_msg import GeneralMsg
from agent_matrix.agent.agent_basic_qa import BasicQaAgent
from textwrap import dedent
from loguru import logger
import json
import os


class StructuredOutputAgent(BasicQaAgent):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.schema = kwargs.get("schema", None)
        self.max_history_depth = kwargs.get("max_history_depth", 2)
        self.structure_agent_type = "extract_message" # "extract_message" or "according_to_query_construction"

        if self.structure_agent_type == "extract_message":
            self.format_instruction = kwargs.get("format_instruction", "You should extract the information from the given context, and return the result in json format.")
        else:
            self.format_instruction = kwargs.get("format_instruction", "You must give answer with json format, and the json format should be consistent with the schema.")


    def on_agent_wakeup(self, kwargs: dict, msg: GeneralMsg):
        # 1. get history if there is any
        history = kwargs.get("history", [])

        # 2. build query
        main_input = kwargs["main_input"]
        if "{MAIN_INPUT_PLACEHOLDER}" in self.query_construction:
            query = self.query_construction.format(MAIN_INPUT_PLACEHOLDER=main_input)
        else:
            query = self.query_construction

        # 4. complete history
        previous = ''.join(history[-self.max_history_depth:])
        obj = self.llm_request.structure_output(previous + query, self.format_instruction, pydantic_cls=self.schema)

        # 4. build downstream
        history.append(main_input)
        if obj is None:
            downstream = {"main_input": "", "history": history}
            return downstream

        # parse
        downstream_input = obj.json()
        downstream = {"main_input": downstream_input, "history": history}

        # 5. finish
        if self.finish_callback is not None:
            downstream = self.finish_callback(downstream, kwargs, msg)
        return downstream
