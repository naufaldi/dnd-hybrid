"""Concurrency utilities for the game."""

import asyncio
from typing import Callable, Any, Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime
import time


@dataclass
class TickConfig:
    """Configuration for the tick system."""

    tick_rate: float = 0.1  # seconds per tick
    max_ticks_per_second: float = 10.0
    enable_ticks: bool = True


class TickSystem:
    """Manages game ticks with configurable rate.

    Provides a coroutine-based tick loop that can be started/stopped
    and allows callbacks to be registered for tick events.
    """

    def __init__(self, config: Optional[TickConfig] = None):
        self.config = config or TickConfig()
        self._running = False
        self._tick_count: int = 0
        self._start_time: Optional[float] = None
        self._callbacks: list = []
        self._task: Optional[asyncio.Task] = None

    def register_callback(self, callback: Callable[[int], Any]) -> None:
        """Register a callback to be called on each tick.

        Args:
            callback: Async or sync function that receives tick count.
        """
        self._callbacks.append(callback)

    def unregister_callback(self, callback: Callable[[int], Any]) -> None:
        """Remove a registered callback.

        Args:
            callback: Callback to remove.
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    async def start(self) -> None:
        """Start the tick loop."""
        if self._running:
            return

        self._running = True
        self._start_time = time.time()
        self._task = asyncio.create_task(self._tick_loop())

    async def stop(self) -> None:
        """Stop the tick loop."""
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._task = None

    async def _tick_loop(self) -> None:
        """Main tick loop."""
        while self._running:
            tick_start = time.time()

            # Increment tick counter
            self._tick_count += 1

            # Call all registered callbacks
            for callback in self._callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(self._tick_count)
                    else:
                        callback(self._tick_count)
                except Exception:
                    # Log but don't stop ticking
                    pass

            # Calculate sleep time to maintain tick rate
            elapsed = time.time() - tick_start
            sleep_time = max(0, self.config.tick_rate - elapsed)
            await asyncio.sleep(sleep_time)

    @property
    def tick_count(self) -> int:
        """Get current tick count."""
        return self._tick_count

    @property
    def running(self) -> bool:
        """Check if tick system is running."""
        return self._running

    @property
    def uptime(self) -> float:
        """Get seconds since tick system started."""
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time


class AsyncSpawner:
    """Manages async spawning of entities/tasks.

    Provides rate-limited spawning to prevent overwhelming
    the game with too many simultaneous async operations.
    """

    def __init__(self, max_concurrent: int = 10, spawn_interval: float = 0.1):
        self.max_concurrent = max_concurrent
        self.spawn_interval = spawn_interval
        self._active_count: int = 0
        self._spawn_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start the spawner worker."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._worker_loop())

    async def stop(self) -> None:
        """Stop the spawner."""
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def spawn(
        self,
        coro: Callable[[], Any],
        on_complete: Optional[Callable[[Any], None]] = None
    ) -> None:
        """Queue a coroutine to be spawned.

        Args:
            coro: Coroutine or async function to execute.
            on_complete: Optional callback when spawning completes.
        """
        await self._spawn_queue.put((coro, on_complete))

    async def _worker_loop(self) -> None:
        """Worker that processes the spawn queue."""
        while self._running:
            # Wait if at max capacity
            while self._active_count >= self.max_concurrent and self._running:
                await asyncio.sleep(self.spawn_interval)

            if not self._running:
                break

            # Get next item from queue
            try:
                item = await asyncio.wait_for(
                    self._spawn_queue.get(),
                    timeout=self.spawn_interval
                )
            except asyncio.TimeoutError:
                continue

            coro, on_complete = item
            self._active_count += 1

            # Spawn the coroutine
            asyncio.create_task(self._run_and_notify(coro, on_complete))

    async def _run_and_notify(
        self,
        coro: Callable[[], Any],
        on_complete: Optional[Callable[[Any], None]]
    ) -> None:
        """Run a coroutine and call completion callback."""
        try:
            result = await coro()
            if on_complete:
                if asyncio.iscoroutinefunction(on_complete):
                    await on_complete(result)
                else:
                    on_complete(result)
        except Exception:
            pass
        finally:
            self._active_count -= 1

    @property
    def active_count(self) -> int:
        """Get number of active spawned tasks."""
        return self._active_count

    @property
    def queue_size(self) -> int:
        """Get number of items waiting to spawn."""
        return self._spawn_queue.qsize()


@dataclass
class WorkerTask:
    """Represents a worker task."""

    id: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    result: Any = None
    error: Optional[Exception] = None
    completed: bool = False


class WorkerPool:
    """Thread pool for running blocking operations.

    Provides a pool of workers that can execute tasks
    concurrently while keeping the async event loop free.
    """

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self._tasks: Dict[str, WorkerTask] = {}
        self._running = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    async def start(self) -> None:
        """Start the worker pool."""
        if self._running:
            return
        self._running = True
        self._loop = asyncio.get_event_loop()

    async def stop(self) -> None:
        """Stop the worker pool and wait for tasks."""
        self._running = False
        # Wait for all tasks to complete
        while any(not t.completed for t in self._tasks.values()):
            await asyncio.sleep(0.1)
        self._tasks.clear()

    async def submit(
        self,
        task_id: str,
        func: Callable,
        *args,
        priority: int = 0,
        **kwargs
    ) -> str:
        """Submit a task to the worker pool.

        Args:
            task_id: Unique identifier for the task.
            func: Function to execute.
            *args: Positional arguments for the function.
            priority: Task priority (higher = more important).
            **kwargs: Keyword arguments for the function.

        Returns:
            Task ID.
        """
        task = WorkerTask(
            id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority
        )
        self._tasks[task_id] = task

        # Run in thread pool to not block event loop
        if self._loop:
            await asyncio.sleep(0)  # Yield to event loop
            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: func(*args, **kwargs)
                )
                task.result = result
            except Exception as e:
                task.error = e
            task.completed = True

        return task_id

    def get_result(self, task_id: str) -> Any:
        """Get the result of a completed task.

        Args:
            task_id: Task ID.

        Returns:
            Task result, or None if not found/completed.
        """
        task = self._tasks.get(task_id)
        if task and task.completed:
            return task.result
        return None

    def is_complete(self, task_id: str) -> bool:
        """Check if a task is complete."""
        task = self._tasks.get(task_id)
        return task.completed if task else False

    def has_error(self, task_id: str) -> bool:
        """Check if a task had an error."""
        task = self._tasks.get(task_id)
        return task.error is not None if task else False

    def get_error(self, task_id: str) -> Optional[Exception]:
        """Get error from a failed task."""
        task = self._tasks.get(task_id)
        return task.error if task else None
