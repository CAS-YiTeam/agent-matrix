from typing import List, Tuple, Any
from pydantic import BaseModel, Field
from agent_matrix.agent.agent import Agent, EchoAgent
from agent_matrix.agent.router.agent_multi_downstream import SplitAgent
from loguru import logger
from agent_matrix.matrix.matrix_mastermind import MasterMindMatrix

class TracerAgent(EchoAgent):

    def on_agent_wakeup(self, kwargs, msg):
        main_input = kwargs["main_input"]
        downstream = {"main_input": main_input + "\t" + self.agent_id, "history": []}
        return downstream

class TracerAgent2(EchoAgent):

    def on_agent_wakeup(self, kwargs, msg):
        main_input = kwargs["main_input"]
        downstream = {"main_input": main_input + "\t" + self.agent_id, "history": []}
        return downstream
