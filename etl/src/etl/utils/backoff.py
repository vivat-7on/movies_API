import logging
from functools import wraps
from time import sleep

logger = logging.getLogger(__name__)


def backoff(
        start_sleep_time: float = 0.1,
        factor: int = 2,
        border_sleep_time: int = 10,
        max_tries: int = 8,
        exceptions: tuple[type[Exception], ...] = (Exception,),
):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor)
    до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * (factor ^ n), если t < border_sleep_time
        t = border_sleep_time, иначе
    :param start_sleep_time: начальное время ожидания
    :param factor: во сколько раз нужно увеличивать время ожидания на каждой итерации
    :param border_sleep_time: максимальное время ожидания
    :param max_tries: количество попыток перезапустить функцию
    :param exceptions кортеж перехватываемых исключений
    :return: результат выполнения функции
    """
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            attempt = 1
            while attempt <= max_tries:
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    if attempt == max_tries:
                        logger.error(
                            "Max retries exceeded in %s",
                            func.__name__,
                            exc_info=True,
                        )
                        raise
                    sleep_time = min(
                        start_sleep_time * (factor ** attempt),
                        border_sleep_time,
                    )
                    logger.warning(
                        "Error in %s: %s. Retry %d/%d in %.1f seconds",
                        func.__name__,
                        exc.__class__.__name__,
                        attempt,
                        max_tries,
                        sleep_time,
                        exc_info=False,
                    )
                    sleep(sleep_time)
                    attempt += 1
        return inner

    return func_wrapper
