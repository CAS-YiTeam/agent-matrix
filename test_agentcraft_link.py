from agent_matrix.matrix.mastermind_matrix import MasterMindMatrix
# from agent_matrix.agent.agent_basic import Agent

mmm = MasterMindMatrix(host='localhost', port=10101, dedicated_server=False)
mmm.begin_event_loop_non_blocking()

# 在母体中，一个特殊的容器智能体
agent_kwargs = {}
plane_0 = mmm.create_agent(
    agent_id=f"plane_0",
    agent_class="agent_matrix.agent.agent->Agent",
    agent_kwargs=agent_kwargs
)



# 主控已经不需要再做什么了，让主控进入休眠状态，让智能体们完成任务
import time
time.sleep(3600)
# sys.pause()