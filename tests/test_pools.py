import trio
import tp

async def basic_guy(lock, i, flags):
	async with lock:
		flags[i] = True

	await trio.sleep(0.1)
	print(f'{i=} end')

async def test_pool():
	flags = [False] * 100
	lock = trio.Lock()

	with trio.fail_after(55):
		async with tp.open_task_pool(concurrency=20) as pool:
			for i in range(100):
				await pool.start(basic_guy, lock, i, flags)
