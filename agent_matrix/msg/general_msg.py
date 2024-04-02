from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel
from .ui_msg import UserInterfaceMsg

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
