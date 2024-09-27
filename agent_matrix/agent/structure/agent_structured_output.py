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
        self.format_instruction = kwargs.get("format_instruction", "You should extract the information from the given context, and return the result in json format.")


    def on_agent_wakeup(self, kwargs: dict, msg: GeneralMsg):
        # 1. get history if there is any
        history = kwargs.get("history", [])

        # 2. build query
        main_input = kwargs["main_input"]

        # 4. complete history
        history.append(main_input)
        obj = self.llm_request.structure_output(main_input, self.format_instruction, pydantic_cls=self.schema)

        downstream_input = obj.json()
        downstream = {"main_input": downstream_input, "history": history}

        if self.finish_callback is not None:
            downstream = self.finish_callback(downstream, kwargs, msg)
        return downstream
