# negotiation_engine/message_broker.py
import asyncio
import logging
from typing import Dict, List, Set, Callable, Awaitable, Any
from collections import defaultdict

logger = logging.getLogger(__name__)

class MessageBroker:
    """
    In-memory async message broker for agent communication.
    Supports publish-subscribe pattern.
    """

    def __init__(self):
        self.subscribers: Dict[str, Set[Callable[[Any], Awaitable[None]]]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def publish(self, topic: str, message: Any):
        """Publish a message to a topic."""
        async with self._lock:
            if topic in self.subscribers:
                tasks = [callback(message) for callback in self.subscribers[topic]]
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

    async def subscribe(self, topic: str, callback: Callable[[Any], Awaitable[None]]):
        """Subscribe to a topic."""
        async with self._lock:
            self.subscribers[topic].add(callback)

    async def unsubscribe(self, topic: str, callback: Callable[[Any], Awaitable[None]]):
        async with self._lock:
            if topic in self.subscribers:
                self.subscribers[topic].discard(callback)
                if not self.subscribers[topic]:
                    del self.subscribers[topic]

    async def clear(self):
        async with self._lock:
            self.subscribers.clear()

# Global broker instance
broker = MessageBroker()
