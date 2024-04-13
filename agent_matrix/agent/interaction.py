import os
import sys
import time
import platform
import asyncio
import threading
from loguru import logger
from queue import Queue
from agent_matrix.agent.agent import Agent
import networkx as nx

class InteractionManager(object):
    def __init__(self, agent_proxy) -> None:
        self.agent_proxy = agent_proxy
        self.interaction_graph = nx.DiGraph()  # Directed graph
        pass

    def update_nodes(self):
        children = self.agent_proxy.direct_children
        for child in children:
            self.interaction_graph.add_node(child.agent_id)

    def create_edge(self, src_agent_id, dst_agent_id, channel=None):
        self.interaction_graph.add_edge(src_agent_id, dst_agent_id, channel=channel)

    def get_downstream(self):
        try:
            return self.interaction_graph.successors(self.agent_proxy.agent_id)
        except:
            return []


