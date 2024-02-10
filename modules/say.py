import io
from interactions import *
import json
from uuid import uuid4
import os
from Utilities.fancysend import fancy_message, fancy_embed
from Utilities.bot_icons import icon_loading
from PIL import Image, ImageDraw, ImageFont
import textwrap
import aiohttp
import aiofiles


class TextBoxGeneration(Extension):

    @staticmethod
    async def generate_welcome_message(guild: Guild, user: Member):

        uuid = str(uuid4())

        message = f'Hello, {user.username}! Welcome to {guild.name}! We hope you enjoy your stay.'

        await TextBoxGeneration.generate_dialogue(message,
                                                  'https://cdn.discordapp.com/emojis/1023573458296246333.webp?size=128&quality=lossless',
                                                  uuid)

        file = File(file=f'Images/{uuid}.png', description=message)
        await guild.system_channel.send(user.mention, files=file)
        os.remove(f'Images/{uuid}.png')

    @staticmethod
    async def generate_dialogue(l1, image_url, uuid):
        img = Image.open("Images/Dialogue Generation/niko-background.png")  # Opening Images for both the background...

        icon = await TextBoxGeneration.GetImage(image_url=image_url) # ...And the niko face selected in the command
        icon = icon.resize((96, 96)) # This doesn't need to be done for the OneShot characters, but for avatars and the elusive eyebrow raise.

        fnt = ImageFont.truetype("font/TerminusTTF-Bold.ttf", 20)  # Font

        d = ImageDraw.Draw(img)  # Textbox background
        # The X and Y starting positions
        text_x = 20
        text_y = 17
        for line in textwrap.wrap(l1, width=46):  # Text Wrap Length
            d.text((text_x, text_y), line, font=fnt, fill=(255, 255, 255))  # Text and Text Wrapping
            text_y += 25  # Width of line breaks, by y value

        img.paste(icon, (496, 16), icon.convert('RGBA'))  # The face sprite to use on the textbox

        img.save(f'Images/{uuid}.png')

        return Image.open(f'Images/{uuid}.png')

    async def generate_dialogue_animated(self, text, image_url, uuid):

        img = Image.open("Images/Dialogue Generation/niko-background.png")  # Opening Images for both the background...

        icon = await TextBoxGeneration.GetImage(image_url=image_url)  # ...And the niko face selected in the command
        icon = icon.resize((96, 96)) # This doesn't need to be done for the OneShot characters, but for avatars and the elusive eyebrow raise.

        fnt = ImageFont.truetype("font/TerminusTTF-Bold.ttf", 20)  # Font

        images = []
        cumulative_text = ''

        final_text = '\n'.join(textwrap.wrap(text, width=46))
        
        def append_frame():
            text_x = 20
            text_y = 17
            d = ImageDraw.Draw(img)

            d.text((text_x, text_y), cumulative_text, font=fnt, fill=(255, 255, 255))  # Text and Text Wrapping
            text_y += 25  # Width of line breaks, by y value

            img.paste(icon, (496, 16), icon.convert('RGBA'))  # The face sprite to use on the textbox
            return img.copy()

        for char in final_text:
            cumulative_text += char
            
            frame_time = 0
            
            if char in ['. ', '! ', '? ']:
                frame_time = 10
            
            if char in ['.', '!', '?']:
                frame_time = 5
            
            img = append_frame()
            
            if frame_time > 0:
                for _ in range(frame_time):
                    images.append(img)
            else:
                images.append(img)         
                
                
        img.save(f'Images/{uuid}.gif', save_all=True, append_images=images, optimize=False, duration=40)

    @staticmethod
    async def GetImage(image_url):
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    file = io.BytesIO(await resp.read())
                    return Image.open(file)

    def emojis(self):
        json_data = {}

        with open('Data/characters.json', 'r') as f:
            json_data = json.loads(f.read())

        characters = json_data['characters']

        awesome = []

        for character in characters:
            name = character['name']
            id_ = character['faces'][0]['id']

            awesome.append(
                StringSelectOption(
                    label=name,
                    emoji=PartialEmoji(id=id_),
                    value=name
                )
            )

        return StringSelectMenu(
            *awesome,
            placeholder="Select a character!",
            custom_id="menu_component_char"
        )

    @slash_command(description='Generate a OneShot textbox!')
    @slash_option(description='What you want the character to say.', max_length=180, name='text',
                  opt_type=OptionType.STRING, required=True)
    @slash_option(description='Do you want this to be animated? (Will take a lot longer to generate.)', name='animated',
                  opt_type=OptionType.BOOLEAN, required=True)
    async def textbox(self, ctx: SlashContext, text: str, animated: bool):

        channel = ctx.channel

        text__ = self.emojis()

        await fancy_message(ctx, f"[ <@{ctx.user.id}>, select a character. ]", ephemeral=True, components=text__)

        char = await self.client.wait_for_component(components=text__)

        char_ctx = char.ctx

        await char_ctx.defer(edit_origin=True)

        val_char = char_ctx.values[0]

        options = []

        with open('Data/characters.json', 'r') as f:
            json_data = json.loads(f.read())

        characters = json_data['characters']

        char = None

        for character in characters:
            if character['name'] == val_char:
                char = character
                break

        for face in char['faces']:
            
            if type(face['id']) == str:
                emoji = face['id']
            else:
                emoji = PartialEmoji(id=face['id'])
            
            options.append(
                StringSelectOption(
                    label=face['face_name'],
                    value=face['id'],
                    emoji=emoji
                )
            )

        select_menu = StringSelectMenu(
            *options,
            custom_id='Custom_Select_Menu_For b ' + str(ctx.guild_id),
            disabled=False,
            placeholder='Select a face!'
        )

        embed = await fancy_embed(f"[ <@{ctx.user.id}>, select a face. ]")

        await ctx.edit(embed=embed, components=select_menu)

        char_ctx = await self.client.wait_for_component(components=select_menu)

        await char_ctx.ctx.defer(edit_origin=True)

        value = char_ctx.ctx.values[0]

        await ctx.delete()

        msg = await fancy_message(channel, "[ Generating Image... <a:loading:1026539890382483576> ]")

        uuid = uuid4()

        uuid = str(uuid)

        if value == '964952736460312576':
            emoji = ctx.author.avatar.url
        else:
            emoji = f'https://cdn.discordapp.com/emojis/{value}.png'

        if not animated:
            await TextBoxGeneration.generate_dialogue(text, emoji, uuid)
            await msg.delete()
            file = File(file=f'Images/{uuid}.png', description=text)
            await channel.send(f"[ Generated by <@{int(ctx.user.id)}>. ]", files=file)
            os.remove(f'Images/{uuid}.png')
        else:
            await self.generate_dialogue_animated(text, emoji, uuid)
            await msg.delete()
            file = File(file=f'Images/{uuid}.gif', description=text)
            await channel.send(f"[ Generated by <@{int(ctx.user.id)}>. ]", files=file)
            os.remove(f'Images/{uuid}.gif')
