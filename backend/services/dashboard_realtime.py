from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class RealtimeState:
    version: int = 0
    event: asyncio.Event | None = None
    loop: asyncio.AbstractEventLoop | None = None


_states: dict[str, RealtimeState] = defaultdict(RealtimeState)


def key_for(tenant_id: int, user_id: int) -> str:
    return f"{tenant_id}:{user_id}"


def notify_dashboard_change(tenant_id: int, user_id: int) -> None:
    state = _states[key_for(tenant_id, user_id)]
    state.version += 1
    try:
        if state.event is None:
            return
        if state.loop and state.loop.is_running():
            state.loop.call_soon_threadsafe(state.event.set)
        else:
            state.event.set()
    except RuntimeError:
        # Sem loop ativo; o websocket também tem heartbeat para atualização eventual.
        pass


async def wait_for_dashboard_change(tenant_id: int, user_id: int, last_version: int, timeout: float = 30.0) -> int:
    state = _states[key_for(tenant_id, user_id)]
    loop = asyncio.get_running_loop()
    if state.loop is not loop or state.event is None:
        state.loop = loop
        state.event = asyncio.Event()
    if state.version != last_version:
        return state.version
    event = state.event
    try:
        await asyncio.wait_for(event.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        return state.version
    finally:
        event.clear()
    return state.version


def current_dashboard_version(tenant_id: int, user_id: int) -> int:
    return _states[key_for(tenant_id, user_id)].version
