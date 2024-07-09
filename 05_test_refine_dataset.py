############ 加载数据集 ############
from datasets import load_dataset
def my_load_dataset(path):
    dataset = load_dataset(path)
    dataset = dataset.shuffle(seed=42)
    for k, ds in dataset.items():
        print(k)
    def preview_dataset(dataset, num_samples=5):
        for i in range(num_samples):
            print(dataset[i])
        print(' ------------------ end preview ----------------')
    print(set(dataset['train']['kind']))
    preview_dataset(dataset['train'])
    return dataset
dataset = my_load_dataset(
    "/home/hmp/llm/prj/filtered_dataset"
)



############ 定义并激活智能体 ############
def on_agent_finish(d):
    with open("llm2.log", "a+", encoding='utf-8') as f:
        print(str(d['main_input']), file=f)

import time
from agent_matrix.matrix.matrix_mastermind import MasterMindMatrix
from textwrap import dedent
def create_agent_arg_dict(**kwargs): return kwargs
mmm = MasterMindMatrix(host='localhost', port=10101, dedicated_server=False).begin_event_loop_non_blocking()
emoji_reviser = mmm.create_child_agent(
    agent_id=f"emoji_reviser",
    agent_class="agent_matrix.agent.agent_basic_qa->BasicQaAgent",
    agent_kwargs={
        "finish_callback": on_agent_finish,
        "sys_prompt": "",
        "query_construction":
            dedent(
                """
                The Original Question and Answer are as follows:

                {MAIN_INPUT_PLACEHOLDER}\n

                Can you add one or two emojis to the Answer to make it more interesting?
                You should note that only one or two emojis are enough, do not add too many of them.
                You should only return the emoji-revised answer using Chinese.
                """
            )
    },
)
emoji_reviser.activate_all_children()


############ 处理数据集（用线程池并行处理） ############
max_workers = 2
def process_samples(sample):
    build_main_input = 'Question is:\n\n' + sample['input'] + '\n\n---\n\n\Original answer is:\n\n' + sample['target']
    # print(build_main_input)
    future = emoji_reviser.wakeup(build_main_input)
    res = future.wait_and_get_result()

from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=max_workers)
futures = []
for i, sample in enumerate(dataset['train']):
    if sample['kind'] != 'OpenQA': continue
    futures.append(executor.submit(process_samples, sample))

while True:
    worker_done = [h.done() for h in futures]
    if all(worker_done):
        executor.shutdown()
        break

time.sleep(3600) # 已经不需要再做什么了，让主控进入休眠状态，让智能体们完成任务
