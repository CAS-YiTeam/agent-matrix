import time
import copy
from loguru import logger
from agent_matrix.shared.config_loader import get_conf as agent_matrix_get_conf
from agent_matrix.shared.cache_fn_io import file_cache
from agent_matrix.shared.llm_bridge import RequestLlmSubClass
from agent_matrix.msg.general_msg import print_msg_string, GeneralMsg
from agent_matrix.agent.agent_groupchat_host import BasicQaAgent
from textwrap import dedent
from rich.panel import Panel
from rich import print
try: logger.level("LLM", no=23)
except: pass
logger.add("llm.log", level="LLM", rotation="10 MB", retention="10 days")
PANEL_WIDTH = agent_matrix_get_conf("PANEL_WIDTH")




select_speaker_prompt_template =  """
Read the above conversation. Then select the next role from {agentlist} to play. Only return the role."""

select_speaker_auto_multiple_template = """
You provided more than one name in your text, please return just the name of the next speaker. To determine the speaker use these prioritised rules:
1. If the context refers to themselves as a speaker e.g. "As the..." , choose that speaker's name
2. If it refers to the "next" speaker name, choose that name
3. Otherwise, choose the first provided speaker's name in the context
The names are case-sensitive and should not be abbreviated or changed.
Respond with ONLY the name of the speaker and DO NOT provide a reason."""

select_speaker_auto_none_template = """
You didn't choose a speaker. As a reminder, to determine the speaker use these prioritised rules:
1. If the context refers to themselves as a speaker e.g. "As the..." , choose that speaker's name
2. If it refers to the "next" speaker name, choose that name
3. Otherwise, choose the first provided speaker's name in the context
The names are case-sensitive and should not be abbreviated or changed.
The only names that are accepted are {agentlist}.
Respond with ONLY the name of the speaker and DO NOT provide a reason."""

# def _mentioned_agents(self, message_content, agents):
#     """Counts the number of times each agent is mentioned in the provided message content.
#     Agent names will match under any of the following conditions (all case-sensitive):
#     - Exact name match
#     - If the agent name has underscores it will match with spaces instead (e.g. 'Story_writer' == 'Story writer')
#     - If the agent name has underscores it will match with '\\_' instead of '_' (e.g. 'Story_writer' == 'Story\\_writer')

#     Args:
#         message_content (Union[str, List]): The content of the message, either as a single string or a list of strings.
#         agents (List[Agent]): A list of Agent objects, each having a 'name' attribute to be searched in the message content.

#     Returns:
#         Dict: a counter for mentioned agents.
#     """
#     if agents is None:
#         agents = self.agents

#     # Cast message content to str
#     if isinstance(message_content, dict):
#         message_content = message_content["content"]
#     message_content = content_str(message_content)

#     mentions = dict()
#     for agent in agents:
#         # Finds agent mentions, taking word boundaries into account,
#         # accommodates escaping underscores and underscores as spaces
#         regex = (
#             r"(?<=\W)("
#             + re.escape(agent.name)
#             + r"|"
#             + re.escape(agent.name.replace("_", " "))
#             + r"|"
#             + re.escape(agent.name.replace("_", r"\_"))
#             + r")(?=\W)"
#         )
#         count = len(re.findall(regex, f" {message_content} "))  # Pad the message to help with matching
#         if count > 0:
#             mentions[agent.name] = count
#     return mentions


class GroupChatAgent(BasicQaAgent):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.activate = False
        self.kwargs = kwargs
        self.max_try = kwargs.get("max_try", 4)
        self.need_history = kwargs.get("need_history", True)
        self.max_history_depth = kwargs.get("max_history_depth", 8)
        self.prompt_examples = kwargs.get("prompt_examples", "")
        self.use_debug_cache = kwargs.get("use_debug_cache", False)
        self.query_construction = kwargs.get("query_construction", "Do your job according to the instructions.") # default: tell lm to do its job according to the sys_prompt
        self.llm_request = RequestLlmSubClass(kwargs.get("temperature", 0.5))
        self.mode = 'only_query'

    def agent_task_cycle(self):
        # do nothing
        time.sleep(60.0)
        return

    def on_children_fin(self, kwargs:dict, msg: GeneralMsg):
        return kwargs

    def get_next_speaker(self, history_for_llm_request):
        query = dedent(
        """
            You are in a role play game. The following roles are available:
            {roles}.
            Read the following conversation.
            Then select the next role from {agentlist} to play. Only return the role.
        """
        )
        # 5. make the request
        if self.mode == 'history_query':
            raw_output = self.llm_request.generate_llm_request(
                query=query,
                history=history_for_llm_request,
                sys_prompt="",
                use_debug_cache=self.use_debug_cache)
        elif self.mode == 'only_query':
            join_query_and_history = "\n".join(history_for_llm_request) + "\n\n" + query
            raw_output = self.llm_request.generate_llm_request(
                query=join_query_and_history,
                history=[],
                sys_prompt="",
                use_debug_cache=self.use_debug_cache)
        print(raw_output)


    def on_agent_wakeup(self, kwargs:dict, msg: GeneralMsg):
        # 1. get history if there is any
        print_kwargs = copy.deepcopy(kwargs)
        history = kwargs.get("history", [])
        history_for_llm_request = []
        history_for_llm_request.extend(history)
        downstream_history = []
        downstream_history.extend(history)


        for i in range(self.max_try): # prepare to loop until the agent returns a valid response
            self.get_next_speaker(history_for_llm_request)

            # build query

            query = select_speaker_message_template.format(roles="roles", agentlist=self.agent_list)

            # 3. fetch system prompt
            sys_prompt = self.sys_prompt

            # 4. complete history
            if not self.need_history:
                history_for_llm_request = []
                assert "{MAIN_INPUT_PLACEHOLDER}" in self.query_construction, "If you do not need history, you must have a `MAIN_INPUT_PLACEHOLDER` in the `query_construction` argument."
            else:
                if len(history_for_llm_request) > self.max_history_depth:
                    history_for_llm_request = history_for_llm_request[-self.max_history_depth:]


        self.agent_status = raw_output
        print_kwargs["upstream_input"] = main_input = print_kwargs.pop("main_input")
        print_kwargs.update(
            {
                "query": query,
                "history": history_for_llm_request,
                "sys_prompt": sys_prompt,
                "raw_output": raw_output,
            }
        )
        print(Panel(f"{print_msg_string(print_kwargs, msg)}", width=PANEL_WIDTH))
        print(Panel(f"{print_msg_string(print_kwargs, msg, auto_clip=False)}", width=PANEL_WIDTH), file=open("llm.log", "a", encoding='utf-8'))

        # 6. send the request downstream
        if len(downstream_history) == 0 or (main_input not in downstream_history[-1]):
            downstream_history.append(main_input)
        downstream_input = """Step {NUM_STEP}, Agent 「{AGENT_ID}」:\n{AGENT_SPEECH}"""
        downstream_input = downstream_input.format(AGENT_ID=self.agent_id, AGENT_SPEECH=raw_output, NUM_STEP=msg.num_step)
        downstream_history.append(downstream_input)
        downstream = {"main_input": raw_output, "history": downstream_history}

        # return
        return downstream


