from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel
from textwrap import dedent, indent
auto_downstream = "auto_downstream"
no_downstream = "no_downstream"

def concrete_str(string, clip_long=True):
    res = string.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').replace('  ', ' ') # .replace(']', '】').replace('[', '【')
    if clip_long: res = len_limit(res)
    return res

def len_limit(string):
    if len(string) > 350:
        return string[:200] + f' 「... (hide {len(string)-300} chars) ...」 ' + string[-100:]
    return string

def print_msg_string(kwargs, msg, auto_clip=True):
    def print_kwargs(kwargs):
        buf = "\n"
        keys = list(kwargs.keys())
        vip_order = ["sys_prompt", "history", "query", "raw_output"]
        no_clip = ["raw_output"]
        for k in (vip_order):
            if k in keys:
                keys.remove(k)
                keys = list(keys) + [k]
        #
        for k in keys:
            v = kwargs[k]
            color = "red" if k in vip_order else "blue"
            if isinstance(v, list):
                # add space before each
                v_arr = v
                v = "\n"
                for index, item in enumerate(v_arr):
                    # print('****', item)
                    ccstr = concrete_str(str(item))
                    v += f"[{color}]{index}:[/{color}]{ccstr}\n"
            if isinstance(v, str):
                # add a new line before the string,
                # then remove line break inside this string
                if not str(v).startswith('\n'):
                    v = '\n' + concrete_str(str(v), clip_long=((auto_clip) and (k not in no_clip)))
            else:
                # add a new line before the string,
                # then remove line break inside this string
                if not str(v).startswith('\n'):
                    v = '\n' + concrete_str(str(v))
            # add indent
            v = indent((str(v)), "    ")
            buf += f"[{color}]{k}[/{color}]: {v}\n\n"
        return indent(buf, "    ")

    string_msg = dedent(
        f"""
        [green]- agent:[/green] {msg.dst}
        [green]- command:[/green] {msg.command}
        [green]- kwargs:[/green]"""
    ) + f"{print_kwargs(kwargs)}"
    return string_msg


class GeneralMsg(BaseModel):
    src: str
        # source agent id

    dst: str
        # destination agent id

    command: str
        # enum "connect_to_matrix"
        # enum "agent_activate"

    num_step: int = 0

    need_reply: bool = False

    downstream_override: str = None

    kwargs: dict = {}

    level_shift: str = '→' # from  '↑', '↓', '→'

    def print_string(self):
        return print_msg_string(self.kwargs, self)

    def get(self, msg, default=None):
        return self.kwargs.get(msg, default)