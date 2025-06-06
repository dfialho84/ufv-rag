import signal
import time
from functools import wraps
from types import FrameType
from typing import Callable, Optional

ShouldStopFn = Callable[[], bool]


def safe_interrupt_loop(func: Callable[[], None]) -> Callable[[], None]:
    stop_requested = False

    def signal_handler(sig: int, frame: Optional[FrameType]) -> None:
        nonlocal stop_requested
        print("\nInterruption requested. Stopping after current iteration...")
        stop_requested = True

    @wraps(func)
    def wrapper() -> None:
        nonlocal stop_requested
        # Registra o handler de interrupção
        signal.signal(signal.SIGINT, signal_handler)
        # Chama a função principal com acesso à flag
        func(lambda: stop_requested)  # type: ignore

    return wrapper
