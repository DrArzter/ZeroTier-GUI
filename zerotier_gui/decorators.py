from typing import Callable, TypeVar, Coroutine, Any
from loguru import logger
import functools

R = TypeVar("R")
T = TypeVar("T")

def async_logging(func: Callable[..., Coroutine[Any, Any, R]]) -> Callable[..., Coroutine[Any, Any, R]]:
    """Decorator for logging asynchronous functions."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> R:
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            logger.exception(f"Error in {func.__name__}: {e}")
            raise
    return wrapper

def handle_http_status(func: Callable[..., Coroutine[Any, Any, R]]) -> Callable[..., Coroutine[Any, Any, R]]:
    """Decorator for handling HTTP status codes.
    
    Raises an exception if the response status is not 200.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> R:
        result = await func(*args, **kwargs)
        if result.status != 200:
            raise Exception(f"HTTP status {result.status} returned")
        return result
    return wrapper

def handle_exceptions(func: Callable[..., Coroutine[Any, Any, R]]) -> Callable[..., Coroutine[Any, Any, R]]:
    """Decorator for handling exceptions in asynchronous functions.
    
    Logs the exception and returns None instead of propagating the exception.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> R:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Error in {func.__name__}: {e}")
            return None
    return wrapper 