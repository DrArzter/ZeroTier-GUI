from typing import Callable, TypeVar, Coroutine, Any
from loguru import logger
from functools import wraps

R = TypeVar("R")
T = TypeVar("T")

def async_logging(func: Callable[..., Coroutine[Any, Any, R]]) -> Callable[..., Coroutine[Any, Any, R]]:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> R:
        logger.info(f"Calling {func.__name__}")
        try:
            result = await func(*args, **kwargs)
            logger.info(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed: {str(e)}")
            raise
    return wrapper

def handle_http_status(func: Callable[..., Coroutine[Any, Any, R]]) -> Callable[..., Coroutine[Any, Any, R]]:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> R:
        result = await func(*args, **kwargs)
        if result.status != 200:
            raise Exception(f"HTTP status {result.status} returned")
        return result
    return wrapper

def handle_exceptions(func: Callable[..., Coroutine[Any, Any, R]]) -> Callable[..., Coroutine[Any, Any, R]]:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> R:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise e
    return wrapper 