#!/usr/bin/python3 -u

import os
import re
import asyncio
import discord
from datetime import datetime, time
#Logging stuff for when stuff just stops working
#import logging
#logger = logging.getLogger('discord')
#logger.setLevel(logging.DEBUG)
#handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
#handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
#logger.addHandler(handler)

class EDPriceCheckBot(discord.Client):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.launch = 0
        self.memberset = set()
        self.dmset = set()
        self.timeoutlst = []
        self.timeoutdict = {}
        self.timeouttime = 60 * 1440
        self.lastcheck = datetime.now()
        self.tokenfile = open('token','r')
        self.TOKEN = self.tokenfile.readline().rstrip()
        self.botadminfile = open('botadmin','r')
        self.botadmin = int(self.botadminfile.readline().rstrip())
        self.bgtask1 = self.loop.create_task(self.price_watcher())

    def price_grabber(self,commodity):
        if commodity.lower() == 'ltd' or commodity.lower() == 'ltds':
            stationlst,systemlst,pricelst,demandlst,padsizelst,agelst = self.cmdty_reader('lowtemperaturediamond')
            return stationlst,systemlst,pricelst,demandlst,padsizelst,agelst
        elif commodity.lower() == 'vopals' or commodity.lower() == 'void opals':
            stationlst,systemlst,pricelst,demandlst,padsizelst,agelst = self.cmdty_reader('opal')
            return stationlst,systemlst,pricelst,demandlst,padsizelst,agelst
        elif commodity.lower() == 'vopal' or commodity.lower() == 'void opal':
            stationlst,systemlst,pricelst,demandlst,padsizelst,agelst = self.cmdty_reader('opal')
            return stationlst,systemlst,pricelst,demandlst,padsizelst,agelst
        elif commodity.lower() == 'painite':
            stationlst,systemlst,pricelst,demandlst,padsizelst,agelst = self.cmdty_reader('painite')
            return stationlst,systemlst,pricelst,demandlst,padsizelst,agelst
        elif commodity.lower() == 'benitoite':
            stationlst,systemlst,pricelst,demandlst,padsizelst,agelst = self.cmdty_reader('benitoite')
            return stationlst,systemlst,pricelst,demandlst,padsizelst,agelst
        elif commodity.lower() == 'musgravite':
            stationlst,systemlst,pricelst,demandlst,padsizelst,agelst = self.cmdty_reader('musgravite') 
            return stationlst,systemlst,pricelst,demandlst,padsizelst,agelst
        elif commodity.lower() == 'grandidierite':
            stationlst,systemlst,pricelst,demandlst,padsizelst,agelst = self.cmdty_reader('grandidierite')
            return stationlst,systemlst,pricelst,demandlst,padsizelst,agelst
        elif commodity.lower() == 'serendibite':
            stationlst,systemlst,pricelst,demandlst,padsizelst,agelst = self.cmdty_reader('serendibite')
            return stationlst,systemlst,pricelst,demandlst,padsizelst,agelst
        else:
            stationlst = []
            systemlst = []
            pricelst = []
            demandlst = []
            padsizelst = []
            agelst = []
            return stationlst,systemlst,pricelst,demandlst,padsizelst,agelst

    def cmdty_reader(self,cmdty):
        stationlst = []
        systemlst = []
        pricelst = []
        demandlst = []
        padsizelst = []
        agelst = []
        i = 0
        with open(cmdty) as f:
            lines = f.readlines()
            for line in lines:
                if i > 4:
                    break
                linesplit = line.split(',')
                stationlst.append(linesplit[0])
                systemlst.append(linesplit[1])
                pricelst.append('{:,}'.format(int(linesplit[2])))
                demandlst.append('{:,}'.format(int(linesplit[3])))
                padsizelst.append(linesplit[4])
                agelst.append(linesplit[5])
                i += 1
            return stationlst,systemlst,pricelst,demandlst,padsizelst,agelst

    def file_create_check(self):
        if not os.path.exists('membership.lst'):
            print('Generating membership.lst')
            os.mknod('membership.lst')
        if not os.path.exists('dm.lst'):
            print('Generating dm.lst')
            os.mknod('dm.lst')

    def memberset_gen(self):
        memberfile = open('membership.lst','r')
        for member in memberfile.readlines():
            self.memberset.add(member.rstrip())
        memberfile.close()

    def alertset_gen(self):
        dmfile = open('dm.lst','r')
        for user in dmfile.readlines():
            self.dmset.add(user.rstrip())
        dmfile.close()

    def member_write(self,guildid,channelid):
        memberfile = open('membership.lst','a')
        memberfile.write(str(guildid) + ',' + str(channelid) + '\n')
        memberfile.close()
        self.memberset_gen()

    def alert_write(self,user):
        dmfile = open('dm.lst','a')
        dmfile.write(str(user.id) + '\n')
        dmfile.close()
        self.alertset_gen()

    def alert_delete(self,user):
        with open('dm.lst','r') as f:
            lines = f.readlines()
        with open('dm.lst','w') as f:
            for line in lines:
                if not str(user.id) in line.strip('\n'):
                    f.write(line)
        self.dmset = set()
        self.alertset_gen()

    def set_channel_check(self,channelid,guildid):
        memberid = str(guildid) + ',' + str(channelid)
        for entry in self.memberset:
            guildsplit = entry.split(',')
            if str(guildid) in guildsplit[0]:
                return False
        if not memberid in self.memberset:
            return True

    def member_delete(self,target):
        with open('membership.lst','r') as f:
            lines = f.readlines()
        with open('membership.lst','w') as f:
            for line in lines:
                if not str(target.id) in line.strip('\n'):
                    f.write(line)
        self.memberset = set()
        self.memberset_gen()

    def channel_delete(self,channel):
        with open('membership.lst','r') as f:
            lines = f.readlines()
        with open('membership.lst','w') as f:
            for line in lines:
                if not str(channel) in line.strip('\n'):
                    f.write(line)
        self.memberset = set()
        self.memberset_gen()

    def dm_delete(self,user):
        with open('dm.lst','r') as f:
            lines = f.readlines()
        with open('dm.lst','w') as f:
            for line in lines:
                if not str(user) == line.strip('\n'):
                    f.write(line)
        self.dmset = set()
        self.alertset_gen()

    def unset_channel(self,messagechannel):
        self.member_delete(messagechannel)

    def alert_checker(self):
        try:
            i = 0
            stationlst,systemlst,pricelst,demandlst,padsizelst,agelst = self.price_grabber('ltd')
            idescription = ''
            while i < 5:
                price = pricelst[i].replace(',','')
                if int(price) >= 1400000:
                    demand = demandlst[i].replace(',','')
                    if int(demand) >= 2000:
                        if not stationlst[i] in self.timeoutlst:
                            print(stationlst[i] + ', ' + systemlst[i] + " has high LTD sell price!")
                            self.timeoutlst.append(stationlst[i])
                            idescription+='\n**' + stationlst[i] + ', ' + systemlst[i] + '**\n'
                            idescription+='Sell price: **' + pricelst[i] + '**\n'
                            idescription+='Demand: **' + demandlst[i] + '**\n'
                            idescription+='Pad size: **' + padsizelst[i] + '**\n'
                            idescription+='Time since last update: **' + agelst[i] + '**'
                i += 1
            if not idescription == '':
                ititle = '**High LTD price alert!**'
                em = discord.Embed(
                    title=ititle,
                    description=idescription,
                    color=0x00FF00
                )
                return em
            else:
                em = None
                return em
        except Exception as e:
            print(e)
            em = None
            return em

    def timeout_checker(self):
        if self.timeoutlst:
            for entry in self.timeoutlst:
                if not entry in self.timeoutdict:
                    self.timeoutdict[entry] = datetime.now()
                else:
                    timediff = datetime.now() - self.timeoutdict[entry]
                    checkdiff = datetime.now() - self.lastcheck
                    if int(timediff.total_seconds()) >= self.timeouttime:
                        self.lastcheck = datetime.now()
                        print("Timeout reached for " + entry)
                        del self.timeoutdict[entry]
                        self.timeoutlst.remove(entry)
                    elif int(checkdiff.total_seconds()) >= 60*60:
                        self.lastcheck = datetime.now()
                        print("----------------------------------")
                        for entry in self.timeoutlst:
                            convertedtime = self.time_converter(self.timeoutdict[entry])
                            print(convertedtime + " remaining on " + entry + " timeout")
                        print("----------------------------------")

    def time_converter(self,timeobj):
        timediff = datetime.now() - timeobj
        timeinsec = self.timeouttime - int(timediff.total_seconds())
        if timeinsec >= 60:
            timeinmin = timeinsec//60
            if timeinmin >= 60:
                timeinhr = timeinmin//60
                if timeinhr >= 24:
                    timeinday = timeinhr//24
                    timeinday = str(timeinday) + ' days'
                    return timeinday
                else:
                    timeinhr = str(timeinhr) + ' hours'
                    return timeinhr
            else:
                timeinmin = str(timeinmin) + ' mins'
                return timeinmin
        else:
            timeinsec = str(timeinsec) + ' secs'
            return timeinsec

    def tick_check(self):
        timebegin = time(13,50)
        timeend = time(14,30)
        timenow = datetime.utcnow().time()
        if timenow >= timebegin and timenow <= timeend:
            return True
        else:
            return False

    async def price_watcher(self):
        i = 0
        await self.wait_until_ready()
        print('Starting price watcher')
        while not self.is_closed():
            if self.launch == 0:
                self.launch = 1
                await asyncio.sleep(1)
            else:
                em = self.alert_checker()
                if em is not None:
                    for userid in self.dmset:
                        try:
                            user = self.get_user(int(userid))
                            if not user is None:
                                print("Sending alert to user " + str(user))
                                await user.send(embed=em)
                                await asyncio.sleep(1)
                            else:
                                print("Deleting invalid user " + str(userid))
                                self.dm_delete(userid)
                        except Exception as e:
                            print("Error on user send:")
                            print(e)
                    for member in self.memberset:
                        try:
                            channelsplit = member.split(',')
                            channel = self.get_channel(int(channelsplit[1]))
                            if not channel is None:
                                print("Sending alert to channel " + str(channel) + " in server " + str(channel.guild))
                                await channel.send(embed=em)
                                await asyncio.sleep(1)
                            else:
                                print("Deleting invalid channel " + str(member))
                                self.channel_delete(member)
                        except Exception as e:
                            print("Error on channel send:")
                            print(e)
                    print("Done sending alerts to users")
                    self.timeout_checker()
                    await asyncio.sleep(1)
                else:
                    self.timeout_checker()
                    await asyncio.sleep(1)

    async def on_guild_channel_delete(self,channel):
        print("Bot removed from channel " + str(channel))
        self.member_delete(channel)

    async def on_guild_remove(self,guild):
        print("Bot removed from server " + str(guild))
        self.member_delete(guild)

    async def on_message(self,message):
        #Make sure message.guild is not NoneType and create var for checking against memberset
        if message.guild is None:
            return
        else:
            memberid = str(message.guild.id) + ',' + str(message.channel.id)

        #Don't reply to yourself
        if message.author == self.user:
            return

        #Reload DM and Membership sets as long as it's from the bot owner
        if message.content.lower().startswith('!reloadsets'):
            if message.author.id == self.botadmin:
                self.alertset_gen()
                self.memberset_gen()
                print("Both sets regenerated")

        #Set primary channel
        if message.content.lower().startswith('!setchannel'):
            result = self.set_channel_check(message.channel.id,message.guild.id)
            if result == True:
                print(str(message.channel) + " has been set as the primary channel in the server " + str(message.guild))
                self.member_write(message.guild.id, message.channel.id)
                await message.channel.send('Channel set.')
            else:
                await message.channel.send('Channel already set, please run `!unsetchannel` in the currently set channel before running this command again.')

        #Only allow calls from channels in the membership set
        if not memberid in self.memberset:
            return

        #Help response
        if message.content.lower().startswith('!help'):
            em = discord.Embed(
                title='EDPriceAlert Help',
                description="""Available Commands:
                            `!help`
                            Displays this help message
                            `!setchannel`
                            Sets primary channel for price alerts and communication based on where the command is executed
                            `!unsetchannel`
                            Unsets primary channel (Must be run in the currently assigned primary channel)
                            `!check x`
                            Checks top 5 mineral prices where x is the name of the mineral
                            `!getalerts`
                            Sends DM to user when prices for LTD's reach 1.4mil with at least 2000 demand
                            `!stopalerts`
                            Removes user from DM list
                            `!prune`
                            Deletes all messages belonging to EDPriceCheckBot
                            """,
                color=0x00FF00
            )
            await message.channel.send(embed=em)

        #Unset primary channel
        if message.content.lower().startswith('!unsetchannel'):
            self.unset_channel(message.channel)
            await message.channel.send('Channel unset, use `!setchannel` to set a new primary channel.')

        #Delete bot messages
        if message.content.lower().startswith('!prune'):
            async for message in message.channel.history(limit=200):
                if message.author == client.user:
                    try:
                        await message.delete()
                    except Exception as e:
                        print('Failed to delete message')
                        print(e)
            print('Messages pruned from channel ' + str(message.channel) + ' in server ' + str(message.guild))

        #Mineral check
        if message.content.lower().startswith('!check'):
            content = re.split('(?i)(!check )', message.content)[-1]
            stationlst,systemlst,pricelst,demandlst,padsizelst,agelst = self.price_grabber(content)
            if stationlst:
                i = 0
                idescription = ''
                while i < 5:
                    idescription+='\n**' + stationlst[i] + ', ' + systemlst[i] + '**\n'
                    idescription+='Sell price: **' + pricelst[i] + '**\n'
                    idescription+='Demand: **' + demandlst[i] + '**\n'
                    idescription+='Pad size: **' + padsizelst[i] + '**\n'
                    idescription+='Time since last update: **' + agelst[i] + '**'
                    i += 1
                if not idescription == '':
                    result = self.tick_check()
                    if result:
                        ititle = '_**Prices may be affected by server tick!**_\n**Top 5 prices for ' + content + '**'
                    else:
                        ititle = '**Top 5 prices for ' + content + '**'
                    em = discord.Embed(
                        title=ititle,
                        description=idescription,
                        color=0x00FF00
                    )

                    await message.channel.send(embed=em)
                    i += 1
            else:
                await message.channel.send('Unsupported or unknown mineral entered.')

        #Add user to DM list
        if message.content.lower().startswith('!getalerts'):
            if not str(message.author.id) in self.dmset:
                self.alert_write(message.author)
                print(message.author + ' has been added to the alert list.')
                await message.channel.send('Added to alert list, DM incoming!')
                await message.author.send('You will now get a DM every time a a station is selling for at least 1.5m and demand is at least 2,000.  To unsubscribe, send the `!stopalerts` command in the channel you subscribed from.')
            else:
                await message.channel.send('You are already on the alert list.')

        #Delete user from DM list
        if message.content.lower().startswith('!stopalerts'):
            self.alert_delete(message.author)
            print(message.author + ' has been removed from the alert list.')
            await message.channel.send('You have been removed from the alert list.')
    
    async def on_ready(self):
        print('Checking for dm and membership files')
        self.file_create_check()
        print('Generating memberset')
        self.memberset_gen()
        print('Generating dmset')
        self.alertset_gen()
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

print("Starting bot at " + (datetime.now().strftime("%H:%M:%S on %m/%d/%Y")))
client = EDPriceCheckBot()
client.run(client.TOKEN)
