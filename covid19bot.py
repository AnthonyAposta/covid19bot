# TODO or ideas
# - [x] /info
#   - [ ] top countries infected and deltas in /info
# - [ ] /graph
# - [ ] /help
# - [ ] /map
# - [ ] /daily_subscribe
# - [ ] /news

import COVID19Py
import telepot
import os
import subprocess
import time

token = os.getenv("COV19BOT_TOKEN")
bot = telepot.Bot(token)

covid19 = COVID19Py.COVID19(data_source="jhu")

allData = covid19.getAll()
total = allData['latest']
locations = allData['locations']
ids = [country['country_code'] for country in locations]

print("Ready: Database updated")

def recebendoMsg(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(chat_id, msg['from']['first_name']+":", msg['text'])
##########################################
    if msg['text'] == '/start':
        bot.sendMessage(chat_id, 'Hello '+msg['from']['first_name']+', I can show you the stats of the covid19 from all around the world.')
##########################################
    if msg['text'].split(' ',1)[0] == '/graph':
        bot.sendChatAction(chat_id, 'upload_photo')
        if len(msg['text'].split(' ',1)) == 2:
            bot.sendPhoto(chat_id, open(msg['text'].split(' ',1)[1]+".jpg",'rb'))
        else:
            bot.sendPhoto(chat_id, open("world.png",'rb'))
##########################################
    if msg['text'].split(' ',1)[0] == '/info':
        bot.sendChatAction(chat_id, 'typing')
        if len(msg['text'].split(' ',1)) == 2: # Filtered by country code
            countryID=ids.index(msg['text'].split(' ',1)[1])
            
            bot.sendMessage(chat_id, parse_mode='Markdown', text='\
            *'+str(locations[countryID]['country'])+'*\
            \n- Total confirmed cases until today: '+str(locations[countryID]['latest']['confirmed'])+'\
            \n- Total deaths until today:  '+str(locations[countryID]['latest']['deaths']))
        else: # World total cases
            bot.sendMessage(chat_id, parse_mode='Markdown', text='\
            *World*\
            \n- Total confirmed cases until today: '+str(total['confirmed'])+'\
            \n- Total deaths until today: '+str(total['deaths']))
##########################################

bot.message_loop(recebendoMsg)

while True:
    pass
