import importlib


def hot_reload_class(agent_class):
    # agent_class = 'agent_matrix.matrix.mastermind_matrix->MasterMindWebSocketServer'
    module, fn_name = agent_class.split('->')
    f_hot_reload = getattr(importlib.import_module(module, fn_name), fn_name)
    return f_hot_reload