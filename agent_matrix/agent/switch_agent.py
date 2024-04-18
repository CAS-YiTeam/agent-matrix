from agent_matrix.agent.agent import Agent

class SwitchAgent(Agent):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.condition_callback = kwargs.get("condition_callback")
        self.downstream_options = kwargs.get("downstream_options")

    def agent_task_cycle(self):
        return

    def on_agent_wakeup(self, kwargs, msg):
        main_input = kwargs["main_input"]
        if self.condition_callback(main_input, self.downstream_options):
            downstream_override = self.downstream_options[main_input]
        kwargs.update({'downstream_override': downstream_override})
        return kwargs

    def on_children_fin(self, kwargs, msg):
        return kwargs
