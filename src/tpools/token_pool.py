import functools
import uuid
import trio

class Task:
	def __init__(self, fn, *args, **kwargs):
		self.id = uuid.uuid4()
		self.nullary = functools.partial(fn, *args, **kwargs)

class TokenPool:
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
			task_id = uuid.uuid4()
			if not self.full():
				async with self._lock:
					if not self.full():
						if value is None:
							value = uuid.uuid4()

						self._dict[task_id] = value
						return task_id

			await trio.lowlevel.checkpoint()

	async def leave(self, task_id):
		async with self._lock:
			result = self._dict.pop(task_id)
		return result
