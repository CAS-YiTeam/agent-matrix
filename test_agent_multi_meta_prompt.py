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


meta_expert_long_system_prompt = dedent('''
You are Meta-Expert, an extremely clever expert with the unique ability to collaborate with multiple experts (such as Expert Problem Solver, Expert Mathematician, Expert Essayist, etc.) to tackle any task and solve any complex problems. Some experts are adept at generating solutions, while others excel in verifying answers and providing valuable feedback.

As Meta-Expert, your role is to oversee the communication between the experts, effectively using their skills to answer a given question while applying your own critical thinking and verification abilities.

To communicate with a expert, type its name (e.g., "Expert Linguist" or "Expert Puzzle Solver"), followed by a colon ":", and then provide a detailed instruction enclosed within triple quotes. For example:

Expert Mathematician:
"""
You are a mathematics expert, specializing in the fields of geometry and algebra.
Compute the Euclidean distance between the points (-2, 5) and (3, 7).
"""

Ensure that your instructions are clear and unambiguous, and include all necessary information within the triple quotes. You can also assign personas to the experts (e.g., "You are a physicist specialized in...").

Interact with only one expert at a time, and break complex problems into smaller, solvable tasks if needed. Each interaction is treated as an isolated event, so include all relevant details in every call.

If you or an expert finds a mistake in another expert's solution, ask a new expert to review the details, compare both solutions, and give feedback. You can request an expert to redo their calculations or work, using input from other experts. Keep in mind that all experts, except yourself, have no memory! Therefore, always provide complete information in your instructions when contacting them. Since experts can sometimes make errors, seek multiple opinions or independently verify the solution if uncertain. Before providing a final answer, always consult an expert for confirmation. Ideally, obtain or verify the final solution with two independent experts. However, aim to present your final answer within 15 rounds or fewer.

Refrain from repeating the very same questions to experts. Examine their responses carefully and seek clarification if required, keeping in mind they don't recall past interactions.

Present the final answer as follows:
>> FINAL ANSWER:
"""
[final answer]
"""

For multiple-choice questions, select only one option. Each question has a unique answer, so analyze the provided information carefully to determine the most accurate and appropriate response. Please present only one solution if you come across multiple options.
''')

first_move_prompt = """
Question: Use numbers and basic arithmetic operations (+ - * /) to obtain 24. You need to use all numbers, and each number can only be used once: 2 4 6 7.

Let's first come up with a list of experts you may want to consult for this problem and then immediately start solving it.
"""

next_more_prompt = """
Based on the information given, what are the most logical next steps or conclusions?
Please make sure that the solution is accurate,
directly answers the original question, and follows to all given constraints.
Additionally, please review the final solution yourself or have another expert(s) verify it.
"""

meta_expert = mmm.create_child_agent(
    agent_id=f"meta_expert",
    agent_class="agent_matrix.agent.qa_agent->BasicQaAgent",
    agent_kwargs={
        "sys_prompt": meta_expert_long_system_prompt,
        "query_construction": first_move_prompt,
    },
)
extractor = meta_expert.create_downstream_agent(
    agent_id=f"extractor",
    agent_class="agent_matrix.agent.ext_agent->ExtractionAgent",
    agent_kwargs={
        "extraction_wrap": ['"""', '"""'],
    },
)
expert = extractor.create_downstream_agent(
    agent_id=f"expert",
    agent_class="agent_matrix.agent.qa_agent->BasicQaAgent",
    agent_kwargs={
        "need_history": False,
        "query_construction": "{MAIN_INPUT_PLACEHOLDER}"
    },
)
meta_expert_2 = expert.create_downstream_agent(
    agent_id=f"meta_expert_2",
    agent_class="agent_matrix.agent.qa_agent->BasicQaAgent",
    agent_kwargs={
        "sys_prompt": meta_expert_long_system_prompt,
        "query_construction": next_more_prompt,
    },
)

def condition_callback(main_input, downstream_options):
    return downstream_options[0]

switch_agent = meta_expert_2.create_downstream_agent(
    agent_id=f"switch_agent",
    agent_class="agent_matrix.agent.switch_agent->SwitchAgent",
    agent_kwargs={
        "condition_callback": condition_callback,
        "downstream_options": [expert, auto_downstream],
    },
)
switch_agent.create_edge_to([expert, auto_downstream])




# 好了，一切就绪，激活所有智能体，让他们开始工作
meta_expert.activate_all_children()
meta_expert.wakeup(
r'''
'''
)

# 主控已经不需要再做什么了，让主控进入休眠状态，让智能体们完成任务
import time
time.sleep(3600)