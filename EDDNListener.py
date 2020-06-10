#!/usr/bin/python3 -u

import os
import zmq
import json
import zlib
import requests
from time import sleep
from datetime import datetime

class EDDNListener():
    def __init__(self):
        self.eddnrelay = 'tcp://eddn.edcd.io:9500'
        self.eddntimeout = 600000
        self.backoff = False
        self.ltddict = {}
        self.opaldict = {}
        self.paindict = {}
        self.benidict = {}
        self.musgdict = {}
        self.grandict = {}
        self.seredict = {}
        self.tritidict = {}
        self.minerals = [
            'lowtemperaturediamond',
            'opal',
            'painite',
            'benitoite',
            'musgravite',
            'grandidierite',
            'serendibite',
            'tritium'
        ]

    def eddn_parser(self):
        ctx = zmq.Context()
        sub = ctx.socket(zmq.SUB)
        sub.setsockopt(zmq.SUBSCRIBE, b"")
        sub.setsockopt(zmq.RCVTIMEO, self.eddntimeout)
        while True:
            try:
                sub.connect(self.eddnrelay)
                while True:
                    msg = sub.recv()
                    if msg == False:
                        sub.disconnect(self.eddnrelay)
                        break
                    msg = zlib.decompress(msg)
                    jsonmsg = json.loads(msg)
                    if jsonmsg['$schemaRef'] == 'https://eddn.edcd.io/schemas/commodity/3':
                        sendrequest = 0
                        for commodity in jsonmsg['message']['commodities']:
                            if commodity['name'].lower() in self.minerals:
                                mineralname = commodity['name']
                                stationname = jsonmsg['message']['stationName']
                                systemname = jsonmsg['message']['systemName']
                                sellprice = commodity['sellPrice']
                                demand = commodity['demand']
                                if sendrequest == 0:
                                    padsize = self.pad_size_check(systemname,stationname)
                                    sendrequest += 1
                                recvtime = datetime.now()
                                self.add_to_dict(mineralname,stationname,systemname,sellprice,demand,padsize,recvtime)
                                if mineralname == 'tritium':
                                    print(mineralname,stationname,systemname,sellprice,demand,padsize,recvtime)
                    else:
                        continue
            except zmq.ZMQError as e:
                print('ZMQSocketException: ' + str(e))
                sub.disconnect(self.eddnrelay)
                sleep(5)
                self.eddn_parser()
            break

    def dict_sorter(self,dictname,cmdty):
        #Thank the stackoverflow gods for this gift of comprehension that I cannot comprehend.  REJOICE IN ITS FUNCTION!
        dictname = {k: v for k, v in sorted(dictname.items(), key=lambda item: item[1], reverse=True)}
        tempdict = {}
        i = 0
        for key,value in dictname.items():
            if i == 10:
                break
            tempdict[key] = value
            i += 1
        dictname = tempdict
        self.cmdty_write(dictname,cmdty)

    def dict_timer(self,dictname):
        deletelist = []
        for key,value in dictname.items():
            timediff = datetime.now() - value[3]
            if int(timediff.total_seconds()) >= 60*720:
                deletelist.append(key)
        for key in deletelist:
            del dictname[key]

    def add_to_dict(self,mineral,station,system,sell,demand,pad,recvtime):
        if mineral == self.minerals[0]:
            self.ltddict[station + ',' + system] = [sell,demand,pad,recvtime]
            self.dict_sorter(self.ltddict,self.minerals[0])
            self.dict_timer(self.ltddict)
        elif mineral == self.minerals[1]:
            self.opaldict[station + ',' + system] = [sell,demand,pad,recvtime]
            self.dict_sorter(self.opaldict,self.minerals[1])
            self.dict_timer(self.opaldict)
        elif mineral == self.minerals[2]:
            self.paindict[station + ',' + system] = [sell,demand,pad,recvtime]
            self.dict_sorter(self.paindict,self.minerals[2])
            self.dict_timer(self.paindict)
        elif mineral == self.minerals[3]:
            self.benidict[station + ',' + system] = [sell,demand,pad,recvtime]
            self.dict_sorter(self.benidict,self.minerals[3])
            self.dict_timer(self.benidict)
        elif mineral == self.minerals[4]:
            self.musgdict[station + ',' + system] = [sell,demand,pad,recvtime]
            self.dict_sorter(self.musgdict,self.minerals[4])
            self.dict_timer(self.musgdict)
        elif mineral == self.minerals[5]:
            self.grandict[station + ',' + system] = [sell,demand,pad,recvtime]
            self.dict_sorter(self.grandict,self.minerals[5])
            self.dict_timer(self.grandict)
        elif mineral == self.minerals[6]:
            self.seredict[station + ',' + system] = [sell,demand,pad,recvtime]
            self.dict_sorter(self.seredict,self.minerals[6])
            self.dict_timer(self.seredict)
        elif mineral == self.minerals[7]:
            self.tritidict[station + ',' + system] = [sell,demand,pad,recvtime]
            self.dict_sorter(self.tritidict,self.minerals[7])
            self.dict_timer(self.tritidict)

    def pad_size_check(self,system,station):
        try:
            r = requests.get('https://www.edsm.net/api-system-v1/stations?systemName=' + system)
            jsonmsg = json.loads(r.text)
            ratelimit = int(r.headers['X-Rate-Limit-Remaining'])
            if ratelimit == None:
                print('Ratelimit is NoneType')
            if ratelimit < 360:
                self.backoff = True
            elif ratelimit == 720:
                self.backoff = False
            if self.backoff == True:
                sleep(10)
            for entry in jsonmsg['stations']:
                if entry['name'] == station:
                    if 'outpost' in entry['type'].lower():
                        size = 'M'
                        return size
                    else:
                        size = 'L'
                        return size
        except Exception as e:
            if not e == None:
                print("Error: " + str(e))
                print(r.text)
            else:
                print("Error with NoneType:")
                print(e)
            size = 'Unknown'
            return size

    def file_create_check(self):
        for commodity in self.minerals:
            if not os.path.exists(commodity):
                print('Generating file for ' + commodity)
                os.mknod(commodity)
            else:
                print('Generating dictionary from existing price list for ' + commodity)
                self.dict_gen(commodity)

    def time_converter(self,timeobj):
        timediff = datetime.now() - timeobj
        timeinsec = int(timediff.total_seconds())
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

    def cmdty_write(self,sorteddict,cmdty):
        cmdtyfile = open(cmdty,'w')
        try:
            for key,value in sorteddict.items():
                age = self.time_converter(value[3])
                if value[2] == None:
                    value[2] = "Unknown"
                cmdtyfile.write(key + ',' + str(value[0]) + ',' + str(value[1]) + ',' + value[2] + ',' + age + '\n')
            cmdtyfile.close()
        except Exception as e:
            print(e)
            for k,v in sorteddict.items():
                print(k)
                print(v)
            cmdtyfile.close()

    def dict_gen(self,mineral):
        mineralfile = open(mineral,'r')
        for line in mineralfile.readlines():
            linesplit = line.split(',')
            station = linesplit[0]
            system = linesplit[1]
            price = int(linesplit[2])
            demand = int(linesplit[3])
            padsize = linesplit[4]
            age = datetime.now()
            self.add_to_dict(mineral,station,system,price,demand,padsize,age)
        mineralfile.close()

print("Starting parser at " + (datetime.now().strftime("%H:%M:%S on %m/%d/%Y")))
EDDNListener = EDDNListener()
EDDNListener.file_create_check()
EDDNListener.eddn_parser()
