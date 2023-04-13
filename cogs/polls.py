from discord.ext import commands
from discord import app_commands
import discord

from bot import Bot


class PollEmbed:
    def __init__(self, info: dict) -> None:
        self.info = info

    def get_progress_bar(self, length: int) -> str:
        progress_bar = ''

        try:
            percentage = round((length / self.total_votes) * 100, 2)
        except Exception:
            percentage = 0

        if percentage > 0:
            progress_bar += '`'
            progress_bar += ' ' * int(percentage)
            progress_bar += '` '

        progress_bar += f'{percentage}%'

        return progress_bar

    def add_embed_field(self, name: str, value: list) -> None:
        choice_name = f'{self.count}. {name}'
        progress_bar = self.get_progress_bar(len(value))
        self.embed.add_field(
            name=choice_name, value=progress_bar, inline=False
        )

    def calculate_total_votes(self) -> None:
        self.total_votes = 0
        for name, value in self.info['choices'].items():
            self.total_votes += len(value)

    def build(self) -> discord.Embed:
        self.calculate_total_votes()

        self.embed = discord.Embed(
            title=self.info['question'],
            description=f'Total votes: {self.total_votes}',
            color=0
        )

        self.count = 1
        for name, value in self.info['choices'].items():
            self.add_embed_field(name, value)
            self.count += 1

        return self.embed


class VotePollButton(discord.ui.Button):
    def __init__(self, count: int) -> None:
        super().__init__(label=count, style=discord.ButtonStyle.primary)


class VotePollView(discord.ui.View):
    def __init__(self, choices: list) -> Bot:
        super().__init__(timeout=None)
        for count in range(1, len(choices) + 1):
            self.add_item(VotePollButton(count))


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

        choices = poll_info['choices']

        if len(choices) < 2:
            content = 'Not enough options'
            embed = None
        elif len(choices) > 25:
            content = 'Too many options'
            embed = None
        else:
            content = f'Poll sent to {self.channel.mention}'
            embed = PollEmbed(poll_info).build()

        if embed:
            view = VotePollView(choices)
            await self.channel.send(embed=embed, view=view)
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
