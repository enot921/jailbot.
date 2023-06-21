import json
import asyncio
from datetime import datetime, timedelta
import a2s
import pytz
import subprocess

import discord
from discord.ext import commands

from Cybernator import Paginator as pag

client = commands.Bot( command_prefix = ".." )



class server_info1():
    def __init__(self, config):
        self.config = config
        self.ip_address = config.get('server_ip')
        self.server_port = config.get('server_port')
        self.connect_link = 'steam://connect/' + str(self.ip_address) + ':' + str(self.server_port) + '/'
        print('Loaded server config: ' + self.ip_address + ':' + str(self.server_port))

    def get(self):     
        try:
            server_info = a2s.info((self.ip_address, self.server_port))
            self.player_list = a2s.players((self.ip_address, self.server_port))
            self.server_name = server_info.server_name
            self.curr_map = server_info.map_name.split('/')[-1]
            self.players = str(server_info.player_count) + '/' + str(server_info.max_players)
            self.ping = str(int((server_info.ping* 1000))) + 'ms'

        except:
            print('Server down :(')
            self.server_name = 'Server down :('
            self.curr_map = 'Unknown'
            self.players = '0'
            self.playerstats = 'Unknown'
            self.ping = '999ms'

class mm_player():
    def __init__(self, author):
        self.author = author
        self.init_time = datetime.now()
        self.time_diff = timedelta(seconds=0)


# Refresh server info every n seconds     
async def refresh_server_info():
    while True:
        server_info.get()

        # Find player names
        player_names = []
        for player in server_info.player_list:
            player_names.append(player.name)

        # Create embed with updated information
        emb = discord.Embed(title='Jail', color=0x6600ff)
        emb.add_field(name='Server Name', value=server_info.server_name, inline=False)
        emb.add_field(name='Current Map', value=server_info.curr_map, inline=False)
        emb.add_field(name='Players', value=server_info.players, inline=False)
        emb.add_field(name='Player Names', value= '\n'.join(player_names), inline=False)

        current_time = datetime.now(pytz.timezone('Europe/Moscow')).strftime("%H:%M:%S")
        emb.set_footer(text=f"Current Time (Moscow): {current_time}")


        # Send the updated embed to the channel
        channel = client.get_channel(1120756254046949456)  # Замени YOUR_CHANNEL_ID на ID канала, на котором бот будет отправлять информацию
        message = await channel.fetch_message(1120756323336851600)  # Замени MESSAGE_ID на ID сообщения, которое бот будет обновлять
        await message.edit(embed=emb)

        await asyncio.sleep(30)

# check for inactive matchmaking search status every n minutes, after this, remove player from list
async def check_mm_state():
    while True:
        for player in mm_player_list:
            player.time_diff = datetime.now() - player.init_time
            if int((player.time_diff.total_seconds() / 60) % 60) > config.get('mm_status_reset_minutes', 30):
                mm_player_list.remove(player)
        await asyncio.sleep(60)

def player_exists(iterable):
    for element in iterable:
        if element:
            return True
    return False

# Load the config file
with open("config1.json") as json_file1:
    config = json.load(json_file1)

server_info = server_info1(config)

mm_player_list = []


@client.event
async def on_ready():
    client.loop.create_task(refresh_server_info())
    client.loop.create_task(check_mm_state())
    print('Bot logged in as {0.user}'.format(client))

# !server - show server info embed
async def jail(ctx):
    server_info.get()

    # Find player names
    player_names = []
    for player in server_info.player_list:
        player_names.append(player.name)

    emb = discord.Embed(title='Jail', color=0x6600ff)
    emb.add_field(name='Server Name', value=server_info.server_name, inline=False)
    emb.add_field(name='Current Map', value=server_info.curr_map, inline=False)
    emb.add_field(name='Players', value=server_info.players, inline=False)
    emb.add_field(name='Player Names', value='\n'.join(player_names), inline=False)

    chunks = [player_names[i:i+10] for i in range(0, len(player_names), 10)]
    
    # Add multiple fields for player names
    for i, chunk in enumerate(chunks):
        emb.add_field(name=f'Player Names (Part {i+1})', value='\n'.join(chunk), inline=False)


    channel = client.get_channel(1116323719434993705)  # Замени YOUR_CHANNEL_ID на ID канала, на котором бот будет отправлять информацию
    message = await channel.send(embed=emb)

    # Сохранение ID сообщения, чтобы можно было его обновлять
    MESSAGE_ID = message.id

@client.command( aliases = ['cs', 'status'] )
@commands.is_owner()
async def changestatus( ctx, statustype:str = None, *, arg:str = None):
    if statustype is None: # Type Check
        await ctx.send( 'Please select status' )
    elif arg is None: # Arg Check
        await ctx.send( 'Write argument please' )
    else:
        if statustype.lower() == 'game': # Game
            await client.change_presence (activity=discord.Game( name = arg) )
        elif statustype.lower() == 'listen': # Listen
            await client.change_presence( activity=discord.Activity( type=discord.ActivityType.listening, name = arg) )
        elif statustype.lower() == 'watch': # Watch
            await client.change_presence( activity=discord.Activity( type=discord.ActivityType.watching, name = arg) )

@client.command()
@commands.cooldown(1, 5, commands.BucketType.member)
async def say(ctx, *, text):
	await ctx.channel.purge( limit = 1 )
	t = (text)
	emb = discord.Embed(description = f'{t}', colour = discord.Colour(0x6600ff))
	await ctx.send(embed = emb)

@client.command( pass_context = True )
@commands.has_permissions( manage_messages = True )
@commands.cooldown(1, 5, commands.BucketType.member)
async def clear ( ctx, amount = 100 ):
    await ctx.channel.purge( limit = amount )

def is_owner(ctx):
    return ctx.message.author.id == 926499487118139435

def reload_bot():
    subprocess.call(["python", "jailbot.py"])

@client.command()
@commands.check(is_owner)  # Проверка прав доступа
async def reload(ctx):
    await ctx.send("Перезапуск бота...")
    await client.close()  # Закрытие текущего соединения бота
    reload_bot()  # Вызов функции для перезапуска jailbot.py


# ID канала, в который бот будет отправлять сообщение о запуске
STARTUP_CHANNEL_ID = 1116323719434993705

@client.event
async def on_ready():
    # Получение объекта канала запуска по его ID
    startup_channel = client.get_channel(STARTUP_CHANNEL_ID)

    if startup_channel:
        # Отправка сообщения о запуске в канал
        await startup_channel.send("Бот успешно запущен!")
    else:
        print(f"Канал с ID {STARTUP_CHANNEL_ID} не найден.")


token = open( 'token.txt', 'r' ).readline()

client.run(token)
