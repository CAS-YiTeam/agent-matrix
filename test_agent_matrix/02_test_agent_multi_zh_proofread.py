import init_test # 修正测试路径到项目根目录，这样才能正确导入agent_matrix
from agent_matrix.matrix.matrix_mastermind import MasterMindMatrix
from agent_matrix.agent.agent_basic_qa import BasicQaAgent

"""
原始文本 -> 校对者 -> 润色者 -> 去口语化 -> 汇总者
"""

mmm = MasterMindMatrix(host='localhost', port=10101, dedicated_server=False)
mmm.begin_event_loop_non_blocking()
位面 = mmm.create_agent(
    agent_id=f"nest",
    agent_class="agent_matrix.agent.agent->EchoAgent",
    agent_kwargs={}
)

智能体_校对者 = 位面.create_agent(
    agent_id=f"校对者",
    agent_class=BasicQaAgent,
    agent_kwargs={
        "sys_prompt": "你是一个中文写作专家，任务是校对文本，找出其中的错误。你只需要做好自己的分内工作即可。使用中文。",
        "query_construction": "{MAIN_INPUT_PLACEHOLDER}\n" + "Do your job according to the instructions, consider the results from other agents."
    }
)

agent_kwargs = {""}
智能体_润色者 = 位面.create_agent(
    agent_id=f"润色者",
    agent_class=BasicQaAgent,
    agent_kwargs={
        "sys_prompt": "你是一个中文写作专家，任务是润色文本。你只需要做好自己的分内工作即可。使用中文。",
        "query_construction": "Do your job according to the instructions, consider the results from other agents if there are any."
    }
)

智能体_去口语化 = 位面.create_agent(
    agent_id=f"去口语化",
    agent_class=BasicQaAgent,
    agent_kwargs={
        "sys_prompt": "你是一个中文写作专家，你的任务是对不符合中文书面语言习惯的句子进行修改。你只需要做好自己的分内工作即可。使用中文。",
        "query_construction": "Do your job according to the instructions, consider the results from other agents if there are any."
    }
)

智能体_汇总者 = 位面.create_agent(
    agent_id=f"汇总者",
    agent_class=BasicQaAgent,
    agent_kwargs={
        "sys_prompt": "你的任务是将校对者、润色者和本地化者的工作结果进行汇总，形成最终的文本。不得输出除最终文本之外的任何废话。使用中文。",
        "query_construction": "Do your job according to the instructions, consider the results from other agents if there are any."
    }
)



# 用明确的边连接定义智能体的交互
智能体_校对者.create_edge_to(dst_agent_id=智能体_润色者)
智能体_润色者.create_edge_to(dst_agent_id=智能体_去口语化)
智能体_去口语化.create_edge_to(dst_agent_id=智能体_汇总者)

# 好了，一切就绪，激活所有智能体，让他们开始工作
位面.activate_all_children()

位面.wakeup(r"""
你需要处理的材料如下：
国内企业非常重视群体系统的落地应用。以京东和菜鸟为代表的一些企业也在群体系统领域投入了大量的研。如图~\ref{fig:jd-deliver} 所示，京东仓储物流基本实现仓库内以多无人车系统代替人工的自动化流程，建立了以自动导引车（Automated Guided Vehicle, AGV）和拣货机械臂相互配合的物流分拣系统，降本增效提高了货物归纳和分拣的效率。受到近年来高速发展的互联网经济影响，国内其他涉及仓储物流的创业公司也都加大了对货运机器人集群的投入，如极智嘉，隆博科技AICROBO，蓝胖子Dorabot等。在无人机集群灯gehtqgew光表演上，亿航无人机于2017年在广州塔前完成了1180架无人机集群编队灯光表演，随后，高巨无人机于2019年以2100架无人机集群编队表演献礼新中国成立70周年，再次刷新了记录。群体智能技术辅助下的高效物流网络逐渐我国基础设施的一部分，例如在2020年新冠疫情的高峰期间，顺畅的物流设施对于防疫工作开展起到了至关重要的作用。在游戏仿真当中，腾讯提出一个具有低耦合和高可扩展性的深度强化学习框架\citep{ye2020mastering}，解决了王者荣耀游戏中的AI智能体训练问题，可以在多智能体博弈环境下击败顶级职业人类玩家。阿里巴巴认知计算实验室设计了多智能体双向协调网络 (Bidirectionally-Coordinated Network，简称BiCNet），可以促进智能体之间的通信协作学习，实现了智能体在网络隐含层进行信息传递与沟通，并在星际争霸游戏中实现了群体协调移动与攻击等战术生成 \citep{peng2017multiagent}。
""")

input('主线程进入休眠状态，让智能体们完成任务')