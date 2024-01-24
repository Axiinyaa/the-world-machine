from interactions import *
from Utilities.fancysend import fancy_message
from database import Database as db
import Utilities.badge_manager as badge_manager
import Utilities.bot_icons as icons

from datetime import datetime, timedelta

import random


class Command(Extension):


    current_limit = 0

    wool_finds = [
        'You sheared some sheep for wool.',
        'You dug around a trashcan and found some wool.',
        'You tore up your old bedsheets for some wool.',
        'You summoned the devil and asked for some wool.',
        'You won a videogame tournament and won wool.',
        'You got the world record speedrun for a game and won wool.',
        "You robbed a wool store and got caught by the cops, now you're serving time for wool.",
        "You sold your soul for wool, now you're cursed forever.",
        "You stole your neighbor's wool.",
        "You vandalized a museum for wool. You're a menace to society.",
        "You extorted a small business for wool. You should be ashamed.",
        "You traded in a novelty t-shirt and got wool."
    ]

    @slash_command(description='All things to do with wool.')
    async def wool(self, ctx: SlashContext):
        pass

    @wool.subcommand(sub_cmd_description='Check your balance.')
    @slash_option(description='Check someone else\'s balance...', name='user', opt_type=OptionType.USER)
    async def balance(self, ctx: SlashContext, user: User = None):

        if user is None:
            user = ctx.user

        wool: int = await db.fetch('user_data', 'wool', user.id)

        if user is None:
            await fancy_message(ctx, f'[ You have <:wool:1044668364422918176>**{wool}**. ]')

        else:
            await fancy_message(ctx, f'[ **{user.username}** has <:wool:1044668364422918176>**{wool}**. ]')

    @wool.subcommand(sub_cmd_description='Find out who has the most wool.')
    async def leaderboard(self, ctx: SlashContext):

        msg = await ctx.send(
            embeds=Embed(description=f'[ Getting Entries... {icons.loading()} ]', color=0x8b00cc))

        lb: tuple[int, int] = await db.get_leaderboard('wool')

        usernames: str = ''
        value = ''

        msg = await msg.edit(
            embeds=Embed(description=f'[ Fetching Usernames... {icons.loading()} ]', color=0x8b00cc))

        index = 1
        for entry in lb:
            user = await self.bot.fetch_user(entry[0])
            wool = entry[1]
            usernames += f'{index}. **{user.username}** - {icons.wool()} **{wool}**\n'
            index += 1

        embed = Embed(
            title='Wool Leaderboard',
            color=0x8b00cc
        )

        embed.add_field(name='Users', value=usernames, inline=True)

        await msg.edit(embeds=embed)

    @wool.subcommand(sub_cmd_description='Grab your daily wool.')
    async def daily(self, ctx: SlashContext):

        get_time = await db.fetch('user_data', 'daily_wool_timestamp', ctx.user.id)

        if get_time is None:
            last_reset_time = datetime(2000, 1, 1, 0, 0, 0)
        else:
            last_reset_time = datetime.strptime(get_time, '%Y-%m-%d %H:%M:%S')

        now = datetime.now()

        if now < last_reset_time:
            time_unix = last_reset_time.timestamp()
            return await fancy_message(ctx, f"[ You've already collected your wool in the past 24 hours. You can collect it again <t:{int(time_unix)}:R>. ]", ephemeral=True, color=0xFF0000)

        # reset the limit if it is a new day
        if now >= last_reset_time:
            reset_time = datetime.combine(now.date(), now.time()) + timedelta(days=1)
            await db.update('user_data', 'daily_wool_timestamp', ctx.user.id, reset_time.strftime("%Y-%m-%d %H:%M:%S"))

        random.shuffle(self.wool_finds)

        response = self.wool_finds[0]

        amount: int
        message: str

        if random.randint(0, 100) == 2:
            amount = 50_000
            message = f'## Jackpot! 🎉You found <:wool:1044668364422918176>**{amount}**!'
        else:
            amount = random.randint(100, 300)
            message = f'You found <:wool:1044668364422918176>**{amount}**.'

        wool: int = await db.fetch('user_data', 'wool', ctx.user.id)
        await db.update('user_data', 'wool', ctx.user.id, wool + amount)
        await badge_manager.check_wool_value(ctx, wool + amount)

        await fancy_message(ctx, f'*{response}*\n{message}')
