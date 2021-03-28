import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import pymongo
from pymongo import MongoClient

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()
bot = commands.Bot(command_prefix='!!')

# @client.event
# async def on_ready():
#     print(f'{client.user} has connected to discord')

@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write('Unhandled message: {args[0]}\n')
        else:
            raise

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to discord!')




bot.run(TOKEN)