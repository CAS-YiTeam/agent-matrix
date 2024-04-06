from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel
from enum import auto, Enum

# class UserInterfaceMsg_Command(Enum):
#     # matrix -> ue
#     connect_to_matrix   =  "connect_to_matrix"

#     # ue -> matrix
#     update_script       =  "update_script"
#     update_location     =  "update_location"
#     play_event          =  "play_event"
#     parent_play_event   =  "parent_play_event"
#     create_agent        =  "create_agent"
#     agent_activate      =  "agent_activate"
#     duplicate_agent     =  "duplicate_agent"
#     connect_agent       =  "connect_agent"
#     disconnect_agent    =  "disconnect_agent"

#     update_agents       =  "update_agents"


class UserInterfaceMsg(BaseModel):
    """ Warning: this class must be modified together with agentcraft:
        `struct FMatrixMsgStruct`

    Args:
        BaseModel (_type_): _description_
    """

    src: str # source agent id

    dst: str # destination agent id

    command: str #| UserInterfaceMsg_Command

    arg: str = ""

    kwargs: str = ""

    need_reply: bool = False

    reserved_field_01: str = ""

    reserved_field_02: str = ""

    reserved_field_03: str = ""

    reserved_field_04: str = ""

    reserved_field_05: str = ""

    reserved_field_06: str = ""

    reserved_field_07: str = ""

    reserved_field_08: str = ""
