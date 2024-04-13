from agent_matrix.matrix.matrix_mastermind import MasterMindMatrix
# from agent_matrix.agent.agent_basic import Agent

"""
复现OpenAI的Meta-Prompting
"""

mmm = MasterMindMatrix(host='localhost', port=10101, dedicated_server=False)
mmm.begin_event_loop_non_blocking()

# 在母体中，创建一个校对智能体
agent_proofreader = mmm.create_agent(
    agent_id=f"proofreader",
    agent_class="agent_matrix.agent.agent->BasicQaAgent",
    agent_kwargs={"sys_prompt":
        "你是一个校对员，你的任务是校对文本，找出其中的错误。你的队伍中还有一个润色员和一个中文本地化员，你只需要做好自己的分内工作，不能僭越其他人的工作。"
    }
)

# 在母体中，创建一个润色智能体
agent_kwargs = {""}
agent_polisher = mmm.create_agent(
    agent_id=f"polisher",
    agent_class="agent_matrix.agent.agent->BasicQaAgent",
    agent_kwargs={"sys_prompt":
        "你是一个润色员，你的任务是润色文本。你的队伍中还有一个校对员和一个中文本地化员，你只需要做好自己的分内工作，不能僭越其他人的工作。"
    }
)

# 在母体中，创建一个中文专业化智能体
agent_chinese_localization_worker = mmm.create_agent(
    agent_id=f"chinese_localization_worker",
    agent_class="agent_matrix.agent.agent->BasicQaAgent",
    agent_kwargs={"sys_prompt":
        "你是一个中文本地化专员，你的任务是将不符合中文语言习惯的句子进行修改。你的队伍中还有一个校对员和一个润色员，你只需要做好自己的分内工作，不能僭越其他人的工作。"
    }
)

# 用明确的边连接定义智能体的交互
agent_proofreader.create_edge_to(dst_agent_id=agent_polisher)
agent_polisher.create_edge_to(dst_agent_id=agent_chinese_localization_worker)

# 好了，一切就绪，激活所有智能体，让他们开始工作
mmm.activate_agent(agent_id=f"proofreader")
mmm.activate_agent(agent_id=f"polisher")
mmm.activate_agent(agent_id=f"chinese_localization_worker")


agent_proofreader.wakeup("""
国内企业非常重视群体系统的落地应用。
以京东和菜鸟为代表的一些企业也在群体系统领域投入了大量的研究。如图~\ref{fig:jd-deliver} 所示，京东仓储物流基本实现了仓库内以多无人车系统代替人工的自动化流程，建立了以自动导引车（Automated Guided Vehicle, AGV）和拣货机械臂相互配合的物流分拣系统，降本增效提高了货物归纳和分拣的效率。受到近年来高速发展的互联网经济影响，国内其他涉及仓储物流的创业公司也都加大了对货运机器人集群的投入，如极智嘉，隆博科技AICROBO，蓝胖子Dorabot等。在无人机集群灯光表演上，亿航无人机于2017年在广州塔前完成了1180架无人机集群编队灯光表演，随后，高巨无人机于2019年以2100架无人机集群编队表演献礼新中国成立70周年，再次刷新了记录。群体智能技术辅助下的高效物流网络逐渐我国基础设施的一部分，例如在2020年新冠疫情的高峰期间，顺畅的物流设施对于防疫工作开展起到了至关重要的作用。
在游戏仿真当中，腾讯提出一个具有低耦合和高可扩展性的深度强化学习框架\citep{ye2020mastering}，解决了王者荣耀游戏中的AI智能体训练问题，可以在多智能体博弈环境下击败顶级职业人类玩家。阿里巴巴认知计算实验室设计了多智能体双向协调网络 (Bidirectionally-Coordinated Network，简称BiCNet），可以促进智能体之间的通信协作学习，实现了智能体在网络隐含层进行信息传递与沟通，并在星际争霸游戏中实现了群体协调移动与攻击等战术生成 \citep{peng2017multiagent}。
""")

# 主控已经不需要再做什么了，让主控进入休眠状态，让智能体们完成任务
import time
time.sleep(3600)
# sys.pause()