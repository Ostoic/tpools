import trio
import tpool

async def basic_guy(lock, i, flags):
	async with lock:
		flags[i] = True

	await trio.sleep(1)
	print(f'{i=} end')

async def test_pool():
	flags = [False] * 100
	lock = trio.Lock()

	with trio.fail_after(55):
		async with tpool.open_task_pool(concurrency=5) as pool:
			for i in range(10):
				await pool.start(basic_guy, lock, i, flags)
