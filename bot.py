import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import pymongo
from pymongo import MongoClient
from utils.panda import *
import random

#discord setup
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!!'), intents=intents)


#mongo
pw = os.getenv('MONGODB_PASSWORD')
cluster = pymongo.MongoClient("mongodb+srv://Chris:" + str(pw) + "@yupbot.jim1g.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster["YupBot"]
collection = db["UserData"]

#panda setup
PANDA = PandaAPI()

@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write('Unhandled message: {args[0]}\n')
        else:
            f.write('Unknown Error')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to discord!')

# commands
@bot.command(name='register', help='For first time users, let\'s set you up with a bank account so you can gamble it all away!')
async def register(ctx):
    __id = ctx.author.id
    __mention = ctx.author.mention
    __name = ctx.author.name
    is_registered = collection.find_one({"_id": __id})
    if is_registered:
        await ctx.channel.send('You are already registered ' + str(__mention))
        return
    # else
    post = {"_id": __id, "balance": 0, "name":__name}
    collection.insert_one(post)
    await ctx.channel.send('Congratulations ' + __mention + ', you have been registered!')

@bot.command(name='balance', help='Check your current balance. Can also check others\' balances, usage: \"!!balance @[user]')
async def check_balance(ctx, *args):
    if len(args) == 0:
        __id = ctx.author.id
        member = ctx.author
    else:
        mention = args[0]
        mention = mention.replace("<","")
        mention = mention.replace(">","")
        mention = mention.replace("@","")
        mention = mention.replace("!","")
        __id = int(mention)
        member = ctx.guild.get_member(__id)
        if member == None:
            await ctx.channel.send("User not found, did you make a typo?")
            return
    query = {"_id":__id}
    doc = collection.find_one(query)
    if doc:
        balance = doc["balance"]
        message = "The user " + str(member.mention) + " currently has a balance of $" + str(balance)
    else:
        message = "The user " + str(member.mention) + " is not registered yet. Register using: \"!!register\""
    await ctx.channel.send(message)

@bot.command(name='test', help='For debugging purposes')
async def test(ctx, *args):
    if len(args) > 0:
        arg1 = args[0]
        if len(args) > 1:
            arg2 = args[1]
            if arg1 == "setbalance":
                query = {"_id": ctx.author.id}
                update = {"$set": {"balance": arg2}}
                collection.update_one(query, update)
    author = ctx.author
    member = ctx.guild.get_member(author.id)
    print("id:", author.id)
    print("member:", member)

@bot.command(name='gamble', help='This is what you came here for.\nUsage: \"!!gamble [amount] ...\"')
async def gamble(ctx, amount, *args):
    message = "error"
    author = ctx.author
    amount = int(amount)
    query = {"_id": author.id}
    doc = collection.find_one(query)
    if doc:
        balance = int(doc["balance"])
        if balance < amount:
            message = str(author.mention) + " You lack the critical funds! Get a job!"
        else:
            if len(args) == 0: # coin flip
                odds = 0.5
                rand = random.random()
                if rand > odds: # win
                    message = str(author.mention) + " Congratulations! You won $" + str(amount)
                    update = {"$set": {"balance": balance + amount}}
                    collection.update_one(query, update)
                else:   #lose
                    message = str(author.mention) + " Unlucky, better luck next time, you lost all $" + str(amount)
                    update = {"$set": {"balance": balance - amount}}
                    collection.update_one(query, update)
            else:
                command = args[0]
                if command == "dice":
                    if len(args) > 2:
                        sides = int(args[1])
                        prediction = int(args[2])
                        outcome = random.randint(1,sides)
                        if prediction > sides:
                            message = "Thats not how dice work...\n!!gamble [amount] dice [number of sides] [prediction]"
                        else:
                            if prediction == outcome:   # win
                                winnings = amount * sides
                                message = "Outcome was " + str(outcome) + ", you guessed " + str(prediction) +"\n" + str(author.mention) + " Congratulations! You won $" + str(winnings - amount)
                                update = {"$set": {"balance": balance - amount + winnings}}
                                collection.update_one(query, update)
                            else:   # loss
                                message = "Outcome was " + str(outcome) + ", you guessed " + str(prediction) +"\n" + str(author.mention) + " Never lucky! You lost $" + str(amount)
                                update = {"$set": {"balance": balance - amount}}
                                collection.update_one(query, update)
                    else:
                        message = "!!gamble [amount] dice [number of sides] [prediction]"
                else:
                    message = "Invalid command"
    else:
        message = str(author.mention) + " You are not registered yet. Register using: \"!!register\""
    await ctx.channel.send(message)

@bot.command(name='kait', help='You know what this does...')
async def kait(ctx):
    if random.random() > 0.5:
        await ctx.channel.send("kait: I'll be back")
    else:
        await ctx.channel.send("kait: Hello???")
    
@bot.command(name='lol', help='Many League of Legends commands')
async def test(ctx, command, *args):
    embed = None
   
    if command == 'icon':    # url to champion icon
        if len(args) == 0:
            message = "Usage: \"!!lol icon [champion_name]\""
        else:
            __name = args[0]
            url = PANDA.get_champ_portrait(__name)
            if url:
                message = url
            else:
                message = "Error, maybe you made a typo"
    elif command == 'schedule': # upcoming week's schedule
        schedule_string = PANDA.get_schedule_message(str(PANDA.LCS_ID))
        embed = discord.Embed(
            title="This week's schedule",
            url="https://lolesports.com/schedule" 
        )
        embed.add_field(name="Matches:", value = schedule_string)
        if schedule_string:
            message = None
        else:
            message = "Error, something went wrong"
    else:   # does not match any commands
        message = "Invalid command"

    await ctx.channel.send(message, embed=embed)


bot.run(TOKEN)