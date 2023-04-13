from discord.ext import commands
from discord import app_commands
import discord

from cogs.utils import mongo
from bot import Bot


class PollEmbed:
    def __init__(self, info: dict) -> None:
        self.info = info
        self.emojis = {
            '100': '<:100p:1096059911865114807>',
            '80': '<:80p:1096059910594236556>',
            '60': '<:60p:1096059908518056017>',
            '40': '<:40p:1096059906362191925>',
            '20': '<:20p:1096059903719776427>',
            '0': '<:0p:1096060707994353724>'
        }

    def get_progress_bar(self, length: int) -> str:
        progress_bar = []

        try:
            percentage = (length / self.total_votes) * 100
        except Exception:
            percentage = 0

        if percentage > 0:
            full_count = int(percentage / 10)
            for _ in range(full_count):
                progress_bar.append(self.emojis['100'])

            remainder = percentage % 10
            if remainder >= 8:
                progress_bar.append(self.emojis['80'])
            elif remainder >= 6:
                progress_bar.append(self.emojis['60'])
            elif remainder >= 4:
                progress_bar.append(self.emojis['40'])
            elif remainder >= 2:
                progress_bar.append(self.emojis['20'])

        progress_bar.append(self.emojis['0'] * (11 - len(progress_bar)))
        progress_bar.append(f'{round(percentage, 2)}%')

        return ''.join(progress_bar)

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

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)

        message = interaction.message
        user = interaction.user

        poll = mongo.Poll(message.id)
        poll_info = await poll.check()

        choices = poll_info['choices']

        voted = False
        for name, value in choices.items():
            if user.id in value:
                voted = True

        if voted:
            content = 'You have already voted'
            await interaction.followup.send(content)
            return

        vote_list = [n for n, v in choices.items()]
        vote = vote_list[int(self.label) - 1]

        user_list = choices[vote]

        user_list.append(user.id)
        await poll.update({f'choices.{vote}': user_list})

        poll_info = await poll.check()
        embed = PollEmbed(poll_info).build()
        await interaction.message.edit(embed=embed)

        content = 'Your vote has been received'
        await interaction.followup.send(content)


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
            message = await self.channel.send(embed=embed, view=view)

            poll_info['_id'] = message.id
            await mongo.Poll().create(poll_info)

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
