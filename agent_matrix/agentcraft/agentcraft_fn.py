from agent_matrix.msg.general_msg import GeneralMsg
from agent_matrix.msg.ui_msg import UserInterfaceMsg
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
            agent_summary_array.append({
                "valid": True,
                "agent_id":         agent.agent_id,
                "agent_location":   {
                    "X": agent.agent_location[0],
                    "Y": agent.agent_location[1],
                    "Z": agent.agent_location[2],
                },
                "agent_ue_class":   agent.agent_ue_class,
                "agent_status":     agent.agent_status,
                "agent_animation":  agent.agent_animation,
                "agent_activity":   agent.agent_activity,
                "agent_request":    agent.agent_request,
            })

        return {"agent_summary_array": agent_summary_array}