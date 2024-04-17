from agent_matrix.matrix.matrix_mastermind import MasterMindMatrix
from textwrap import dedent

PROMPT_DO_IT = "Do your job according to the instructions."
PROMPT_DO_IT_ZH = "根据提示完成任务。"


"""
复现OpenAI的Meta-Prompting
"""

mmm = MasterMindMatrix(host='localhost', port=10101, dedicated_server=False)
mmm.begin_event_loop_non_blocking()

# 在母体中，创建一个嵌套智能体，一个高级的翻译者
pro_zh_translator = mmm.create_agent(
    agent_id=f"pro_zh_translator",
    agent_class="agent_matrix.agent.qa_agent->BasicQaAgent",
    agent_kwargs={
        "sys_prompt": "",
        "query_construction":
            r"Below is a section from an English academic paper, translate it into Chinese. " +
            r"Do not modify any latex command such as \section, \cite, \begin, \item and equations. " +
            r"Answer me only with the translated text:" + "{MAIN_INPUT_PLACEHOLDER}\n"
    },
)


# 为这个高级翻译者创建一个子智能体，用于纠正生硬的翻译，使其更符合中文语言习惯
passive_editor = pro_zh_translator.create_agent(
    agent_id=f"passive_editor",
    agent_class="agent_matrix.agent.qa_agent->BasicQaAgent",
    agent_kwargs={
        "sys_prompt": dedent("""
                                移除句子中所有的“我们”一词，将涉及到的动词改为被动语态。仅输出修改后的句子。

                                举例1：
                                    We note that the workflow of AutoCodeRover...
                                    错误翻译：我们注意到，到目前为止讨论的AutoCodeRover的工作流程...
                                    改正方法：直接删除

                                举例2：
                                    We present a case study on one of the tasks uniquely resolved by ACR-val-sbfl...
                                    错误翻译：我们呈现了一个由ACR-val-sbfl独特解决的任务的案例研究...
                                    改正方法：替换成“本文”，“本节”
                                """),
        "need_history": False,
        "query_construction": "{MAIN_INPUT_PLACEHOLDER}\n" + PROMPT_DO_IT_ZH
    }
)


reflector = passive_editor.create_agent(
    agent_id=f"reflector",
    agent_class="agent_matrix.agent.qa_agent->BasicQaAgent",
    agent_kwargs={
        "sys_prompt": "你需要按照要求检查其他智能体的错误，并进行修改。",
        "need_history": True,
        "query_construction": f"你知道智能体「{passive_editor.agent_id}」犯了什么错误吗？请检查并修正。"
    }
)
reflector.create_agent(
    agent_id=f"correct_domain",
    agent_class="agent_matrix.agent.qa_agent->BasicQaAgent",
    agent_kwargs={
        "sys_prompt": "纠正领域翻译的错误，例如Agent在机器学习领域应当翻译为智能体。",
        "query_construction": "这篇文章来及哪个领域？在这个领域中，上述翻译中哪些专业名词存在翻译错误？请检查并修正。"
    }
)


concluder = pro_zh_translator.create_agent(
    agent_id=f"concluder",
    agent_class="agent_matrix.agent.qa_agent->BasicQaAgent",
    agent_kwargs={
        "query_construction": "给出以上智能体（「pro_zh_translator」，「passive_editor」，「reflector」）讨论的最终翻译结果，用```包裹翻译结果。"
    }
)

passive_editor.create_edge_to(concluder)

# 好了，一切就绪，激活所有智能体，让他们开始工作
pro_zh_translator.activate_all_children()

# pro_zh_translator.wakeup(r"""
# We selected two recent LLM-based agent systems Swe-agent [38] and Magis
# [32] designed for SWE-bench tasks as baselines and compare their performance against our AutoCodeRover.
# Swe-agent is publicly available as a GitHub repository4,
# so we replicated it as Swe-agent-rep with the default
# setting based on the provided scripts. In contrast to Sweagent, we do not have access to Magis, so we take the
# most relevant reported result from their technical report
# [32]. To avoid the natural randomness of LLM,
# we repeat our experiments with AutoCodeRover and Sweagent-rep on SWE-bench lite three times. We use (1) the
# percentage of resolved instances, (2) average time cost,
# and (3) average token cost to evaluate the effectiveness of
# the tools. The three evaluation metrics represent overall
# effectiveness, time efficiency, and economic efficacy in
# resolving real-world GitHub issues. For AutoCodeRover
# and Swe-agent-rep, we report the average and total number of resolved instances across three repetitions.
# """.replace("\n", " "))

pro_zh_translator.wakeup(r"""
A series of methods derived from velocity obstacle (VO)
algorithm [6], such as Reciprocal Velocity Obstacle (RVO)
[7], Optima Reciprocal Collision Avoidance (ORCA) [8],
etc. [9]–[11], can deal with MCNP in a decentralized way.
The principle of reciprocity assumes that agents share the
same responsibility for collision avoidance so that multiple
agents using the same policy can safely reach their respective
destinations. Although increasing the safety radius alleviates
the problem caused by the perfect sensing assumption of
the VO-based methods [12], [13], it will be difficult for a
conservative policy to escape the freezing robot problem [14].
On the other hand, with the emergence of Deep Reinforcement
Learning (DRL) in the field of robot navigation [15]–[18],
some DRL-based methods [19]–[22] have also been used to
solve MCNP in a decentralized manner. The agent-level DRLbased framework is promising in navigation due to its demonstrated potential for modeling complex interactions between
dynamic obstacles with unknown modes. However, the above
decentralized methods do not lead to a cooperative multiagent policy, that is, the global optimal solution of MCNP is
difficult to obtain. Specifically, in these decentralized methods,
each agent has a pre-assigned and exclusive destination and
treats all other “teammates” as dynamic obstacles in the
environment. Besides, DRL-based methods also face the nonstationarity of the environment induced by simultaneously
learning and exploring agents.
""".replace("\n", " "))

# 主控已经不需要再做什么了，让主控进入休眠状态，让智能体们完成任务
import time
time.sleep(3600)