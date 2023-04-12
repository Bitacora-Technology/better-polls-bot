from discord.ext import commands
from discord import app_commands
import discord

from bot import Bot


def poll_embed(info: dict) -> discord.Embed:
    embed = discord.Embed(title=info['question'], color=0)
    for choice in info['choices']:
        embed.add_field(name=choice, value='Test', inline=False)
    return embed


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
            'channel': self.channel,
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

        embed = poll_embed(poll_info)
        await interaction.response.send_message(embed=embed, ephemeral=True)


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
