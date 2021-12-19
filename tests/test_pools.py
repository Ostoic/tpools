import trio
import tpools

async def race_lock(lock, i, flags):
	async with lock:
		flags[i] = True

async def test_pool():
	pass

async def test_task_pool():
	flags = [False] * 10
	lock = trio.Lock()

	with trio.fail_after(55):
		# Open a pool where 10 tasks race for the above lock, but are throttled to 5 tasks at a time.
		async with tpools.open_task_pool(concurrency=5) as pool:
			for i in range(10):
				await pool.spawn(race_lock, lock, i, flags)

	for flag in flags:
		assert flag
