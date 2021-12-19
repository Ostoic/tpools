import trio
import inspect
from contextlib import asynccontextmanager

from .token_pool import TokenPool, Task

# Throttled concurrent task pool
class AsyncTaskPool:
	def __init__(self, nursery, concurrency=10):
		self._nursery = nursery
		self._concurrency = concurrency
		self._active_tasks = TokenPool(max_size=concurrency)

	def cancel(self):
		self._nursery.cancel_scope.cancel()

	async def spawn(self, fn, *args, **kwargs) -> Task:
		token = await self._active_tasks.enter()

		async def task_stub(*args, **kwargs):
			try:
				if not inspect.iscoroutinefunction(fn):
					result = await trio.to_thread.run_sync(lambda: fn(*args, **kwargs))
				else:
					result = await fn(*args, **kwargs)
			finally:
				# Remove self from tasks list
				await self._active_tasks.leave(token)
			return result

		task = Task(task_stub, *args, **kwargs)
		self._nursery.start_soon(task.nullary)
		return task

@asynccontextmanager
async def open_task_pool(concurrency=10) -> AsyncTaskPool:
	async with trio.open_nursery() as n:
		pool = AsyncTaskPool(nursery=n, concurrency=concurrency)
		yield pool
