from agent_matrix.msg.general_msg import GeneralMsg
from agent_matrix.msg.ui_msg import UserInterfaceMsg
from agent_matrix.msg.agent_msg import generate_agent_dict
from agent_matrix.agentcraft.agentcraft_proxy import AgentCraftProxy
import asyncio
import json

class PythonMethod_AgentcraftHandler:

    async def matrix_process_msg_from_agentcraft(self,
        msg: UserInterfaceMsg,
        message_queue_out: asyncio.Queue,
        agentcraft_proxy: AgentCraftProxy
    ):
        agent_summary = self.generate_agent_summary()
        if msg.command == "update_agents":
            reply_msg = UserInterfaceMsg(
                src = 'matrix',
                dst = agentcraft_proxy.client_id,
                command = "update_agents.re",
                arg = json.dumps(agent_summary),
            )
            await message_queue_out.put(reply_msg)


    def get_all_agents_in_matrix(self):
        all_agents = []
        for agent in self.direct_children:
            all_agents.append(agent)
            all_agents.extend(agent.get_children())
        return all_agents

    def generate_agent_summary(self):
        agent_summary_array = []
        for agent in self.get_all_agents_in_matrix():
            agent_summary_array.append(generate_agent_dict(agent))

        return {"agent_summary_array": agent_summary_array}