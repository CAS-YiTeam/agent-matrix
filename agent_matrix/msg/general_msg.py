from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel
from .ui_msg import UserInterfaceMsg
from textwrap import dedent, indent

def concrete_str(string):
    return string.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').replace('  ', ' ')


class GeneralMsg(BaseModel):
    src: str
        # source agent id

    dst: str
        # destination agent id

    command: str
        # enum "connect_to_matrix"
        # enum "agent_activate"

    need_reply: bool = False

    kwargs: dict = {}

    level_shift: str = '→' # from  '↑', '↓', '→'



    def print_string(self):

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

                v = indent(str(v), "    ")
                buf += f"[red]{k}[/red]: {v}\n\n"
            return indent(buf, "    ")

        string_msg = dedent(
            f"""
            [green]- src:[/green] {self.src}\t{self.level_shift}{self.level_shift}{self.level_shift}\t[green] dst:[/green] {self.dst}
            [green]- command:[/green] {self.command}
            [green]- kwargs:[/green]"""
        ) + f"{print_kwargs(self.kwargs)}"
        return string_msg
