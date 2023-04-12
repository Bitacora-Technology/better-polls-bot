from discord.ext import commands
import discord
import logging

from cogs.utils import files
import config

description = """
This is a bot focused in creating polls.
"""

log = logging.getLogger(__name__)

initial_extensions = files.get_initial_extensions()


class Bot(commands.Bot):
    def __init__(self):
        allowed_mentions = discord.AllowedMentions.all()
        intents = discord.Intents.default()
        super().__init__(
            command_prefix=config.prefix,
            allowed_mentions=allowed_mentions,
            intents=intents,
            enable_debug_events=True,
        )

    async def setup_hook(self) -> None:
        self.bot_app_info = await self.application_info()

        for extension in initial_extensions:
            try:
                await self.load_extension(extension)
            except Exception:
                log.exception(f'Failed to load extension {extension}')
            else:
                log.info(f'Successfully loaded extension {extension}')

    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner

    async def on_ready(self) -> None:
        if not hasattr(self, 'uptime'):
            self.uptime = discord.utils.utcnow()

        log.info(f'Ready: {self.user} (ID: {self.user.id})')

    async def start(self) -> None:
        await super().start(config.token, reconnect=True)

    @property
    def config(self) -> config:
        return __import__('config')
