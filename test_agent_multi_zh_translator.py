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
    agent_class="agent_matrix.agent.agent->EchoAgent",
    agent_kwargs={},
)

# 为这个高级翻译者创建一个子智能体，用于原始翻译
primitive_translation = pro_zh_translator.create_agent(
    agent_id=f"primitive_translation",
    agent_class="agent_matrix.agent.qa_agent->BasicQaAgent",
    agent_kwargs={"sys_prompt": "",
        "query_construction":
            r"Below is a section from an English academic paper, translate it into Chinese. " +
            r"Do not modify any latex command such as \section, \cite, \begin, \item and equations. " +
            r"Answer me only with the translated text:" + "{MAIN_INPUT_PLACEHOLDER}\n"
    },
    blocking=True
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
    },
    blocking=True
)



# 为这个高级翻译者创建一个子智能体，用于纠正生硬的翻译，使其更符合中文语言习惯
adjust_grammar = pro_zh_translator.create_agent(
    agent_id=f"adjust_grammar",
    agent_class="agent_matrix.agent.qa_agent->BasicQaAgent",
    agent_kwargs={
        "sys_prompt": dedent("""
                                你是一个中文科研论文写作导师，正在纠正学生的学术文章错误。仅输出修改后的句子。

                                示例1
                                -- 原文与翻译：
                                    “Given this motivation of automating program repair, ...”
                                    “鉴于自动程序修复的这种动机，...”
                                -- 问题：
                                    冗余，重点不突出
                                -- 更正方法：
                                    “为了自动化地修复程序，...”

                                示例2
                                -- 原文与翻译：
                                    “We show an example of a challenging feature addition task.”
                                    “我们展示了一个具有挑战性的特性添加任务的示例。”
                                -- 问题：
                                    学术文章里面禁止出现“我们”一词
                                    句子中连续出现两个“的”
                                -- 更正方法：
                                    “以下是一个挑战性的特性添加任务示例。”

                                示例3
                                -- 原文与翻译：
                                    “We propose an automated approach to autonomously achieve program improvement. ”
                                    “我们提出了一种自动化方法，以自主实现程序改进。”
                                -- 问题：
                                    to从句形式不符合中文学术文章中的语法习惯
                                    学术文章里面禁止出现“我们”一词
                                -- 更正方法：
                                    “本文提出一种自动改进程序的方法。”
                                ]
                            """),
        "need_history": False,
        "query_construction": "{MAIN_INPUT_PLACEHOLDER}\n" + PROMPT_DO_IT_ZH
    },
    blocking=True
)


# 为这个高级翻译者创建一个子智能体，用于纠正生硬的翻译，使其更符合中文语言习惯
punctuation_editor = pro_zh_translator.create_agent(
    agent_id=f"punctuation_editor",
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
    },
    blocking=True
)


# 用明确的边连接定义智能体的交互
primitive_translation.create_edge_to(dst_agent_id=passive_editor)
passive_editor.create_edge_to(dst_agent_id=adjust_grammar)

# 好了，一切就绪，激活所有智能体，让他们开始工作
primitive_translation.activate()
passive_editor.activate()
adjust_grammar.activate()
pro_zh_translator.activate()

pro_zh_translator.wakeup(r"""
We selected two recent LLM-based agent systems Swe-agent [38] and Magis
[32] designed for SWE-bench tasks as baselines and compare their performance against our AutoCodeRover.
Swe-agent is publicly available as a GitHub repository4,
so we replicated it as Swe-agent-rep with the default
setting based on the provided scripts. In contrast to Sweagent, we do not have access to Magis, so we take the
most relevant reported result from their technical report
[32]. To avoid the natural randomness of LLM,
we repeat our experiments with AutoCodeRover and Sweagent-rep on SWE-bench lite three times. We use (1) the
percentage of resolved instances, (2) average time cost,
and (3) average token cost to evaluate the effectiveness of
the tools. The three evaluation metrics represent overall
effectiveness, time efficiency, and economic efficacy in
resolving real-world GitHub issues. For AutoCodeRover
and Swe-agent-rep, we report the average and total number of resolved instances across three repetitions.
""".replace("\n", " "))




# 主控已经不需要再做什么了，让主控进入休眠状态，让智能体们完成任务
import time
time.sleep(3600)