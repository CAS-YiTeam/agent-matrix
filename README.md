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
