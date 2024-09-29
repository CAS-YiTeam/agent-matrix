from agent_matrix.msg.general_msg import GeneralMsg
from agent_matrix.msg.general_msg import SpecialDownstreamSet
from agent_matrix.agent.agent_basic_qa import BasicQaAgent
from textwrap import dedent
from loguru import logger

import json
import os


class StructuredArrayOutputAgent(BasicQaAgent):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.schema = kwargs.get("schema", None)
        self.max_history_depth = kwargs.get("max_history_depth", 2)
        self.format_instruction = kwargs.get("format_instruction", "You should extract the information from the given context, and return the result in json format.")


    def on_agent_wakeup(self, kwargs: dict, msg: GeneralMsg):
        # 1. get history if there is any
        history = kwargs.get("history", [])

        # 2. build query
        main_input = kwargs["main_input"]

        # 4. complete history
        previous = ''.join(history[-self.max_history_depth:])
        history.append(main_input)
        obj_arr = self.llm_request.structure_output(previous + main_input, self.format_instruction, pydantic_cls=self.schema)

        downstream = []
        downstream_split_override = []
        for i, obj in enumerate(obj_arr.topic_arr):
            downstream_input = obj.json()
            downstream.append({"main_input": downstream_input, "history": history})
            if self.finish_callback is not None:
                downstream = self.finish_callback(downstream, kwargs, msg)
            downstream_split_override.append(SpecialDownstreamSet.auto_downstream)

        msg.downstream_split_override = downstream_split_override
        return downstream