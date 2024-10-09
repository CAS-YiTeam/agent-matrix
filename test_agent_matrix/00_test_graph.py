import init_test # 修正测试路径到项目根目录，这样才能正确导入agent_matrix
from typing import List, Tuple, Any
from pydantic import BaseModel, Field
from agent_matrix.agent.agent import Agent, EchoAgent
from agent_matrix.agent.router.agent_multi_downstream import SplitAgent
from loguru import logger
from agent_matrix.matrix.matrix_mastermind import MasterMindMatrix
from test_graph_agents import TracerAgent, TracerAgent2
from agent_matrix.agent.agent_switch import SwitchCaseAgent

mmm = MasterMindMatrix(host='localhost', port=10101, dedicated_server=False).begin_event_loop_non_blocking()

n1 = mmm.create_agent(
    agent_id = f"node-1",
    agent_class = TracerAgent,
    run_in_matrix_process = True,
    agent_kwargs = {}
)
n2 = mmm.create_agent(
    agent_id = f"node-2",
    agent_class = TracerAgent,
    run_in_matrix_process = True,
    agent_kwargs = {}
)
n3 = mmm.create_agent(
    agent_id = f"node-3",
    agent_class = SplitAgent,
    run_in_matrix_process = True,
    agent_kwargs = {
        "split_downstream_agent_id": ["node-4", "node-5", "node-6"]
    }
)
n1 >> n2
n2 >> n3


n4 = mmm.create_agent(
    agent_id = f"node-4",
    agent_class = TracerAgent2,
    run_in_matrix_process = True,
    agent_kwargs = {}
)
n5 = mmm.create_agent(
    agent_id = f"node-5",
    agent_class = TracerAgent2,
    run_in_matrix_process = True,
    agent_kwargs = {}
)
n6 = mmm.create_agent(
    agent_id = f"node-6",
    agent_class = TracerAgent2,
    run_in_matrix_process = True,
    agent_kwargs = {}
)
n7 = mmm.create_agent(
    agent_id = f"node-7",
    agent_class = TracerAgent,
    run_in_matrix_process = True,
    agent_kwargs = {
        "join_upstream": True,
    }
)
n4 >> n7
n5 >> n7
n6 >> n7


n11 = mmm.create_agent(
    agent_id = f"node-11",
    agent_class = SwitchCaseAgent,
    run_in_matrix_process = True,
    agent_kwargs = {
        "switch_key": "intention",
        "switch_case": {
            "personal_info": "node-12", # if .intention == "personal_info", then go to node-12 (first is default)
            "peek_memory": "node-13",   # if .intention == "peek_memory", then go to node-13
        }
    }
)
n7 >> n11

n12 = mmm.create_agent(
    agent_id = f"node-12",
    agent_class = TracerAgent,
    run_in_matrix_process = True,
    agent_kwargs = {}
)
n13 = mmm.create_agent(
    agent_id = f"node-13",
    agent_class = TracerAgent,
    run_in_matrix_process = True,
    agent_kwargs = {}
)
n14 = mmm.create_agent(
    agent_id = f"node-14",
    agent_class = TracerAgent,
    run_in_matrix_process = True,
    agent_kwargs = {}
)
n12 >> n14
n13 >> n14

# ===========================================================================================

agents = mmm.get_all_agents_in_matrix()
for agent in agents:
    agent.activate()

future = agents[0].wakeup("hello")
res = future.wait_and_get_result()

input('waiting for user input to exit...')