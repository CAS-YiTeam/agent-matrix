from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel
from textwrap import dedent, indent
downstream = "downstream"

def concrete_str(string):
    res = string.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').replace('  ', ' ')
    return res

def len_limit(string):
    if len(string) > 350:
        return string[:200] + f' [... (hide {len(string)-300} chars) ...] ' + string[-100:]
    return string

def print_msg_string(kwargs, msg):
    def print_kwargs(kwargs):
        buf = "\n"
        keys = list(kwargs.keys())
        if "history" in keys:
            keys.remove("history")
            keys = ["history"] + list(keys)
        for k in keys:
            v = kwargs[k]
            if isinstance(v, list):
                # add space before each
                v_arr = v
                v = "\n"
                for index, item in enumerate(v_arr):
                    # print('****', item)
                    ccstr = concrete_str(str(item))
                    v += f"[red]{index}:[/red]{ccstr}\n"
            if isinstance(v, str):
                # add a new line before the string,
                # then remove line break inside this string
                if not str(v).startswith('\n'):
                    v = '\n' + concrete_str(str(v))
            else:
                # add a new line before the string,
                # then remove line break inside this string
                if not str(v).startswith('\n'):
                    v = '\n' + concrete_str(str(v))
            if k == "raw_output":
                v = indent(str(v), "    ")
            else:
                v = indent(len_limit(str(v)), "    ")
            buf += f"[red]{k}[/red]: {v}\n\n"
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

    need_reply: bool = False

    downstream_override: str = downstream

    kwargs: dict = {}

    level_shift: str = '→' # from  '↑', '↓', '→'

    def print_string(self):
        return print_msg_string(self.kwargs, self)
