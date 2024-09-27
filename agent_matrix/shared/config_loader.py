import importlib
import time
import os


from loguru import logger
from functools import lru_cache


pj = os.path.join
default_user_name = 'default_user'


def read_env_variable(arg, default_value):

    arg_with_prefix = "AGENT_MATRIX_" + arg
    if arg_with_prefix in os.environ:
        env_arg = os.environ[arg_with_prefix]
    elif arg in os.environ:
        env_arg = os.environ[arg]
    else:
        raise KeyError
    logger.info(f"[ENV_VAR] Loading {arg}, default value: {default_value} --> modified value: {env_arg}")
    try:
        if isinstance(default_value, bool):
            env_arg = env_arg.strip()
            if env_arg == 'True': r = True
            elif env_arg == 'False': r = False
            else: logger.error('Enter True or False, but have:', env_arg); r = default_value
        elif isinstance(default_value, int):
            r = int(env_arg)
        elif isinstance(default_value, float):
            r = float(env_arg)
        elif isinstance(default_value, str):
            r = env_arg.strip()
        elif isinstance(default_value, dict):
            r = eval(env_arg)
        elif isinstance(default_value, list):
            r = eval(env_arg)
        elif default_value is None:
            assert arg == "proxies"
            r = eval(env_arg)
        else:
            logger.error(f"[ENV_VAR] Setting ({arg}) does not support changing by environment variable!")
            raise KeyError
    except:
        logger.error(f"[ENV_VAR] Load env variable ({arg}) fail! ")
        raise KeyError(f"[ENV_VAR] Load env variable ({arg}) fail! ")

    logger.info(f"[ENV_VAR] Load env variable successful ({arg}).")
    return r


@lru_cache(maxsize=128)
def read_single_conf_with_lru_cache(arg):
    try:
        # 优先级1. 获取环境变量作为配置
        default_ref = getattr(importlib.import_module('agent_matrix.config'), arg) # 读取默认值作为数据类型转换的参考
        r = read_env_variable(arg, default_ref)
    except:
        try:
            # 优先级2. 获取config_private中的配置
            r = getattr(importlib.import_module('config_private'), arg)
        except:
            # 优先级3. 获取config中的配置
            r = getattr(importlib.import_module('agent_matrix.config'), arg)

    # 在读取API_KEY时，检查一下是不是忘了改config
    return r


@lru_cache(maxsize=128)
def get_conf(*args):
    res = []
    for arg in args:
        r = read_single_conf_with_lru_cache(arg)
        res.append(r)
    if len(res) == 1: return res[0]
    return res


def set_conf(key, value):
    read_single_conf_with_lru_cache.cache_clear()
    get_conf.cache_clear()
    os.environ[key] = str(value)
    altered = get_conf(key)
    return altered


def set_multi_conf(dic):
    for k, v in dic.items(): set_conf(k, v)
    return
