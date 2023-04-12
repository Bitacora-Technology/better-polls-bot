from discord.ext import commands
import logging

from bot import Bot

log = logging.getLogger(__name__)


class Owner(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.delay = 10  # Seconds to wait to delete a message

    async def cog_check(self, ctx: commands.Context) -> bool:
        return await self.bot.is_owner(ctx.author)

    @commands.command(name='cogs', hidden=True)
    async def cogs(self, ctx: commands.Context) -> None:
        """Get the cog list"""
        cog_list = self.bot.cogs
        content = '\n'.join(cog_list)
        await ctx.send(content, delete_after=self.delay)
        await ctx.message.delete(delay=self.delay)

    @commands.command(name='update', hidden=True)
    async def update(self, ctx: commands.Context) -> None:
        """Reload all extensions"""
        cog_list = [c for c in self.bot.cogs]
        for cog in cog_list:
            extension = cog.lower()
            try:
                await self.bot.reload_extension(f'cogs.{extension}')
            except Exception as e:
                await ctx.send(
                    f'{e.__class__.__name__}: {e}',
                    delete_after=self.delay
                )
                log.exception(f'Failed to reload extension {extension}')
            else:
                await ctx.send(
                    f'Extension \'{extension}\' reloaded.',
                    delete_after=self.delay
                )
                log.info(f'Successfully reloaded extension {extension}')
        await ctx.message.delete(delay=self.delay)

    @commands.command(name='load', hidden=True)
    async def load(self, ctx: commands.Context, extension: str) -> None:
        """Loads a extension"""
        try:
            await self.bot.load_extension(f'cogs.{extension}')
        except commands.ExtensionError as e:
            await ctx.send(
                f'{e.__class__.__name__}: {e}',
                delete_after=self.delay
            )
            log.exception(f'Failed to load extension {extension}')
        else:
            await ctx.send(
                f'Extension \'{extension}\' loaded.',
                delete_after=self.delay
            )
            log.info(f'Successfully loaded extension {extension}')
        await ctx.message.delete(delay=self.delay)

    @commands.command(name='unload', hidden=True)
    async def unload(self, ctx: commands.Context, extension: str) -> None:
        """Unloads a extension"""
        try:
            await self.bot.unload_extension(f'cogs.{extension}')
        except commands.ExtensionError as e:
            await ctx.send(
                f'{e.__class__.__name__}: {e}',
                delete_after=self.delay
            )
            log.exception(f'Failed to unload extension {extension}')
        else:
            await ctx.send(
                f'Extension \'{extension}\' unloaded.',
                delete_after=self.delay
            )
            log.info(f'Successfully unloaded extension {extension}')
        await ctx.message.delete(delay=self.delay)

    @commands.command(name='reload', hidden=True)
    async def reload(self, ctx: commands.Context, extension: str) -> None:
        """Reloads a extension"""
        try:
            await self.bot.reload_extension(f'cogs.{extension}')
        except commands.ExtensionError as e:
            await ctx.send(
                f'{e.__class__.__name__}: {e}',
                delete_after=self.delay
            )
            log.exception(f'Failed to reload extension {extension}')
        else:
            await ctx.send(
                f'Extension \'{extension}\' reloaded.',
                delete_after=self.delay
            )
            log.info(f'Successfully reloaded extension {extension}')
        await ctx.message.delete(delay=self.delay)

    @commands.command(name='sync', hidden=True)
    async def sync(self, ctx: commands.Context, target: str) -> None:
        """Syncs the slash commands"""
        if target == 'global':
            guild = None
        elif target == 'guild':
            guild = ctx.guild
            self.bot.tree.copy_global_to(guild=guild)
        else:
            return await ctx.send(
                'You need to specify the sync target',
                delete_after=self.delay
            )

        commands_sync = await self.bot.tree.sync(guild=guild)
        await ctx.send(
            f'Successfully synced {len(commands_sync)} commands',
            delete_after=self.delay
        )
        log.info(f'Successfully synced {len(commands_sync)} commands')
        await ctx.message.delete(delay=self.delay)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Owner(bot))
