
downstream_input_template = """「Step {NUM_STEP}, Agent {AGENT_ID}」:\n{AGENT_SPEECH}"""

def generate_step(downstream_history):
    cnt = 1
    for chat_item in downstream_history:
        if '「Step ' + str(cnt) in chat_item:
            cnt += 1
    return cnt