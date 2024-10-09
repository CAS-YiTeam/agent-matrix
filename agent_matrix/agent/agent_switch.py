import time
from agent_matrix.agent.agent import Agent
from loguru import logger

class SwitchAgent(Agent):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.condition_callback = kwargs.get("condition_callback")
        self.downstream_options = kwargs.get("downstream_options")

    def agent_task_cycle(self):
        time.sleep(60.0)
        return

    def on_agent_wakeup(self, kwargs, msg):
        main_input = kwargs["main_input"]
        downstream_override = self.condition_callback(main_input, self.downstream_options)
        kwargs.update({'downstream_override': downstream_override})
        return kwargs

    def on_children_fin(self, kwargs, msg):
        return kwargs


class SwitchCaseAgent(Agent):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.switch_key = kwargs.get("switch_key")
        self.switch_case = kwargs.get("switch_case")

    def agent_task_cycle(self):
        time.sleep(60.0)
        return

    def on_agent_wakeup(self, kwargs, msg):
        switch_key_info = kwargs.get(self.switch_key, "personal_info")

        if switch_key_info not in self.switch_case:
            logger.error(f"switch key {switch_key_info} not in switch mapping")
            downstream_override = self.switch_case[0]
        else:
            downstream_override = self.switch_case[switch_key_info]

        kwargs.update({'downstream_override': downstream_override})
        return kwargs

    def on_children_fin(self, kwargs, msg):
        return kwargs
