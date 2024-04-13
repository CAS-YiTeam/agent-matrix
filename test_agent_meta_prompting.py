from agent_matrix.matrix.matrix_mastermind import MasterMindMatrix
# from agent_matrix.agent.agent_basic import Agent

"""
复现OpenAI的Meta-Prompting
"""

mmm = MasterMindMatrix(host='localhost', port=10101, dedicated_server=False)
mmm.begin_event_loop_non_blocking()

# 在母体中，一个特殊的容器智能体
agent_kwargs = {}
plane_0 = mmm.create_agent(
    agent_id=f"plane_0",
    agent_class="agent_matrix.agent.agent->Agent",
    agent_kwargs=agent_kwargs
)

# # 用明确的边连接定义智能体的交互
# plane_0.interaction_builder.create_edge(src_agent="plane_0_agent_0", dst_agent="plane_0_agent_1", channel="red")
# plane_0.interaction_builder.create_edge(src_agent="plane_0_agent_1", dst_agent="plane_0_agent_2", channel="red")
# plane_0.interaction_builder.create_edge(src_agent="plane_0_agent_2", dst_agent="plane_0_agent_3", channel="red")

# # 好了，一切就绪，激活所有智能体，让他们开始工作
# for i in range(0, 3):
#     mmm.activate_agent(agent_id=f"plane_0_agent_{i}")

# 主控已经不需要再做什么了，让主控进入休眠状态，让智能体们完成任务
import time
time.sleep(3600)
# sys.pause()