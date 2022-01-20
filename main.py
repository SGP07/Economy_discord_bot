import discord
from discord.ext import commands
import asyncio
import random
import json

print("Loading...")
bot = commands.Bot(command_prefix='!')
bot.remove_command('help')


emoji = '🔥'

@bot.event
async def on_ready():
    print('Bot ready')


#Giveaway command
@bot.command()
@commands.has_permissions(kick_members=True)
async def giveaway(ctx, hours : int, *,prize: str):
    embed = discord.Embed(title = 'Excalibur Quest', description = f'You can win {prize}, add {emoji} to participate', color = 0xe74c3c)
    embed.set_footer(text = f'The quest will end in {hours} hours')

    msg = await ctx.send(embed = embed)
    await msg.add_reaction(emoji)
    await asyncio.sleep(hours*3600)

    message = await ctx.channel.fetch_message(msg.id)

    users = await message.reactions[0].users().flatten()
    users.pop(users.index(bot.user))

    print("USERS LIST", users)
    winner = random.choice(users)

    await ctx.send(f' Congratulations {winner.mention} won {prize}')



@bot.command()
#Balance command
async def balance(ctx):
    await open_account(ctx.author)
    
    users = await get_bank_data()
    user = ctx.author

    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"]

    em = discord.Embed(title= f"{ctx.author.name}'s balance", color=discord.Color.blue())
    em.add_field(name ='Wallet balance', value=wallet_amt)
    em.add_field(name= 'Bank balance', value=bank_amt)
    await ctx.send(embed=em)



async def open_account(user):
    
    users = await get_bank_data()

    if str(user.id) in users :
        return False
    else :
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 0

    with open("mainbank.json", 'w') as f:
        json.dump(users, f)
    return True


async def get_bank_data():
    with open("mainbank.json", 'r') as f:
        users = json.load(f)
    
    return users
    

        


token = ''
bot.run(token)
