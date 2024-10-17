import init_test
from agent_matrix.matrix.matrix_mastermind import MasterMindMatrix
from agent_matrix.agent.agent_basic_qa import BasicQaAgent
from agent_matrix.agent.agent_groupchat_host import GroupChatAgent

mmm = MasterMindMatrix().begin_event_loop_non_blocking()

groupchat_host = mmm.create_agent(
    agent_id=f"nest",
    agent_class=GroupChatAgent,
    agent_kwargs={
        "use_debug_cache": False,
    }
)

player_1 = groupchat_host.create_child_agent(
    agent_id=f"player_1",
    agent_class=BasicQaAgent,
    agent_kwargs={
        "use_debug_cache": False,
        "sys_prompt": "",
        "query_construction": "You have secret number of 4.4. You should provide your secrete number when needed by others."
    }
)

player_2 = groupchat_host.create_child_agent(
    agent_id=f"player_2",
    agent_class=BasicQaAgent,
    agent_kwargs={
        "use_debug_cache": False,
        "sys_prompt": "",
        "query_construction": "You have secret number of 5.6. You should provide your secrete number when needed by others."
    }
)

sum_up = groupchat_host.create_child_agent(
    agent_id=f"sum_up",
    agent_class=BasicQaAgent,
    agent_kwargs={
        "use_debug_cache": False,
        "sys_prompt": "",
        "query_construction": "Given previous converstation, sum secret number from all players."
    }
)


# 好了，一切就绪，激活所有智能体，让他们开始工作
groupchat_host.activate_all_children()

future = groupchat_host.wakeup(r"""Objective: Get secret number from all players, sum it up.""")
result = future.wait_and_get_result()
print(result)
