# Agent Matrix

<div align="center">
<img src="https://github.com/binary-husky/agent-matrix/assets/96192199/a51c4498-a5be-4ff6-9625-fd344108cf1f" width="200" >
</div>

The Core Insight of This Project: Achieving Higher Intelligence via **Nested** Agents.

<div align="center">
<img src=https://github.com/binary-husky/agent-matrix/assets/96192199/7d3e2856-9c37-46af-ba26-662f135ffac7" width="600" >
</div>

## Initialize


![image](https://github.com/binary-husky/agent-matrix/assets/96192199/991a47f3-e805-43d5-a62f-da7def5ba5f5)

```mermaid
flowchart LR
    launch --> |"method 1"| MASTER>"python master mind"]
    launch --> |"method 2"| UE2["Launch UE Client"]
    UE2 --> Redis3["Join Redis Network"]
    MASTER --> IF1{"Has UE ?"}
    IF1 -->|"Yes"| UE["Launch UE Client"]
    IF1 -->|"No"| UED["Download UE Client"]
    UED --> UE
    UE --> Redis2["Join Redis Network"]
    UE2 --> MASTER2>"python master mind"]
    MASTER --> Redis["Join Redis Network"]
    MASTER2 --> Redis["Join Redis Network"]
    Redis --> Wait["Wait Further Command"]
    Wait --> Begin(("Begin Tasks"))
```

## python agent tick

```mermaid
flowchart TD
    PyAgent["Agent Init"] --> A["Wait Wake Up Condition 等待唤醒"]
    -->AAA
    subgraph AAA["Thread 新线程"]
        direction LR
        TT1["New Thread Begin 线程启动"]
        TT1 --> BBB
        TT1 --> TT2["Read UUID"] -->
        TT3["Read Call History"] -->
        TT4["LM Call Python Pre-process"] -->
        TT5["LM Call"] -->
        TT6["LM Call Python Post-process"] -->
        TT7["Redis Com and Final Render"] -->
        TT8["Select Next Agents To Wake Up"] -->
        TT9["Wake Up Other Agents"] -->
        TT10["Exit"]


        TT5 --> Ta
        Ta --> TT5
        subgraph BBB["Thread 新线程2"]
        Ta["Redis Com and Stream Render"]
        end

    end

```


## unreal agent tick
```mermaid
flowchart TD
    subgraph Tick
        direction LR
        Tick_S["Tick Begin"] 
        --> Tick_A["Hear from Redis"]
        --> Tick_B["Update Status"]
        --> Tick_C["Read Event"]
        --> Tick_D["Do Event"]
    end
```


## agent university base class

```mermaid
flowchart LR
    Z["X"]
    Z --> A["Basic LM Agent"]
    Z --> B["Internet Agent"]
    Z --> C["RAG Agent"]
    Z --> D["Python Code Exe Agent"]
    Z --> E["Memory Agent"]
    Z --> F["CoT Agent"]
    Z --> G["Screen Capture Agent"]
    Z --> H["Windows Exe Agent"]
    Z --> I["Shell Exe Agent"]
    Z --> J["Realtime Voice Read Agent"]
    Z --> J2["Realtime Speaker Agent"]
```


## Agent Activation Call Cycle

1. upper stream agent proxy call current agent proxy's `___on_agent_wakeup___`

2. [`___on_agent_wakeup___` (anywhere)] current agent modify msg (msg = `on_agent_wakeup`+arguments) and `send_to_real_agent`

3. [`send_to_real_agent` (agent_matrix/agent/agent_proxy.py)]: `message_queue_send_to_real_agent`

4. [`_begin_acquire_command` (agent_matrix/agent/agent.py)]: real agent receive msg and execute `_handle_command`

5. [`_handle_command` (agent_matrix/agent/agent.py)]: real agent receive `on_agent_wakeup` and execute `wakeup_in_new_thread` (in new thread)

```python
    def wakeup_in_new_thread(self, msg):
        # deal with the message from upstream
        msg.num_step += 1
        if msg.level_shift == '↑':
            # Case 1:
            # - This agent must be a parent with at leat one child agent,
            #   and all its children have finished their tasks.
            #   It is time that this parent exam all the work done by its children
            #   and decide what to do next.
            downstream = self.on_children_fin(msg.kwargs, msg)
        else:
            # Case 2:
            # - If this agent is a parent (with at least one child agent),
            #   on_agent_wakeup will be called, and its children will handle more work afterwards.
            # - If this agent has no children,
            #   on_agent_wakeup will be called.
            downstream = self.on_agent_wakeup(msg.kwargs, msg)

        # deliver message to downstream
        # (don't worry, agent proxy will deal with it,
        # e.g. chosing the right downstream agent)
        self.on_agent_fin(downstream, msg)
```

6. [`on_agent_wakeup` (agent_matrix/agent/agent.py)]: real agent receive and execute `on_agent_wakeup`

7. [`on_agent_fin` (agent_matrix/agent/agent.py)]: terminate agent task, prepare msg delivery, register `downstream` to `msg`
```python
    def on_agent_fin(self, downstream, msg):
        msg.src = self.agent_id
        msg.dst = self.proxy_id
        msg.command = "on_agent_fin"
        msg.kwargs = downstream
        # for switch agent, add downstream_override
        if downstream.get("downstream_override", None):
            msg.downstream_override = downstream["downstream_override"]
        # for groupchat agent, add children_select_override
        if downstream.get("children_select_override", None):
            msg.children_select_override = downstream["children_select_override"]
        if downstream.get("call_children_again", None):
            msg.call_children_again = downstream["call_children_again"]
        if downstream.get("dictionary_logger", None) and isinstance(downstream["dictionary_logger"], dict):
            msg.dictionary_logger.update(downstream["dictionary_logger"])
        # keep level shift unchanged
        msg.level_shift = msg.level_shift
        self._send_msg(msg)
```