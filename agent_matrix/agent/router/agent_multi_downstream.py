from agent_matrix.msg.general_msg import GeneralMsg
from agent_matrix.msg.general_msg import SpecialDownstreamSet
from agent_matrix.agent.agent import Agent
from agent_matrix.agent.structure.agent_structured_output import StructuredOutputAgent
from textwrap import dedent
from loguru import logger
from typing import List


class SplitAgent(Agent):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.split_downstream_agent_id: List[str] = kwargs.get("split_downstream_agent_id")

    def agent_task_cycle(self):
        return

    def on_agent_wakeup(self, kwargs: dict, msg: GeneralMsg):
        # 1. get history if there is any
        history = kwargs.get("history", [])
        # 2. build query
        main_input = kwargs["main_input"]

        # split downstream
        downstream = []
        downstream_split_override = []
        for i, target in enumerate(self.split_downstream_agent_id):
            downstream.append({"main_input": main_input, "history": history})
            downstream_split_override.append(target)
        msg.downstream_split_override = downstream_split_override
        return downstream


class StructuredArrayOutputAgent(StructuredOutputAgent):

    def on_agent_wakeup(self, kwargs: dict, msg: GeneralMsg):
        # 1. get history if there is any
        history = kwargs.get("history", [])

        # 2. build query
        main_input = kwargs["main_input"]
        if "{MAIN_INPUT_PLACEHOLDER}" in self.query_construction:
            query = self.query_construction.format(MAIN_INPUT_PLACEHOLDER=main_input)
        else:
            query = self.query_construction

        # 3. complete history
        previous = ''.join(history[-self.max_history_depth:])
        obj_arr = self.llm_request.structure_output(previous + query, self.format_instruction, pydantic_cls=self.schema)

        # 4. build downstream
        history.append(main_input)
        if obj_arr is None:
            downstream = {"main_input": "", "history": history}
            return downstream

        # parse
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
