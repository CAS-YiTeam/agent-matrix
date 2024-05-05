from agent_matrix.matrix.matrix_mastermind import MasterMindMatrix
from agent_matrix.msg.general_msg import auto_downstream
from textwrap import dedent

PROMPT_DO_IT = "Do your job according to the instructions."
PROMPT_DO_IT_ZH = "根据提示完成任务。"


"""
复现OpenAI的Meta-Prompting
"""

mmm = MasterMindMatrix(host='localhost', port=10101, dedicated_server=False)
mmm.begin_event_loop_non_blocking()



A1 = mmm.create_child_agent(
    agent_id=f"A1",
    agent_class="agent_matrix.agent.qa_agent->BasicQaAgent",
    agent_kwargs={
        "sys_prompt": "",
        "query_construction": "提出一个机器学习领域的简单问题，不能和之前的问题重复。例如：“什么是Dropout？” / “Batch normalization的原理和作用？”。",
    },
)
A2 = A1.create_downstream_agent(
    agent_id=f"A2",
    agent_class="agent_matrix.agent.qa_agent->BasicQaAgent",
    agent_kwargs={
        "sys_prompt": "",
        "query_construction": "回答以下问题（50字以内，简要回答）：{MAIN_INPUT_PLACEHOLDER}",
    },
)
A3 = A2.create_downstream_agent(
    agent_id=f"A3",
    agent_class="agent_matrix.agent.qa_agent->BasicQaAgent",
    agent_kwargs={
        "sys_prompt": "",
        "query_construction": "判断问题是否回答正确。回答“正确”或者“错误”。",
    },
)

A3.set_downstream_agent(A1) # loop



# 好了，一切就绪，激活所有智能体，让他们开始工作
A1.activate_agent()
A2.activate_agent()
A3.activate_agent()

A1.wakeup(
r'''
'''
)

# 主控已经不需要再做什么了，让主控进入休眠状态，让智能体们完成任务
import time
time.sleep(3600)