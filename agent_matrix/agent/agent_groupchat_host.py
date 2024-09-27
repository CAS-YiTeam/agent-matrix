import time
import copy
from loguru import logger
from agent_matrix.shared.config_loader import get_conf as agent_matrix_get_conf
from agent_matrix.shared.cache_fn_io import file_cache
from agent_matrix.shared.llm_bridge import RequestLlmSubClass
from agent_matrix.msg.general_msg import print_msg_string, GeneralMsg
from agent_matrix.agent.agent_basic_qa import BasicQaAgent
from textwrap import dedent
try: logger.level("LLM", no=23)
except: pass
logger.add("llm.log", level="LLM", rotation="10 MB", retention="10 days")
PANEL_WIDTH = agent_matrix_get_conf("PANEL_WIDTH")
DEBUG_MOD = agent_matrix_get_conf("DEBUG_MOD")

# Prompt forked from AutoGen
select_speaker_prompt_template =  """
Read the above conversation. Then select the next role from {agentlist} to play. Only return the role."""

# Prompt forked from AutoGen
select_speaker_auto_multiple_template = """
You provided more than one name in your text, please return just the name of the next speaker. To determine the speaker use these prioritised rules:
1. If the context refers to themselves as a speaker e.g. "As the..." , choose that speaker's name
2. If it refers to the "next" speaker name, choose that name
3. Otherwise, choose the first provided speaker's name in the context
The names are case-sensitive and should not be abbreviated or changed.
Respond with ONLY the name of the speaker and DO NOT provide a reason."""

# Prompt forked from AutoGen
select_speaker_auto_none_template = """
You didn't choose a speaker. As a reminder, to determine the speaker use these prioritised rules:
1. If the context refers to themselves as a speaker e.g. "As the..." , choose that speaker's name
2. If it refers to the "next" speaker name, choose that name
3. Otherwise, choose the first provided speaker's name in the context
The names are case-sensitive and should not be abbreviated or changed.
The only names that are accepted are {agentlist}.
Respond with ONLY the name of the speaker and DO NOT provide a reason."""


class GroupChatAgent(BasicQaAgent):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.activate = False
        self.kwargs = kwargs
        self.max_try = kwargs.get("max_try", 4)
        self.need_history = kwargs.get("need_history", True)
        self.max_history_depth = kwargs.get("max_history_depth", 8)
        self.prompt_examples = kwargs.get("prompt_examples", "")
        self.query_construction = kwargs.get("query_construction", "Do your job according to the instructions.") # default: tell lm to do its job according to the sys_prompt
        self.llm_request = RequestLlmSubClass(kwargs.get("temperature", 0.5))
        self.mode = 'only_query'

    def agent_task_cycle(self):
        # do nothing
        time.sleep(60.0)
        return

    def on_children_fin(self, kwargs:dict, msg: GeneralMsg):
        return self.on_agent_wakeup(kwargs, msg)

    def get_next_speaker(self, history_for_llm_request):

        query = dedent(
            """
                You are in a role play game, and you are the leader to arrange the order of speakers.
                The following speakers are available: {roles}.
                Read the following conversation,
                plan and select the next speaker from {agentlist},
                and explain why you choose this speaker.

                Note:
                You should wrap the SELECTED speaker name in dollar quotes, e.g. "I decide $the_speaker_name$ should be the next speaker to play".
                When the initial goal is done, you should return $terminate_conversation$ (in dollar quotes) to end the conversation.
            """
        )
        def parse_speaker_maunally(raw_output, agent_list):
            if "$terminate_conversation$" in raw_output:
                return True, None, True

            # optimal case: llm use dollar quotes
            if "$" in raw_output:
                # use regex to extract
                import re
                match = re.search(r'\$(.*?)\$', raw_output)
                if match:
                    next_speaker = match.group(1)
                    if next_speaker in agent_list:
                        return True, next_speaker, False
                    else:
                        return False, None, False
                else:
                    return False, None, False
            else:
                return False, None, False

        direct_children_array = self.get_property_from_proxy("direct_children")
        agent_id_array = [agent["agent_id"] for agent in direct_children_array]
        query = query.format(roles=agent_id_array, agentlist=agent_id_array+["terminate_conversation"])
        # 5. make the request
        if self.mode == 'only_query':
            join_query_and_history = query + "\nPrevious conversation:\n" + "\n".join(history_for_llm_request)
            raw_output = self.llm_request.generate_llm_request(
                query=join_query_and_history,
                history=[],
                sys_prompt="")
        valid, next_speaker, terminate = parse_speaker_maunally(raw_output, agent_id_array)
        return valid, next_speaker, terminate



    def on_agent_wakeup(self, kwargs:dict, msg: GeneralMsg):
        history = kwargs.get("history", [])
        history_for_llm_request = []
        history_for_llm_request.extend(history)
        downstream_history = []
        downstream_history.extend(history)
        main_input = kwargs["main_input"]
        if len(downstream_history) == 0 or (main_input not in downstream_history[-1]):
            downstream_history.append(main_input)

        for _ in range(self.max_try): # prepare to loop until the agent returns a valid response
            valid, next_speaker, terminate = self.get_next_speaker(history_for_llm_request)
            if terminate:
                kwargs.pop("children_select_override", None)
                return kwargs
            if valid:
                kwargs.update({'children_select_override': next_speaker})
                kwargs.update({'call_children_again': True})
                return kwargs

        if DEBUG_MOD: input('next_speaker\t', next_speaker, 'Press Enter to continue...')

        # run fail
        kwargs.pop("children_select_override", None)
        return kwargs

