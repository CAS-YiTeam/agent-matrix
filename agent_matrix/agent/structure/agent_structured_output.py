from agent_matrix.msg.general_msg import GeneralMsg
from agent_matrix.agent.agent_basic_qa import BasicQaAgent
from textwrap import dedent
from loguru import logger
import json
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

        # 4. complete history
        history.append(main_input)
        obj = self.llm_request.structure_output(main_input, self.format_instruction, pydantic_cls=self.schema)

        if obj is None:
            downstream = {"main_input": main_input, "history": history}
            return downstream

        downstream_input = obj.json()
        downstream = {"main_input": downstream_input, "history": history}

        if self.finish_callback is not None:
            downstream = self.finish_callback(downstream, kwargs, msg)
        return downstream
