from dataclasses import dataclass
import json
import random
from datetime import datetime
import re

from dateutil import relativedelta
from interactions import *
from interactions.api.events import Component

import Data.capsule_characters as chars
from Localization.Localization import loc
from Utilities.DatabaseTypes import fetch_nikogotchi, fetch_user
from Utilities.ItemData import fetch_treasure
from database import Database
from Utilities.bot_icons import icon_loading
from Utilities.fancysend import *


@dataclass
class Nikogotchi:
    name: str
    immortal: bool
    rarity: int
    status: int
    emoji: int
    health: float
    hunger: float
    attention: float
    cleanliness: float
    pancake_dialogue: list[str]
    pet_dialogue: list[str]
    cleaned_dialogue: list[str]


class Command(Extension):

    async def get_nikogotchi(self, uid: int):
        nikogotchi_data = await fetch_nikogotchi(uid)

        if not nikogotchi_data.data:
            return None

        return Nikogotchi(**nikogotchi_data.data)

    async def save_nikogotchi(self, nikogotchi: Nikogotchi, uid: int):
        
        nikogotchi_data = await fetch_nikogotchi(uid)
        
        data = json.dumps(nikogotchi.__dict__,)

        await nikogotchi_data.update(data=data)
        
    async def delete_nikogotchi(self, uid: int):
        
        nikogotchi_data = await fetch_nikogotchi(uid)
        
        await nikogotchi_data.update(data='{}')

    def nikogotchi_buttons(self, owner_id: int):
        prefix = 'action_'
        suffix = f'_{owner_id}'

        return [
            Button(
                style=ButtonStyle.SUCCESS,
                label='Pet',
                custom_id=f'{prefix}pet{suffix}'
            ),
            Button(
                style=ButtonStyle.SUCCESS,
                label='Clean',
                custom_id=f'{prefix}clean{suffix}'
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                label='Find Treasure',
                custom_id=f'{prefix}findtreasure{suffix}'
            ),
            Button(
                style=ButtonStyle.GREY,
                emoji=PartialEmoji(id=1147696088250335303),
                custom_id=f'{prefix}refresh{suffix}'
            ),
            Button(
                style=ButtonStyle.DANGER,
                label='X',
                custom_id=f'{prefix}exit{suffix}'
            )
        ]

    async def get_nikogotchi_age(self, uid: int):
        nikogotchi_data = await fetch_nikogotchi(uid)

        return relativedelta.relativedelta(datetime.now(), nikogotchi_data.hatched)

    async def get_main_nikogotchi_embed(self, guild_id: int, age: relativedelta.relativedelta, dialogue: str,
                                        found_treasure: list[dict], n: Nikogotchi):
        progress_bar = {
            'empty': {
                'start': '<:thebeginningofthesong:1117957176724557824>',
                'middle': '<:themiddleofthesong:1117957179463438387>',
                'end': '<:theendofthesong:1117957159938961598>'
            },
            'filled': {
                'start': '<:thebeginningofthesong:1117957177987051530>',
                'middle': '<:themiddleofthesong:1117957181220864120>',
                'end': '<:theendofthesong:1117957174015041679>'
            }
        }

        progress_bar_length = 5

        health_value = round((n.health / 50) * progress_bar_length)
        hunger_value = round((n.hunger / 50) * progress_bar_length)
        attention_value = round((n.attention / 50) * progress_bar_length)
        cleanliness_value = round((n.cleanliness / 50) * progress_bar_length)

        health_progress_bar = ''
        hunger_progress_bar = ''
        attention_progress_bar = ''
        cleanliness_progress_bar = ''

        values = [health_value, hunger_value, attention_value, cleanliness_value]

        for index, value in enumerate(values):
            progress_bar_l = []
            for i in range(progress_bar_length):
                bar_section = 'middle'
                if i == 0:
                    bar_section = 'start'
                elif i == progress_bar_length - 1:
                    bar_section = 'end'

                if i < value:
                    bar_fill = progress_bar['filled'][bar_section]
                else:
                    bar_fill = progress_bar['empty'][bar_section]

                progress_bar_l.append(bar_fill)

            progress = ''.join(progress_bar_l)

            if index == 0:
                health_progress_bar = progress
            elif index == 1:
                hunger_progress_bar = progress
            elif index == 2:
                attention_progress_bar = progress
            elif index == 3:
                cleanliness_progress_bar = progress

        embed = Embed(
            title=n.name,
            color=0x8b00cc
        )

        nikogotchi_status = 'Your Nikogotchi seems to be doing okay.'

        if n.attention < 20:
            nikogotchi_status = f'🤨 {n.name} wants to be pet!'

        if n.cleanliness < 20:
            nikogotchi_status = f'🛀 {n.name} wants to be cleaned!'

        if n.hunger < 20:
            nikogotchi_status = f'🥞 {n.name} is feeling hungry...'

        if n.status == 3:
            nikogotchi_status = f'{n.name} is currently finding treasures for you!'

        treasure_found = ''

        if len(found_treasure) > 0:

            treasures = ''
            looked_over_treasures = []

            for treasure in found_treasure:

                if index in looked_over_treasures:
                    continue

                treasures += f'<:any:{treasure["image"]}> {treasure["name"]}\n'
                looked_over_treasures.append(index)

            treasure_found = f'''
            {n.name} found some treasures!\n\n{treasures}
            '''

        if n.health < 20:
            nikogotchi_status = f'🚨 {n.name} is at low health! Use Golden Pancakes to restore their health! 🚨'

        embed.set_author(name=nikogotchi_status)

        description = f'''
        {treasure_found}\n
        ❤️  {health_progress_bar} ({int(n.health)} / 50)\n\n🍴  {hunger_progress_bar} ({n.hunger} / 50)\n🫂  {attention_progress_bar} ({n.attention} / 50)\n🧽  {cleanliness_progress_bar} ({n.cleanliness} / 50)\n\n⏰  ***{age.years}*** *years*, ***{age.months}*** *months*, ***{age.days}*** *days*
        '''

        embed.description = description

        embed.set_image(url=f'https://cdn.discordapp.com/emojis/{n.emoji}.png')
        embed.set_footer(text=dialogue)

        return embed

    @slash_command(description="All things about your Nikogotchi!")
    async def nikogotchi(self, ctx: SlashContext):
        pass

    @nikogotchi.subcommand(sub_cmd_description="Check out your Nikogotchi!")
    async def check(self, ctx: SlashContext):

        uid = ctx.author.id

        nikogotchi_data = await fetch_nikogotchi(uid)

        if nikogotchi_data.data:
            msg = await fancy_message(ctx, f'[ Loading Nikogotchi... {icon_loading} ]')

        else:

            if not nikogotchi_data.nikogotchi_available:
                return await fancy_message(ctx, "[ You don't have a Nikogotchi! You can buy a capsule from the shop to unlock a random one! ]", ephemeral=True, color=0xff0000)
            
            viable_nikogotchi = []

            nikogotchi_list = chars.get_characters()

            for character in nikogotchi_list:
                if nikogotchi_data.rarity == character.rarity.value:
                    viable_nikogotchi.append(character)

            selected_nikogotchi: chars.Nikogotchi = random.choice(viable_nikogotchi)

            await nikogotchi_data.update(
                data = json.dumps({
                    'name': selected_nikogotchi.name,
                    'emoji': selected_nikogotchi.emoji,
                    'rarity': selected_nikogotchi.rarity.value,
                    'status': 2,
                    'immortal': False,
                    'health': 50,
                    'hunger': 50,
                    'attention': 50,
                    'cleanliness': 50,
                    'pancake_dialogue': selected_nikogotchi.pancake_dialogue,
                    'pet_dialogue': selected_nikogotchi.pet_dialogue,
                    'cleaned_dialogue': selected_nikogotchi.cleaned_dialogue,
                }),
                
                last_interacted = datetime.now(),
                hatched = datetime.now(),
                nikogotchi_available = False
            )

            nikogotchi = await self.get_nikogotchi(ctx.author.id)

            hatched_embed = Embed(
                title=f'You found {nikogotchi.name}!',
                color=0x8b00cc,
                description='Do you want to give them a new name?'
            )

            hatched_embed.set_image(url=f'https://cdn.discordapp.com/emojis/{nikogotchi.emoji}.png')

            buttons = [
                Button(style=ButtonStyle.GREEN, label='Yes', custom_id=f'yes {ctx.author.id}'),
                Button(style=ButtonStyle.RED, label='No', custom_id=f'no {ctx.author.id}')
            ]

            await ctx.send(embed=hatched_embed, components=buttons, ephemeral=True)

            button: Component = await self.bot.wait_for_component(components=buttons)
            button_ctx = button.ctx

            custom_id = button_ctx.custom_id

            if custom_id == f'yes {ctx.author.id}':
                modal = Modal(
                    ShortText(
                        custom_id='name',
                        value=nikogotchi.name,
                        label='Name'
                    ),
                    custom_id='name',
                    title='Give your Nikogotchi a name!',
                )

                await button_ctx.send_modal(modal)

                modal_ctx: ModalContext = await self.bot.wait_for_modal(modal)

                await modal_ctx.defer(edit_origin=True)

                nikogotchi.name = modal_ctx.kwargs['name']
            else:
                await button_ctx.defer(edit_origin=True)

            await self.save_nikogotchi(nikogotchi, ctx.author.id)

        await self.nikogotchi_interaction(ctx)

    r_nikogotchi_interaction = re.compile(r'action_(feed|pet|clean|findtreasure|refresh|callback|exit)_(\d+)$')
    @component_callback(r_nikogotchi_interaction)
    async def nikogotchi_interaction(self, ctx: ComponentContext or SlashContext):
        
        try:
            await ctx.defer(edit_origin=True)
            
            match = self.r_nikogotchi_interaction.match(ctx.custom_id)
        
            if not match:
                return
            
            custom_id = match.group(1)
            uid = int(match.group(2))
            
            if ctx.author.id != uid:
                return
        except:
            uid = ctx.author.id
            custom_id = 'refresh'
            
        if custom_id == 'exit':
            await ctx.delete()
            
        nikogotchi_data = await fetch_nikogotchi(uid)
        nikogotchi = await self.get_nikogotchi(uid)
        
        last_interacted = nikogotchi_data.last_interacted

        # Get the current datetime
        current_time = datetime.now()

        # Calculate the time difference in hours
        time_difference = (current_time - last_interacted).total_seconds() / 3600
        
        age = await self.get_nikogotchi_age(int(ctx.author.id))

        await nikogotchi_data.update(last_interacted=current_time)

        modifier = 1

        if nikogotchi.status == 3:
            modifier = 2.5
            
        random_stat_modifier = random.uniform(1, 1.50)

        nikogotchi.hunger = round(max(0, nikogotchi.hunger - time_difference * random_stat_modifier * modifier))
        
        random_stat_modifier = random.uniform(1, 1.50)
        
        nikogotchi.attention = round(max(0, nikogotchi.attention - time_difference * random_stat_modifier * modifier))
        
        random_stat_modifier = random.uniform(1, 1.50)
        
        nikogotchi.cleanliness = round(max(0, nikogotchi.cleanliness - time_difference * random_stat_modifier * modifier))

        if nikogotchi.immortal:
            nikogotchi.hunger = 9999
            nikogotchi.attention = 9999
            nikogotchi.cleanliness = 9999

        if nikogotchi.hunger <= 0 or nikogotchi.attention <= 0 or nikogotchi.cleanliness <= 0:
            nikogotchi.health = round(nikogotchi.health - time_difference * 0.5)

        if nikogotchi.health <= 0:
            embed = Embed(
                title=f'{nikogotchi.name} Passed away...',
                color=0x696969,
                description=f'''
                {nikogotchi.name} lived a full life of {age.years} years, {age.months} months, and {age.days} days.
                Hours since last taken care of: **{int(time_difference)} Hours**

                Nikogotchis rely on your love and attention, so keep trying to give them the best care possible!
                
                🪦
                '''
            )
            
            await self.delete_nikogotchi(uid)
            
            try:
                await ctx.edit_origin(embed=embed, components=[])
            except:
                await ctx.edit(embed=embed, components=[])
        
        if nikogotchi is None:
            return await ctx.edit_origin(
            embed=Embed(
                title='No Nikogotchi',
                description='Nikogotchi does not exist.'
            ),
            
            components=[
                Button(
                    emoji=PartialEmoji(id=1147696088250335303),
                    custom_id=f'action_refresh_{ctx.author.id}',
                    style=ButtonStyle.GREY)
            ]
        )

        if not custom_id == 'refresh':
            pass

        dialogue = '...'
        
        buttons = self.nikogotchi_buttons(uid)
        select = await self.feed_nikogotchi(ctx)

        if nikogotchi.status == 2:
            if custom_id == 'pet':
                # Adjust hunger, attention, and cleanliness
                attention_increase = 20
                nikogotchi.attention = min(50, nikogotchi.attention + attention_increase)

                dialogue = random.choice(nikogotchi.pet_dialogue)

            if custom_id == 'clean':
                cleanliness_increase = 30
                nikogotchi.cleanliness = min(50, nikogotchi.cleanliness + cleanliness_increase)

                dialogue = random.choice(nikogotchi.cleaned_dialogue)

            if custom_id == 'findtreasure':
                dialogue = 'Your Nikogotchi is now finding treasure! Just be aware that their stats will decrease faster than normal, so make sure to call them back when they\'re done!'
                nikogotchi.status = 3

        if custom_id == 'callback':
            nikogotchi.status = 2

        embed = await self.get_main_nikogotchi_embed(ctx.author.id, age, dialogue, [], nikogotchi)

        if not custom_id == 'feed':
            if nikogotchi.status == 2:
                buttons[0].disabled = False
                buttons[1].disabled = False
                buttons[2].disabled = False

                buttons[2].label = 'Find Treasure'
                buttons[2].custom_id = f'action_findtreasure_{uid}'
            else:
                select.disabled = True
                buttons[0].disabled = True
                buttons[1].disabled = True
                buttons[2].disabled = False

                buttons[2].label = 'Call Back'
                buttons[2].custom_id = f'action_callback_{uid}'

        embed.set_image(url=f'https://cdn.discordapp.com/emojis/{nikogotchi.emoji}.png')

        if nikogotchi.status == 3:
            
            user_data = await fetch_user(uid)
            treasures = await fetch_treasure('all')

            treasures_found = []

            for _ in range(round(time_difference)):
                value = random.randint(0, 5000)
                treasure = -1
                if value > 0:
                    treasure = random.choice(["journal", "bottle", "shirt"])
                if value > 3500:
                    treasure = random.choice(["amber", "pen", "card"])
                if value > 4500:
                    treasure = random.choice(["die", "sun", "clover"])

                treasure_loc = await loc(ctx.guild.id, 'Items', 'Treasures', treasure)
                
                treasures_found.append({'name': treasure_loc['name'], 'image': treasures[treasure]['image']})

                user_treasures = user_data.owned_treasures
                
                user_treasures[treasure] = user_treasures.get(treasure, 0) + 1
                await user_data.update(owned_treasures=user_treasures)

            select.disabled = True
            buttons[0].disabled = True
            buttons[1].disabled = True
            buttons[2].disabled = False

            buttons[2].label = 'Call Back'
            buttons[2].custom_id = f'action_callback_{uid}'
            
            embed = await self.get_main_nikogotchi_embed(ctx.author.id, age, dialogue, treasures_found, nikogotchi)
            embed.set_image(url='')

        await self.save_nikogotchi(nikogotchi, ctx.author.id)
        
        try:
            await ctx.edit_origin(embed=embed, components=[ActionRow(select), ActionRow(*buttons)])
        except:
            await ctx.edit(embed=embed, components=[ActionRow(select), ActionRow(*buttons)])

    async def feed_nikogotchi(self, ctx):
        food_options = []

        nikogotchi_data = await fetch_nikogotchi(ctx.author.id)
        
        nikogotchi = await self.get_nikogotchi(ctx.author.id)
        
        options = False

        if nikogotchi_data.glitched_pancakes > 0:
            food_options.append(
                StringSelectOption(
                    label=f'Feed ??? (x{nikogotchi_data.glitched_pancakes})',
                    emoji=PartialEmoji(1152356972423819436),
                    value=f'pancakeglitched_{ctx.author.id}'
                )
            )
            
            options = True

        if nikogotchi_data.golden_pancakes > 0:
            food_options.append(
                StringSelectOption(
                    label=f'Feed Golden Pancake (x{nikogotchi_data.golden_pancakes})',
                    emoji=PartialEmoji(1152330988022681821),
                    value=f'goldenpancake_{ctx.author.id}'
                )
            )
            
            options = True

        if nikogotchi_data.pancakes > 0:
            food_options.append(
                StringSelectOption(
                    label=f'Feed Pancake (x{nikogotchi_data.pancakes})',
                    emoji=PartialEmoji(1147281411854839829),
                    value=f'pancake_{ctx.author.id}'
                )
            )
            
            options = True
            
        placeholder = f'What do you want to feed {nikogotchi.name}?'
        cannot_feed = False
            
        if not options:
            food_options.append(
                StringSelectOption(
                    label=f'no food',
                    value='nofood'
                )
            )
            
            placeholder = f'No Food!'
            cannot_feed = True
            
        select = StringSelectMenu(
            *food_options,
            custom_id='feed_food',
            placeholder=placeholder,
            disabled=cannot_feed
        )

        return select

    @component_callback('feed_food')
    async def feed_food(self, ctx: ComponentContext):

        await ctx.defer(edit_origin=True)

        nikogotchi = await self.get_nikogotchi(ctx.author.id)
        data = ctx.values[0].split('_')
        
        value = data[0]
        uid = int(data[1])
        
        if ctx.author.id != uid:
            return

        nikogotchi_data = await fetch_nikogotchi(uid)
        
        pancakes = nikogotchi_data.pancakes
        golden_pancakes = nikogotchi_data.golden_pancakes
        glitched_pancakes = nikogotchi_data.glitched_pancakes

        hunger_increase = 0
        health_increase = 0

        if value == 'goldenpancake':
            if golden_pancakes <= 0:
                dialogue = 'You don\'t have any golden pancakes! Buy some from the shop to feed your Nikogotchi!'
            else:
                hunger_increase = 50
                health_increase = 25

                golden_pancakes -= 1
                dialogue = random.choice(nikogotchi.pancake_dialogue)
        elif value == 'pancakeglitched':
            if glitched_pancakes <= 0:
                dialogue = 'You don\'t have any ☐. You don\'t have any ☐. You don\'t have any ☐. You don\'t have any ☐. You don\'t have any ☐. You don\'t have any ☐. Do you?'
            else:
                hunger_increase = 9999
                health_increase = 9999
                
                glitched_pancakes -= 1
                nikogotchi.immortal = True
                dialogue = 'Your Nikogotchi is now Immortal.'
        else:
            if pancakes <= 0:
                dialogue = 'You don\'t have any pancakes! Buy some from the shop to feed your Nikogotchi!'
            else:
                hunger_increase = 25
                health_increase = 1
                
                pancakes -= 1
                dialogue = random.choice(nikogotchi.pancake_dialogue)
                
        await nikogotchi_data.update(
            pancakes = pancakes,
            golden_pancakes = golden_pancakes,
            glitched_pancakes = glitched_pancakes
        )

        nikogotchi.hunger = min(50, nikogotchi.hunger + hunger_increase)
        nikogotchi.health = min(50, nikogotchi.health + health_increase)

        await self.save_nikogotchi(nikogotchi, ctx.author.id)

        buttons = self.nikogotchi_buttons(ctx.author.id)
        select = await self.feed_nikogotchi(ctx)

        embed = await self.get_main_nikogotchi_embed(ctx.author.id, await self.get_nikogotchi_age(ctx.author.id),
                                                     dialogue, [], nikogotchi)

        await ctx.edit_origin(embed=embed, components=[ActionRow(select), ActionRow(*buttons)])

    @nikogotchi.subcommand(sub_cmd_description='Send away your Nikogotchi.')
    async def send_away(self, ctx: SlashContext):

        nikogotchi = await self.get_nikogotchi(ctx.author.id)

        if nikogotchi is None:
            return await fancy_message(ctx, "[ You don't have a Nikogotchi! ]", ephemeral=True, color=0xff0000)

        buttons = [
            Button(style=ButtonStyle.RED, label='Yes', custom_id=f'rehome {ctx.author.id}')
        ]

        embed = await fancy_embed(
            f'[ Are you sure you want to send away {nikogotchi.name} so that you can adopt a new one? ]')
        embed.set_footer(text='Dismiss this message if you change your mind.')

        await fancy_message(ctx,
                            f'[ Are you sure you want to send away {nikogotchi.name} so that you can adopt a new one? ]',
                            ephemeral=True, components=buttons)

        button = await self.bot.wait_for_component(components=buttons)
        button_ctx = button.ctx

        custom_id = button_ctx.custom_id

        if custom_id == f'rehome {ctx.author.id}':
            
            await self.delete_nikogotchi(ctx.author.id)

            embed = await fancy_embed(f'[ Successfully sent away {nikogotchi.name}. Enjoy your future Nikogotchi! ]')

            await ctx.edit(embed=embed, components=[])

    @nikogotchi.subcommand(sub_cmd_description='Rename your Nikogotchi.')
    @slash_option('name', description='Rename your Nikogotchi.', opt_type=OptionType.STRING, required=True)
    async def rename(self, ctx: SlashContext, name):

        nikogotchi = await self.get_nikogotchi(ctx.author.id)

        if nikogotchi is None:
            return await fancy_message(ctx, "[ You don't have a Nikogotchi! ]", ephemeral=True, color=0xff0000)

        old_name = nikogotchi.name
        nikogotchi.name = name

        await self.save_nikogotchi(nikogotchi, ctx.author.id)
        await fancy_message(ctx, f'[ Successfully renamed **{old_name}** to **{nikogotchi.name}**! ]', ephemeral=True)

    @nikogotchi.subcommand(sub_cmd_description='Show off your Nikogotchi, or view someone else\'s.!')
    @slash_option('user', description='The user to view.', opt_type=OptionType.USER, required=True)
    async def show(self, ctx: SlashContext, user: User):

        uid = user.id

        nikogotchi = await self.get_nikogotchi(uid)

        if nikogotchi is None:
            return await fancy_message(ctx, "[ This person doesn't seem to have a Nikogotchi! ]", ephemeral=True,
                                       color=0xff0000)

        age = await self.get_nikogotchi_age(uid)

        embed = Embed(
            title=f'{nikogotchi.name}',
            color=0x8b00cc,
        )

        embed.author = EmbedAuthor(
            name=f'Owned by {user.username}',
            icon_url=user.avatar_url
        )

        embed.description = f'''
        Age: {age.years} years, {age.months} months, and {age.days} days.
        
        Health: {int(nikogotchi.health)}/50
        '''

        embed.set_image(url=f'https://cdn.discordapp.com/emojis/{nikogotchi.emoji}.png?v=1')

        await ctx.send(embed=embed)

    @nikogotchi.subcommand(sub_cmd_description='Trade your Nikogotchi with someone else!')
    @slash_option('user', description='The user to trade with.', opt_type=OptionType.USER, required=True)
    async def trade(self, ctx: SlashContext, user: User):

        nikogotchi_one = await self.get_nikogotchi(ctx.author.id)
        nikogotchi_two = await self.get_nikogotchi(user.id)
        
        if nikogotchi_one is None:
            return await fancy_message(ctx, "[ You don't have a Nikogotchi! ]", ephemeral=True, color=0xff0000)
        if nikogotchi_two is None:
            return await fancy_message(ctx, "[ This person doesn't have a Nikogotchi! ]", ephemeral=True,
                                       color=0xff0000)

        await fancy_message(ctx, f'[ Sent {user.mention} a trade offer! Waiting on their response... {icon_loading} ]',
                            ephemeral=True)

        uid = user.id

        embed = await fancy_embed(f'''
        ### **{ctx.author.mention}** wants to trade their Nikogotchi with you!
        
        **Name:** {nikogotchi_one.name}
        **Health:** {nikogotchi_one.health}/50
        
        Do you want to trade <:dfd:{nikogotchi_two.emoji}> **{nikogotchi_two.name}** with them?
        ''')

        embed.set_image(url=f'https://cdn.discordapp.com/emojis/{nikogotchi_one.emoji}.png?v=1')

        buttons = [
            Button(style=ButtonStyle.SUCCESS, label='Trade', custom_id=f'trade {ctx.author.id} {uid}'),
            Button(style=ButtonStyle.DANGER, label='Decline', custom_id=f'decline {ctx.author.id} {uid}')
        ]

        await user.send(embed=embed, components=buttons)

        button = await self.bot.wait_for_component(components=buttons)
        button_ctx = button.ctx

        await button_ctx.defer(edit_origin=True)

        custom_id = button_ctx.custom_id

        if custom_id == f'trade {ctx.author.id} {uid}':
            await self.save_nikogotchi(nikogotchi_two, ctx.author.id)
            await self.save_nikogotchi(nikogotchi_one, uid)

            embed_two = await fancy_embed(
                f'[ Successfully traded with {user.mention}! Say hello to **{nikogotchi_two.name}**! ]')
            embed_two.set_image(url=f'https://cdn.discordapp.com/emojis/{nikogotchi_two.emoji}.png?v=1')

            embed_one = await fancy_embed(
                f'[ Successfully traded with **{ctx.author.username}**! Say hello to **{nikogotchi_one.name}**! ]')
            embed_one.set_image(url=f'https://cdn.discordapp.com/emojis/{nikogotchi_one.emoji}.png?v=1')

            await button_ctx.edit_origin(embed=embed_one, components=[])
            await ctx.edit(embed=embed_two)
        else:
            embed = await fancy_embed(f'[ {user.mention} declined your trade offer. ]')
            await ctx.edit(embed=embed)

            embed = await fancy_embed(f'[ Successfully declined trade offer. ]')

            await button_ctx.edit_origin(embed=embed, components=[])

    @slash_command(description='View the treasure you currently have, or someone else\'s!')
    @slash_option('user', description='The user to view.', opt_type=OptionType.USER, required=True)
    async def treasure(self, ctx: SlashContext, user: User):
        embed = Embed(
            title=f'{user.username}\'s Treasure',
            color=0x8b00cc,
        )

        all_treasures = await fetch_treasure('all')
        treasure_string = ''
        
        user_data = await fetch_user(user.id)
        owned_treasures = user_data.owned_treasures

        for treasure_nid, item in all_treasures.items():
            
            treasure_loc = await loc(ctx.guild_id, 'Items', 'Treasures')
            
            name = treasure_loc[treasure_nid]['name']
            
            try:
                treasure_string += f'<:emoji:{item["image"]}> {name}: **{owned_treasures[treasure_nid]}x**\n\n'
            except:
                treasure_string += f'<:emoji:{item["image"]}> {name}: **0**\n\n'

        embed.description = f'''
        Here is {user.mention}'s treasure!
        
        {treasure_string}
        Earn more treasure through Nikogotchis or purchasing them from the shop!
        '''

        await ctx.send(embed=embed)
