

def generate_agent_dict(agent):
    return {
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
    }