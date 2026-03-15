from loguru import logger
import asyncio
from config import Config


async def delay():
    """Задержка между запросами"""
    await asyncio.sleep(Config.REQUEST_DELAY)


def setup_logging():
    """Настройка логирования"""
    logger.remove()
    logger.add(
        "output/parser.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="INFO",
        rotation="10 MB",
        retention="7 days"
    )
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>",
        level="INFO"
    )
