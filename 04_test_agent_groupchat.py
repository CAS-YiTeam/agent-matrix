from agent_matrix.matrix.matrix_mastermind import MasterMindMatrix
from agent_matrix.agent.agent_basic_qa import BasicQaAgent
from agent_matrix.agent.agent_groupchat_host import GroupChatAgent

mmm = MasterMindMatrix(host='localhost', port=10101, dedicated_server=False)
mmm.begin_event_loop_non_blocking()

group_chat_master = mmm.create_agent(
    agent_id=f"nest",
    agent_class=GroupChatAgent,
    agent_kwargs={
        "use_debug_cache": False,
    }
)

network_surfer = group_chat_master.create_child_agent(
    agent_id=f"network_surfer",
    agent_class=BasicQaAgent,
    agent_kwargs={
        "use_debug_cache": False,
        "sys_prompt": "You are a network surfer, you can access internet to gather information. Please provide search keywords. Return with the following format: `SEARCH_KEY='XXX'`.",
        "query_construction": "{MAIN_INPUT_PLACEHOLDER}"
    }
)

planner = group_chat_master.create_child_agent(
    agent_id=f"planner",
    agent_class=BasicQaAgent,
    agent_kwargs={
        "use_debug_cache": False,
        "sys_prompt": "You are a planner, when given a task, you are required to break it down into multiple stages.",
        "query_construction": "{MAIN_INPUT_PLACEHOLDER}"
    }
)

analyst = group_chat_master.create_child_agent(
    agent_id=f"analyst",
    agent_class=BasicQaAgent,
    agent_kwargs={
        "use_debug_cache": False,
        "sys_prompt": "You are an analyst, give your solution.",
        "query_construction": "{MAIN_INPUT_PLACEHOLDER}"
    }
)


# 好了，一切就绪，激活所有智能体，让他们开始工作
group_chat_master.activate_all_children()

group_chat_master.wakeup(r"""
Objective:
    Get latest news about Middle East, determine how these news will affect the stock market (e-car related), and make a plan for the next week.
""")

import time
time.sleep(6000)
input('主线程进入休眠状态，让智能体们完成任务')