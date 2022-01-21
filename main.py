import discord
from discord.ext import commands
import asyncio
import random
import json
import os
from datetime import timedelta

os.chdir('Z:\\Documents\\Files\\Dev\\bushicro\\bushicro')

print("Loading...")
bot = commands.Bot(command_prefix='!', case_insensitive=True)
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

    #sending message
    msg = await ctx.send(embed = embed)
    await msg.add_reaction(emoji)
    await asyncio.sleep(hours*3600)

    message = await ctx.channel.fetch_message(msg.id)
    #getting the users 
    users = await message.reactions[0].users().flatten()
    users.pop(users.index(bot.user))

    #Randomly choosing a winner
    winner = random.choice(users)

    #sending winner as a message
    await ctx.send(f' Congratulations {winner.mention} won {prize}')



#Balance command
@bot.command()
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

#beg command
@bot.command()
@commands.cooldown(1, 1800, commands.BucketType.user) #use command once every 30min (1800sec)
async def beg(ctx):
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author

    #generating random earnings
    earnings = random.randrange(101)
    em = discord.Embed(title=f"Donation !",description=f'Someone gave you {earnings} coins !!', color=discord.Color.green())
    await ctx.send(embed=em)
    
    
    #storing earnings in the wallet
    users[str(user.id)]["wallet"] += earnings
    
    #update bankdata
    with open("mainbank.json", 'w') as f:
        json.dump(users, f)

#withdraw command
@bot.command()
async def withdraw(ctx, amount=None):
    await open_account(ctx.author)

    if amount == None:
        em = discord.Embed(title=f" ❌ Error!",description="Please enter the amount", color=0xe74c3c)
        await ctx.send(embed=em)
        return

    bal = await update_bank(ctx.author)

    if amount == 'all':
        amount = bal[1]
    if int(amount) > bal[1]:
        em = discord.Embed(title=f" ❌ Error!",description="You don't have enough money", color=0xe74c3c)
        await ctx.send(embed=em)
        return
    if int(amount) < 0:
        em = discord.Embed(title=f" ❌ Error!",description="The amount must be positive", color=0xe74c3c)
        await ctx.send(embed=em)
        return
    amount = int(amount)
    
    await update_bank(ctx.author, amount) #adding the ammount to the wallet
    await update_bank(ctx.author, -1*amount, 'bank') #substracting the amount from the bank
    #sending the message
    em = discord.Embed(title=f"Withdrawal",description=f'You withdrew {amount} coins', color=discord.Color.green())
    await ctx.send(embed=em)
    

#deposit command
@bot.command()
async def deposit(ctx, amount=None):
    await open_account(ctx.author)

    if amount == None:
        em = discord.Embed(title=f" ❌ Error!",description="Please enter the amount", color=0xe74c3c)
        await ctx.send(embed=em)
        return

    bal = await update_bank(ctx.author)

    if amount == 'all':
        amount = bal[0]
    if int(amount) > bal[0]:
        em = discord.Embed(title="❌ Error!",description="You don't have enough money", color=0xe74c3c)
        await ctx.send(embed=em)
        return
    if int(amount) < 0:
        em = discord.Embed(title="❌ Error!",description="The amount must be positive", color=0xe74c3c)
        await ctx.send(embed=em)
        return

    amount = int(amount)
    
    await update_bank(ctx.author, -1*amount) #substracting the ammount from the wallet
    await update_bank(ctx.author, amount, 'bank') #adding the amount to the bank
    #sending the message
    em = discord.Embed(title="Deposit",description=f"You deposited {amount} coins", color=discord.Color.green())
    await ctx.send(embed=em)
    

#send command
@bot.command()
async def send(ctx, member: discord.Member ,amount=None):
    await open_account(ctx.author)
    await open_account(member)

    if amount == None:
        em = discord.Embed(title=f" ❌ Error!",description="Please enter the amount", color=0xe74c3c)
        await ctx.send(embed=em)
        return

    bal = await update_bank(ctx.author)

    if amount == 'all':
        amount = bal[1]
    if int(amount) > bal[1]:
        em = discord.Embed(title=f" ❌ Error!",description="You don't have enough money", color=0xe74c3c)
        await ctx.send(embed=em)
        return
    if int(amount) < 0:
        em = discord.Embed(title=f" ❌ Error!",description="The amount must be positive", color=0xe74c3c)
        await ctx.send(embed=em)
        return
    amount = int(amount)
    
    await update_bank(ctx.author, -1*amount, 'bank') #substracting the ammount from the bank of the author
    await update_bank(member, amount, 'bank') #adding the amount to the bank of the member
    #sending the message
    em = discord.Embed(title=f"Money transfer",description=f'You gave {amount} coins', color=discord.Color.green())
    await ctx.send(embed=em)
    
#rob command
@bot.command()
async def rob(ctx, member: discord.Member):
    await open_account(ctx.author)
    await open_account(member)

    bal = await update_bank(member)
    bal2 = await update_bank(ctx.author)
    if bal[0] < 100 or bal[0]== 0:
        await ctx.send("This guy is broke, robbing him isn't worth the risk")
        return
    
    net = bal2[0]+bal2[1]

    prob = net/(bal[0]+net)
    prob = int(prob * 100)
    suc = 100-prob
    
    print(suc)  

    if random.randint(1 , 100) in range(prob +1):
        fine = random.randint(100,200)
        em = discord.Embed(title=f"You were caught!",description=f"You were caught trying to steal from your fellow warrior and have had {fine} coins taken from you. Next time they will take your head.", color=0xe74c3c)
        await ctx.send(embed=em)
        await update_bank(ctx.author, -1*fine) #substracting the ammount from the wallet of the member

    
    else :
        earning = suc*(bal[0]/100)
        if earning > bal[0]:
            earning = bal[0]     
         
        earning = int(earning)
        await update_bank(ctx.author, earning) #adding the amount to the wallet of the author
        await update_bank(member, -1*earning) #substracting the ammount from the wallet of the member
        #sending the message
        em = discord.Embed(title="Thief",description=f"You robbed and got {earning} coins", color=discord.Color.green())
        await ctx.send(embed=em)
        

#slots command
@bot.command()
async def slots(ctx, amount=None):
    await open_account(ctx.author)

    if amount == None:
        em = discord.Embed(title=f" ❌ Error!",description="Please enter the amount", color=0xe74c3c)
        await ctx.send(embed=em)
        return

    bal = await update_bank(ctx.author)

    if amount == 'all':
        amount = bal[0]
    if int(amount) > bal[0]:
        em = discord.Embed(title=f" ❌ Error!",description="You don't have enough money", color=0xe74c3c)
        await ctx.send(embed=em)
        return
    if int(amount) < 0:
        em = discord.Embed(title=f" ❌ Error!",description="The amount must be positive", color=0xe74c3c)
        await ctx.send(embed=em)
        return
    amount = int(amount)

    final = []
    #generating slot results
    for i in range(3):
        a = random.choice(['🎌', '🗡', '⚔', '👺','🏯'])
        final.append(a)
        i+=1
    #sending slots result
    await ctx.send(f"{final[0]}{final[1]}{final[2]}")
    
    if final[0]==final[1] or final[0]==final[2] or final[1]==final[2]:
        await ctx.send('You won !')
        await update_bank(ctx.author, 2*amount) #adding double the amount to the wallet
    else:
        await ctx.send('You lost')
        await update_bank(ctx.author, -1*amount)

@bot.command()
@commands.cooldown(1, 1800, commands.BucketType.user) #use the command once every 30min (1800sec)
async def work(ctx):
    await open_account(ctx.author)
    
    #list of jobs with salarys
    jobs = ["shined the Ninja’s swords","served food at a restaurant","helped the samurai carry a severed head"]

    #generating random number to chose a task
    task, salary= random.choice(jobs), random.randint(300,600)

    await update_bank(ctx.author, salary, 'bank') #adding the salary to the bank of the user
    #sending the message
    em = discord.Embed(title=f"You earned money",description=f"You {task} and earned {salary} coins", color=discord.Color.green())
    await ctx.send(embed=em)
    
    
#error beg
@beg.error
async def beg(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        t = float("{:.2f}".format(error.retry_after))
        t = str(timedelta(seconds=t))[2:7].replace(':','min')
        em = discord.Embed(title=f"Slow it down !",description=f"You can use this command once every 30mins.\n Try again in {t}s.", color=0xe74c3c)
        await ctx.send(embed=em)


#error work 
@work.error
async def work(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        t = float("{:.2f}".format(error.retry_after))
        t = str(timedelta(seconds=t))[2:7].replace(':','min')
        em = discord.Embed(title=f"Slow it down !",description=f"You can use this command once every 30mins.\n Try again in {t}s.", color=0xe74c3c)
        await ctx.send(embed=em)




#functions
async def open_account(user):
    
    users = await get_bank_data()

    if str(user.id) in users :
        return False
    else :
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 0

    with open("mainbank.json", 'w') as f:
        json.dump(users, f)
    return True


async def get_bank_data():
    with open("mainbank.json", 'r') as f:
        users = json.load(f)
    
    return users

async def update_bank(user, change=0, mode='wallet'):
    users = await get_bank_data()

    users[str(user.id)][mode] += change
    
    with open("mainbank.json", 'w') as f:
        json.dump(users, f)
    
    bal = [users[str(user.id)]['wallet'], users[str(user.id)]['bank']]
    
    return bal

        


token = 'OTMzMTE0NTgxODY4NDk0OTE4.Yec0rA.BZCe0BJ8Su301Xcqe-1iDAJUMHs'
bot.run(token)
