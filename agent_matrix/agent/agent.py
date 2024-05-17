import time
import pickle
import threading
try:
    from websockets.sync.client import connect
except ImportError:
    raise ImportError("Import websockets failed, upgrade websockets by running: pip install websockets --upgrade")
from agent_matrix.msg.general_msg import GeneralMsg
from threading import Event


class AgentProperties(object):

    def __init__(self, **kwargs) -> None:
        self.is_proxy = kwargs["is_proxy"]
        self.agent_id = kwargs["agent_id"]
        self.proxy_id = '_proxy_' + self.agent_id
        self.matrix_host = kwargs["matrix_host"]
        self.matrix_port = kwargs["matrix_port"]
        self._websocket_connection = None
        self._activation_event = Event()
        self.activate = False

    @property
    def agent_status(self):
        if not hasattr(self, "_agent_status"):
            self._agent_status = agent_status_default = ""
        return self._agent_status

    @agent_status.setter
    def agent_status(self, value):
        if not hasattr(self, "_agent_status"):
            self._agent_status = agent_status_default = ""
        self._agent_status = self.update_property("agent_status", value)

    @property
    def agent_location(self):
        if not hasattr(self, "_agent_location"):
            self._agent_location = agent_location_default = [0, 0, 0]
        return self._agent_location

    @agent_location.setter
    def agent_location(self, value):
        if not hasattr(self, "_agent_location"):
            self._agent_location = agent_location_default = [0, 0, 0]
        self._agent_location = self.update_property("agent_location", value)

    @property
    def agent_animation(self):
        if not hasattr(self, "_agent_animation"):
            self._agent_animation = agent_animation_default = "Standing"
        return self._agent_animation

    @agent_animation.setter
    def agent_animation(self, value):
        if not hasattr(self, "_agent_animation"):
            self._agent_animation = agent_animation_default = "Standing"
        self._agent_animation = self.update_property("agent_animation", value)

    @property
    def agent_request(self):
        if not hasattr(self, "_agent_request"):
            self._agent_request = agent_request_default = ""
        return self._agent_request

    @agent_request.setter
    def agent_request(self, value):
        if not hasattr(self, "_agent_request"):
            self._agent_request = agent_request_default = ""
        self._agent_request = self.update_property("agent_request", value)

    def update_property(self, property_name, property_value):
        msg = GeneralMsg(src=self.agent_id, dst=self.proxy_id, command="on_update_status", kwargs={"property_name": property_name, "property_value": property_value})
        self._send_msg(msg)
        return property_value


class AgentCommunication():

    def _connect_to_matrix(self):
        # do not call this function directly
        host = self.matrix_host
        port = str(self.matrix_port)
        self._websocket_connection = connect(f"ws://{host}:{port}/ws_agent")
        msg = GeneralMsg(src=self.agent_id, dst="matrix", command="connect_to_matrix", kwargs={"agent_id": self.agent_id})
        self._send_msg(msg)

    def _send_msg(self, msg):
        # do not call this function directly
        self._websocket_connection.send(pickle.dumps(msg))

    def _recv_msg(self):
        # do not call this function directly
        msg: GeneralMsg = pickle.loads(self._websocket_connection.recv())
        return msg

    def _begin_acquire_command(self):
        # do not call this function directly
        while True:
            # block and wait for command
            msg = self._recv_msg()
            # handle command
            self._handle_command(msg)
            # reply if needed
            if msg.need_reply:
                msg.dst, msg.src = msg.src, msg.dst
                msg.command += '.re'
                msg.need_reply = False
                self._send_msg(msg)

    def _handle_command(self, msg: GeneralMsg):
        # do not call this function directly
        if msg.command == "activate_agent":
            self.activate_agent()
        elif msg.command == "deactivate_agent":
            self.deactivate_agent()
        elif msg.command == "on_agent_wakeup":
            # deal with the message from upstream
            msg.num_step += 1
            if msg.level_shift == '↑':
                # Case 2:
                # - This agent must be a parent with at leat one child agent,
                #   and all its children have finished their tasks.
                #   It is time that this parent exam all the work done by its children
                #   and decide what to do next.
                downstream = self.on_children_fin(msg.kwargs, msg)
            else:
                # Case 1:
                # - If this agent is a parent (with at least one child agent),
                #   on_agent_wakeup will be called, and its children will handle more work afterwards.
                # - If this agent has no children,
                #   on_agent_wakeup will be called.
                downstream = self.on_agent_wakeup(msg.kwargs, msg)

            # deliver message to downstream
            # (don't worry, agent proxy will deal with it,
            # e.g. chosing the right downstream agent)
            self.on_agent_fin(downstream, msg)
        else:
            raise NotImplementedError


class AgentBasic(AgentProperties, AgentCommunication):

    def on_agent_wakeup(self, kwargs, msg):
        raise NotImplementedError

    def on_children_fin(self, kwargs, msg):
        raise NotImplementedError

    def on_agent_fin(self, downstream, msg):
        msg.src = self.agent_id
        msg.dst = self.proxy_id
        msg.command = "on_agent_fin"
        msg.kwargs = downstream
        # for switch agent, add downstream_override
        if downstream.get("downstream_override", None):
            msg.downstream_override = downstream["downstream_override"]
        # keep level shift unchanged
        msg.level_shift = msg.level_shift
        self._send_msg(msg)

    def activate_agent(self):
        self._activation_event.set()

    def deactivate_agent(self):
        self._activation_event.clear()

    def agent_task_cycle(self):
        raise NotImplementedError

    def run_non_blocking(self):
        # start a new thread to run the agent task cycle
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

    def run(self):
        self.com_websocket = self._connect_to_matrix()
        threading.Thread(target=self._begin_acquire_command, daemon=True).start()
        while True:
            if self._activation_event.is_set():
                tic = time.time()
                self.agent_task_cycle()
                toc = time.time()
                if toc - tic < 1.0:
                    time.sleep(1.0)  # avoid frequent task cycles that is less than 1 second
            else:
                self._activation_event.wait()

    def __del__(self):
        try:
            self._websocket_connection.close()
        except:
            pass


class Agent(AgentBasic):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def agent_task_cycle(self):
        print('Hi, you have to implement this function (Agent.agent_task_cycle) in your subclass.')
        time.sleep(2.0)
        raise NotImplementedError

    def on_agent_wakeup(self, kwargs, msg):
        print('Hi, you have to implement this function (Agent.on_agent_wakeup) in your subclass.')
        time.sleep(2.0)
        raise NotImplementedError

    def on_children_fin(self, kwargs, msg):
        print('Hi, you have to implement this function (Agent.on_children_fin) in your subclass.')
        time.sleep(2.0)
        raise NotImplementedError


class EchoAgent(Agent):
    def agent_task_cycle(self):
        return

    def on_agent_wakeup(self, kwargs, msg):
        return kwargs

    def on_children_fin(self, kwargs, msg):
        return kwargs
