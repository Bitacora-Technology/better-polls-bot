from discord.ext import commands
from discord import app_commands
import discord

from bot import Bot


class PollEmbed:
    def __init__(self, info: dict) -> None:
        self.info = info

    def build(self) -> discord.Embed:
        self.embed = discord.Embed(title=self.info['question'], color=0)
        return self.embed


class CreatePollModal(discord.ui.Modal):
    def __init__(self, channel: discord.TextChannel) -> None:
        super().__init__(title='Create a poll', timeout=None)
        self.channel = channel

    question = discord.ui.TextInput(label='Question', max_length=256)

    placeholder = (
        'Start each option with a `-`\n'
        '-Option 1\n'
        '-Option 2'
    )
    choices = discord.ui.TextInput(
        label='Choices', style=discord.TextStyle.long, placeholder=placeholder
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        poll_info = {
            'question': self.question.value,
            'choices': {},
        }

        for choice in self.choices.value.split('\n'):
            if not choice.startswith('-'):
                continue

            name = choice[1:]
            if name in poll_info['choices']:
                continue

            poll_info['choices'][name] = []

        if len(poll_info['choices']) < 2:
            content = 'Not enough options'
            embed = None
        elif len(poll_info['choices']) > 25:
            content = 'Too many options'
            embed = None
        else:
            content = f'Poll sent to {self.channel.mention}'
            embed = PollEmbed(poll_info).build()

        if embed:
            await self.channel.send(embed=embed)
        await interaction.response.send_message(content, ephemeral=True)


class Polls(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @app_commands.command()
    async def create(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
    ) -> None:
        """Create a poll"""
        modal = CreatePollModal(channel)
        await interaction.response.send_modal(modal)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Polls(bot))
