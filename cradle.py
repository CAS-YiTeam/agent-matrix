import asyncio
import time

# -=-=-=-=-=-=- 阻塞式异步（await coro，自动） =-=-=-=-=-=-=-=
# async def say_after():
#     await asyncio.sleep(1)
#     print('say_after')

# async def main(): # coroutine function
#     await asyncio.sleep(1)  # await blocking
#     await say_after()       # await non-blocking
#     await say_after()       # await non-blocking

# coro = main()
# asyncio.run(coro)


# -=-=-=-=-=-=- 非阻塞式异步（await task） =-=-=-=-=-=-=-=

async def nested():
    time.sleep(1)
    print('nested')
    await say_after()
    return

async def say_after():
    # coroutine function里面，所有函数都要加await（如果想嵌套），太傻比了
    await nested()
    await asyncio.sleep(1)
    print('say_after')

async def main(): # coroutine function
    coro1 = say_after() # create coroutine
    coro2 = say_after() # create coroutine
    
    task1 = asyncio.create_task(coro1)  # coroutine函数是从这里被允许运行的，而不是await
    task2 = asyncio.create_task(coro2)  # coroutine函数是从这里被允许运行的，而不是await
    
    res1 = await task1  # block 阻断
    res2 = await task2  # block 阻断

coro = main()
asyncio.run(coro)


# using task group


# -=-=-=-=-=-=- 非阻塞式异步（await TaskGroup） =-=-=-=-=-=-=-=
# async def main():
#     async with asyncio.TaskGroup() as tg:
#         task1 = tg.create_task(
#             say_after(1, 'hello'))

#         task2 = tg.create_task(
#             say_after(2, 'world'))

#         print(f"started at {time.strftime('%X')}")
#     # The await is implicit when the context manager exits.
#     print(f"finished at {time.strftime('%X')}")