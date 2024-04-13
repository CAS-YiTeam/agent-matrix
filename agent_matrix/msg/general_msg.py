from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel
from .ui_msg import UserInterfaceMsg
from textwrap import dedent

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

    def print_string(self):
        string_msg = dedent(
            f"""
            - self.src: {self.src}
            - self.dst: {self.dst}
            - self.command: {self.command}
            - self.kwargs: {self.kwargs}
            """
        )
        return string_msg
