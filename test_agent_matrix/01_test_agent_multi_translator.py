import init_test # 修正测试路径到项目根目录，这样才能正确导入agent_matrix
from agent_matrix.matrix.matrix_mastermind import MasterMindMatrix
from textwrap import dedent
def create_agent_arg_dict(**kwargs): return kwargs

"""
翻译任务
── pro_zh_translator           // 主智能体，负责初步翻译，将精细调整的工作交给子智能体
   ├── passive_editor          // 子智能体1，负责将主动语态转化为被动
   |── correct_domain
   └── concluder
"""

PROMPT_DO_IT_ZH = "根据上文的提示并完成任务。"  # PROMPT_DO_IT = "Do your job according to the instructions."

mmm = MasterMindMatrix(host='localhost', port=10101, dedicated_server=False)
mmm.begin_event_loop_non_blocking()

# 在母体中，创建一个嵌套智能体，一个高级的翻译者
pro_zh_translator = mmm.create_child_agent(
    agent_id=f"pro_zh_translator",
    agent_class="agent_matrix.agent.agent_basic_qa->BasicQaAgent",
    run_in_matrix_process=True,
    agent_kwargs={
        "sys_prompt": "",
        "query_construction":
            r"Below is a section from an English academic paper, translate it into Chinese. Do not modify any latex command such as \section, \cite, \begin, \item and equations. Answer me only with the translated text:" + "{MAIN_INPUT_PLACEHOLDER}\n"
    },
)

# 为这个高级翻译者创建一个子智能体，用于纠正生硬的翻译，使其更符合中文语言习惯
children = pro_zh_translator.create_child_agent_sequential(
    [
        create_agent_arg_dict(
            agent_id = f"correct_domain",
            agent_class = "agent_matrix.agent.agent_basic_qa->BasicQaAgent",
            # run_in_matrix_process=True,
            agent_kwargs = {
                "sys_prompt": "纠正领域翻译的错误。例如，Agent这个单词在机器学习领域中，应当翻译为“智能体”。",
                "query_construction": "这篇文章来及哪个领域？在这个领域中，上述翻译中哪些专业名词存在翻译错误？请检查并列举这些错误。然后给出完成的正确翻译。"
            }
        ),
        create_agent_arg_dict(
            agent_id=f"passive_editor",
            agent_class="agent_matrix.agent.agent_basic_qa->BasicQaAgent",
            run_in_matrix_process=True,
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
                "query_construction": "按要求修正以下翻译：\n\n{MAIN_INPUT_PLACEHOLDER}"
            }
        ),
        create_agent_arg_dict(
            agent_id=f"concluder",
            agent_class="agent_matrix.agent.agent_basic_qa->BasicQaAgent",
            # run_in_matrix_process=True,
            agent_kwargs={
                "query_construction": "根据以上智能体（「pro_zh_translator」，「passive_editor」，「reflector」）的讨论，给出最终的中文翻译结果，用```（markdown）包裹翻译结果。"
            }
        ),

    ]
)


# 好了，一切就绪，激活所有智能体，让他们开始工作
pro_zh_translator.activate_all_children()
# pro_zh_translator.wakeup(r"""翻译：
# A series of methods derived from velocity obstacle (VO) algorithm [6], such as Reciprocal Velocity Obstacle (RVO) [7], Optima Reciprocal Collision Avoidance (ORCA) [8], etc. [9]–[11], can deal with MCNP in a decentralized way. The principle of reciprocity assumes that agents share the same responsibility for collision avoidance so that multiple agents using the same policy can safely reach their respective destinations. Although increasing the safety radius alleviates the problem caused by the perfect sensing assumption of the VO-based methods [12], [13], it will be difficult for a conservative policy to escape the freezing robot problem [14]. On the other hand, with the emergence of Deep Reinforcement Learning (DRL) in the field of robot navigation [15]–[18], some DRL-based methods [19]–[22] have also been used to solve MCNP in a decentralized manner. The agent-level DRLbased framework is promising in navigation due to its demonstrated potential for modeling complex interactions between dynamic obstacles with unknown modes. However, the above decentralized methods do not lead to a cooperative multiagent policy, that is, the global optimal solution of MCNP is difficult to obtain. Specifically, in these decentralized methods, each agent has a pre-assigned and exclusive destination and treats all other “teammates” as dynamic obstacles in the environment. Besides, DRL-based methods also face the nonstationarity of the environment induced by simultaneously learning and exploring agents.
# """)
future = pro_zh_translator.wakeup(r"""翻译：
Chain-of-thought prompting combined with pre-trained large language models has achieved encouraging results on complex reasoning tasks. In this paper, we propose a new decoding strategy, self-consistency, to replace the naive greedy decoding used in chain-of-thought prompting. It first samples a diverse set of reasoning paths instead of only taking the greedy one, and then selects the most consistent answer by marginalizing out the sampled reasoning paths. Self-consistency leverages the intuition that a complex reasoning problem typically admits multiple different ways of thinking leading to its unique correct answer. Our extensive empirical evaluation shows that self-consistency boosts the performance of chain-of-thought prompting with a striking margin on a range of popular arithmetic and commonsense reasoning benchmarks, including GSM8K (+17.9%), SVAMP (+11.0%), AQuA (+12.2%), StrategyQA (+6.4%) and ARC-challenge (+3.9%).
""")
res = future.wait_and_get_result()
# 主控已经不需要再做什么了，让主控进入休眠状态，让智能体们完成任务
import time
time.sleep(3600)




