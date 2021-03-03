import inspect
import uuid
import trio
from contextlib import asynccontextmanager

class Task:
	def __init__(self, fn, *args, **kwargs):
		self.id = uuid.uuid4()
		self.fn = fn
		self.args = args
		self.kwargs = kwargs

	def nullary_form(self):
		async def _nullary(*args, **kwargs):
			return await self.fn(*self.args, **self.kwargs)
		return _nullary

class Pool:
	def __init__(self, max_size=10):
		self._max_size = max_size
		self._dict = {}
		self._lock = trio.Lock()

	def __str__(self):
		return str(self._dict)

	def __len__(self):
		return len(self._dict)

	def can_join(self) -> bool:
		return not self.full()

	def full(self) -> bool:
		return len(self) >= self._max_size

	async def enter(self, value=None):
		while True:
			id = uuid.uuid4()
			if not self.full():
				async with self._lock:
					if not self.full():
						if value is None:
							value = uuid.uuid4()

						self._dict[id] = value
						return id

			await trio.lowlevel.checkpoint()

	async def leave(self, id):
		async with self._lock:
			result = self._dict.pop(id)
		return result

class AsyncTaskPool:
	def __init__(self, nursery, concurrency=10):
		self._nursery = nursery
		self._concurrency = concurrency
		self._active_tasks = Pool(max_size=concurrency)

	def cancel(self):
		self._nursery.cancel_scope.cancel()

	async def start(self, fn, *args, **kwargs) -> Task:
		async def task_stub(*args, **kwargs):
			token = await self._active_tasks.enter()
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
		self._nursery.start_soon(task.nullary_form())
		return task

	# async def stop(self, task):
	# 	self.

@asynccontextmanager
async def open_task_pool(concurrency=10) -> AsyncTaskPool:
	async with trio.open_nursery() as n:
		pool = AsyncTaskPool(nursery=n, concurrency=concurrency)
		yield pool