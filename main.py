from pymongo import MongoClient
import discord
from discord.ext import commands
import os
import random
from datetime import timedelta
import asyncio
import re



os.chdir('/home/sgp/Documents/Dev/bushicro')


client = MongoClient("..")
db = client["discord"]
data = db["mainbank"]


print("Loading...")

intents = intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)
bot.remove_command('help')


@bot.event
async def on_ready():
    print('Bot ready')


#Balance command
@bot.command(aliases=["bal"])
async def balance(ctx):
    
    user = data.find_one({'_id':ctx.author.id})

    if user == None:
        data.insert_one({'_id':ctx.author.id, 'name': ctx.author.name, 'wallet': 0, 'bank': 0, 'pfp': ctx.author.avatar.url})
        bal = [0,0]

    else : 
        user = data.find_one({'_id':ctx.author.id})
        bal = user['wallet'], user['bank'] 

    em = discord.Embed(title= f"{ctx.author.name}", color=discord.Color.blue())
    em.add_field(name ='Wallet balance', value=bal[0])
    em.add_field(name= 'Bank balance', value=bal[1])
    await ctx.send(embed=em)

#work command
@bot.command()
@commands.cooldown(1, 1800, commands.BucketType.user) #use the command once every 30min (1800sec)
async def work(ctx):
    await open_account(ctx.author)
    
    #list of jobs with salarys
    jobs = [  {"task": "Cleaned the toilet at KFC", "salary": 300},  {"task": "Walked dogs for a neighbor", "salary": 350},  {"task": "Performed a magic show for a birthday party", "salary": 400},  {"task": "Did stand-up comedy at a local club", "salary": 450},  {"task": "Completed a challenging escape room", "salary": 500},  {"task": "Tested rollercoasters at an amusement park", "salary": 550},  {"task": "Explored a haunted house", "salary": 575},  {"task": "Battled monsters in a virtual reality game", "salary": 600},  {"task": "Delivered food for a food delivery service", "salary": 325},  {"task": "Performed as a street musician", "salary": 375}]


    #generating random task with random salary
    job = random.choice(jobs)
    
    #adding the salary to the bank of the user   
    data.update_one({"_id":ctx.author.id}, {"$inc" : {"bank" : job["salary"]}}) 
    
    #sending the message
    em = discord.Embed(title="You earned money",description=f"You {job['task']} and earned {job['salary']} coins", color=discord.Color.green())
    await ctx.send(embed=em)
 
#error work 
@work.error
async def work(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        t = float("{:.2f}".format(error.retry_after))
        t = str(timedelta(seconds=t))[2:7].replace(':','min')
        em = discord.Embed(title=f"Slow it down !",description=f"You can use this command once every 30mins.\n Try again in {t}s.", color=0xe74c3c)
        await ctx.send(embed=em)  

#beg command
@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user) #use command once every 30min (1800sec)
async def beg(ctx):
    await open_account(ctx.author)
    
    #generating random earnings
    earnings = random.randrange(101)

    #storing earnings in the wallet
    data.update_one({"_id":ctx.author.id}, {"$inc" : {'wallet' : earnings}})

    #sending message
    em = discord.Embed(title=f"Donation !",description=f'Someone gave you {earnings} coins !!', color=discord.Color.green())
    await ctx.send(embed=em)


#deposit command
@bot.command(aliases=['dep'])
async def deposit(ctx, amount=None):
    await open_account(ctx.author)

    if amount == None:
        em = discord.Embed(title=f" ❌ Error!",description="Please enter the amount", color=0xe74c3c)
        await ctx.send(embed=em)
        return

    
    bal = await get_balance(ctx.author)


    if amount == 'all':
        amount = bal[0]
    
    amount = int(amount)

    if amount > bal[0]:
        em = discord.Embed(title=f" ❌ Error!",description="You don't have enough money", color=0xe74c3c)
        await ctx.send(embed=em)
        return
    if amount < 0:
        em = discord.Embed(title=f" ❌ Error!",description="The amount must be positive", color=0xe74c3c)
        await ctx.send(embed=em)
        return

    #make this in one line
    data.update_one({"_id":ctx.author.id}, {"$inc" : {'wallet' : -amount}}) #substracting the ammount from the wallet
    data.update_one({"_id":ctx.author.id}, {"$inc" : {'bank' : amount}}) #adding the amount to the bank
  
    #sending the message
    em = discord.Embed(title="Deposit",description=f"You deposited {amount} coins", color=discord.Color.green())
    await ctx.send(embed=em)

#withdraw command
@bot.command(aliases=['with'])
async def withdraw(ctx, amount=None):
    await open_account(ctx.author)

    if amount == None:
        em = discord.Embed(title=f" ❌ Error!",description="Please enter the amount", color=0xe74c3c)
        await ctx.send(embed=em)
        return

    
    bal = await get_balance(ctx.author)


    if amount == 'all':
        amount = bal[1]
    
    amount = int(amount)

    if amount > bal[1]:
        em = discord.Embed(title=f" ❌ Error!",description="You don't have enough money", color=0xe74c3c)
        await ctx.send(embed=em)
        return
    if amount < 0:
        em = discord.Embed(title=f" ❌ Error!",description="The amount must be positive", color=0xe74c3c)
        await ctx.send(embed=em)
        return

    #make this in one line
    data.update_one({"_id":ctx.author.id}, {"$inc" : {'bank' : -amount}}) #substracting the amount from the bank
    data.update_one({"_id":ctx.author.id}, {"$inc" : {'wallet' : amount}}) #adding the ammount to the wallet

    #sending the message
    em = discord.Embed(title=f"Withdrawal",description=f'You withdrew {amount} coins', color=discord.Color.green())
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

    bal = await get_balance(ctx.author)

    if amount == 'all':
        amount = bal[1]
    
    amount = int(amount)

    if amount > bal[1]:
        em = discord.Embed(title=f" ❌ Error!",description="You don't have enough money", color=0xe74c3c)
        await ctx.send(embed=em)
        return
    if amount < 0:
        em = discord.Embed(title=f" ❌ Error!",description="The amount must be positive", color=0xe74c3c)
        await ctx.send(embed=em)
        return
        
    data.update_one({'_id':ctx.author.id}, {'$inc':{'bank':-amount}}) #substracting the ammount from the bank of the author
    data.update_one({'_id':member.id}, {'$inc':{'bank':amount}}) #adding the amount to the bank of the member
  
    #sending the message
    em = discord.Embed(title=f"Money transfer",description=f'You gave {amount} coins', color=discord.Color.green())
    await ctx.send(embed=em)
    

#error beg
@beg.error
async def beg(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        t = float("{:.2f}".format(error.retry_after))
        t = str(timedelta(seconds=t))[2:7].replace(':','min')
        em = discord.Embed(title=f"Slow it down !",description=f"You can use this command once every 30mins.\n Try again in {t}s.", color=0xe74c3c)
        await ctx.send(embed=em)



#slots command
@bot.command(aliases=["slot"])
async def slots(ctx, amount=None):
    await open_account(ctx.author)

    if amount == None:
        em = discord.Embed(title=f" ❌ Error!",description="Please enter the amount", color=0xe74c3c)
        await ctx.send(embed=em)
        return

    bal = await get_balance(ctx.author)

    if amount == 'all':
        amount = bal[0]
    
    amount = int(amount)
    
    if amount < 0:
        em = discord.Embed(title=f" ❌ Error!",description="The amount must be positive", color=0xe74c3c)
        await ctx.send(embed=em)
        return
    
    if amount > bal[0]:
        em = discord.Embed(title=f" ❌ Error!",description="You don't have enough money in your wallet", color=0xe74c3c)
        await ctx.send(embed=em)
        return

    final = []
    #generating slot results
    for i in range(3):
        a = random.choice(['🎌', '🗡', '⚔', '👺','🏯'])
        final.append(a)
        # i+=1
    #sending slots result
    await ctx.send(f"{final[0]}{final[1]}{final[2]}")
    
    if final[0]==final[1] or final[0]==final[2] or final[1]==final[2]:
        await ctx.send(f'You won {amount} coins !')
        data.update_one({"_id":ctx.author.id}, {"$inc" : {'wallet' : amount}}) #adding double the amount to the wallet
    else:
        await ctx.send('You lost')
        data.update_one({"_id":ctx.author.id}, {"$inc" : {'wallet' : -amount}}) #removing the amount from the wallet


    
#rob command
@bot.command()
async def rob(ctx, member: discord.Member):
    await open_account(ctx.author)
    await open_account(member)

    bal = await get_balance(member)
    bal2 = await get_balance(ctx.author)
        
    if bal[0] < 100 or bal[0]== 0:
        await ctx.send("This guy is broke, robbing him isn't worth the risk")
        return
    
    net = sum(bal2)

    prob = net/(bal[0]+net)
    prob = int(prob * 100)
    suc = 100-prob
    
    print(suc)  

    if random.randint(1 , 100) in range(prob +1):
        fine = random.randint(100,200)
        em = discord.Embed(title=f"You were caught!",description=f"You were caught trying to steal from your fellow warrior and have had {fine} coins taken from you. Next time they will take your head.", color=0xe74c3c)
        await ctx.send(embed=em)
        data.update_one({"_id":ctx.author.id}, {"$inc" : {'wallet' : -fine}}) #substracting the ammount from the wallet of the author

    
    else :
        earning = suc*(bal[0]/100)
        if earning > bal[0]:
            earning = bal[0]     
         
        earning = int(earning)
        data.update_one({"_id":ctx.author.id}, {"$inc" : {'wallet' : earning}}) #adding the amount to the wallet of the author
        data.update_one({"_id":member.id}, {"$inc" : {'wallet' : -earning}}) #substracting the ammount from the wallet of the member         
        
        #sending the message
        em = discord.Embed(title="Thief",description=f"You robbed and got {earning} coins", color=discord.Color.green())
        await ctx.send(embed=em)




#leaderboard command
@bot.command(aliases = ["lb"])
async def leaderboard(ctx,x = 3):
    if x > 20:
        x = 20

    leader_board = {}
    total = []
    for user in data.find():
        name = int(user)
        total_amount = data.find_one({"_id":id})['wallet'] + data.find_one({"_id":id})['bank']
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total,reverse=True)    

    em = discord.Embed(title = f"Top {x} Richest People" , description = "This is decided on the basis of net worth in the bank and wallet",color = discord.Color(0xfa43ee))
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = await bot.fetch_user(id_)
        name = member.name
        em.add_field(name = f"{index}. {name}" , value = f"{amt}",  inline = False)
        if index == x:
            break
        else:
            index += 1

    await ctx.send(embed = em)

#battle command
@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user) #use the command once every 30min (1800sec)
async def battle(ctx, member: discord.Member ,amount=None):

    if amount == None:
        em = discord.Embed(title=f" ❌ Error!",description="Please enter the amount", color=0xe74c3c)
        await ctx.send(embed=em)
        return

    await open_account(ctx.author)
    await open_account(member)

    bal = await get_balance(ctx.author)
    bal2 = await get_balance(member)

    if amount == 'all':
        amount = bal[0]

    amount = int(amount) 
    if amount > bal[0]:
        em = discord.Embed(title=f" ❌ Error!",description="You don't have enough money", color=0xe74c3c)
        await ctx.send(embed=em)
        return
    if amount < 0:
        em = discord.Embed(title=f" ❌ Error!",description="The amount must be positive", color=0xe74c3c)
        await ctx.send(embed=em)
        return
    if amount > bal2[0]:
        em = discord.Embed(title=f" ❌ Error!",description=f"{member.mention} does not have enough money", color=0xe74c3c)
        await ctx.send(embed=em)
        return


    #sending challenge message
    em = discord.Embed(title=f"Challenge ⚔",description=f"{ctx.author.mention} challenged {member.mention} to a fight, the winner will get {amount} coins from the looser.\n Do you accept the challenge ? you have 30sec to decide(send y or n)", color=discord.Color.purple())
    await ctx.send(embed=em)

    def check(m):
        return m.author == member and m.channel == ctx.channel and m.content.lower() in ['y','n']

    try :
        message = await bot.wait_for('message',check=check, timeout=30.0)
        if message.content.lower()=='y':
            if random.randrange(2) == 0 : #author wins
                em = discord.Embed(title=f"{ctx.author.name} won",description=f"{ctx.author.mention} won and earned {amount} coins", color=discord.Color.green())
                await ctx.channel.send(embed=em)
                data.update_one({'_id':ctx.author.id}, {'$inc': {'wallet' : amount }}) #adding the amount to the wallet of the author
                data.update_one({'_id':member.id}, {'$inc': {'wallet' : -amount }})  #substracting the ammount from the wallet of the member
                return
            else : #memebr wins
                em = discord.Embed(title=f"{member.display_name} won",description=f"{member.mention} won and earned {amount} coins", color=discord.Color.green())
                await ctx.channel.send(embed=em)
                data.update_one({'_id':ctx.author.id}, {'$inc': {'wallet' : -amount }}) #substracting the amount from the wallet of the author
                data.update_one({'_id':member.id}, {'$inc': {'wallet' : amount }})  #adding the ammount to the wallet of the member
                return
        elif message.content.lower()=='n':
            em = discord.Embed(title=f"Challenged declined!",description=f"{member.mention} Declined the challenge", color=0xe74c3c)
            await ctx.send(embed=em)
            return

    except asyncio.TimeoutError:
        em = discord.Embed(title=f" ❌ Error!",description=f"{member.mention} did not respond", color=0xe74c3c)
        await ctx.channel.send(embed=em)


#functions 
async def open_account(member):
    user = data.find_one({'_id':member.id})

    if user == None:
        data.insert_one({'_id':member.id, 'name': member.name, 'wallet': 0, 'bank': 0, 'pfp': member.avatar.url})
    
    return True

async def get_balance(member):

    user = data.find_one({"_id":member.id})
    bal = user['wallet'], user['bank']
    
    return bal

async def convert(time):
    # [d,h,m,s]
    t = [re.search(r'\d+j',time), re.search(r'\d+h',time), re.search(r'\d+m',time), re.search(r'\d+s',time)] 

    for i in range(len(t)):
        if t[i] :
            t[i] = int(t[i].group(0)[:-1])
        else :
            t[i] = 0

    print(t)

    converted_time = t[0]*86400+t[1]*3600+t[2]*60+t[3]

    return converted_time

token = 'TOKEN'
bot.run(token)
