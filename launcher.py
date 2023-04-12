import logging
import asyncio
import discord
import contextlib

from bot import Bot

from setproctitle import setproctitle
from logging.handlers import RotatingFileHandler


setproctitle('better-polls-bot')


class RemoveNoise(logging.Filter):
    def __init__(self):
        super().__init__(name='discord.state')

    def filter(self, record: logging.LogRecord) -> bool:
        if (
            record.levelname == 'WARNING' and
            'referencing an unknown' in record.msg
        ):
            return False
        return True


@contextlib.contextmanager
def setup_logging():
    log = logging.getLogger()

    try:
        discord.utils.setup_logging()
        max_bytes = 32 * 1024 * 1024  # 32 MiB
        logging.getLogger('discord').setLevel(logging.INFO)
        logging.getLogger('discord.http').setLevel(logging.WARNING)
        logging.getLogger('discord.state').addFilter(RemoveNoise())

        log.setLevel(logging.INFO)
        handler = RotatingFileHandler(
            filename='discord.log',
            encoding='utf-8',
            mode='w',
            maxBytes=max_bytes,
            backupCount=5
        )
        dt_fmt = '%Y-%m-%d %H:%M:%S'
        fmt = logging.Formatter(
            fmt='[{asctime}] [{levelname:<7}] {name}: {message}',
            datefmt=dt_fmt,
            style='{'
        )
        handler.setFormatter(fmt)
        log.addHandler(handler)

        yield
    finally:
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)


async def run_bot() -> None:
    async with Bot() as bot:
        await bot.start()


def main() -> None:
    with setup_logging():
        asyncio.run(run_bot())


if __name__ == '__main__':
    main()
