from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel
from textwrap import dedent, indent

class SpecialDownstream:
    def __init__(self, downstream) -> None:
        self.downstream = downstream
    def __eq__(self, __value: object) -> bool:
        return __value == self.downstream

class SpecialDownstreamSet:
    auto_downstream = SpecialDownstream("auto_downstream")
    return_to_parent = no_downstream = SpecialDownstream("return_to_parent")

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
    flow_uid: str = None
        # the initial uid of the workflow, used to track the whole process

    src: str
        # source agent id

    dst: str
        # destination agent id

    command: str
        # enum "connect_to_matrix"
        # enum "agent_activate"

    num_step: int = 0
        # how many steps this message has been passed in the workflow

    need_reply: bool = False
        # whether this message needs a reply

    downstream_override: str = None
        # which downstream to use

    downstream_split_override: List[str] = None
        # allow one agent to wake up multiple children
        # warning: when `downstream_split_override` is set, 
        #          `downstream_override` must be None, 
        #          and `kwargs` must be a list that equals the length of `downstream_split_override`

    downstream_see_you_again_waitlist: List[List[str]] = []
        # when a flow is splited, we use this stack list to re-join the splited flow in some special join agents

    downstream_see_you_again_uid: List[str] = []
        # when a flow is splited, we use this stack uid to re-join the splited flow in some special join agents

    downstream_see_you_again_msg_arr: List["GeneralMsg"] = []
        # when a flow is splited, we use this pass re-joined messages

    children_select_override: str = None
        # explicitly select children

    call_children_again: bool = False
        # call children agent once more

    dictionary_logger: dict = {}
        # record trivial stuff accumulated during the workflow

    kwargs: dict = {}
        # downstream arguments (including main_input)

    level_shift: str = '→' # from  '↑', '↓', '→'
        # '→': pass to agents in the same level
        # '↑': pass to agents in the upper level (pass to parent)
        # '↓': pass to agents in the lower level (pass to children)

    def print_string(self):
        return print_msg_string(self.kwargs, self)

    def get(self, msg, default=None):
        return self.kwargs.get(msg, default)