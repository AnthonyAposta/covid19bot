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
from database import Database, Chart

token = os.getenv("COV19BOT_TOKEN")
bot = telepot.Bot(token)

DADOS = Database()

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
            countryID=DADOS.ids.index(msg['text'].split(' ',1)[1])
            Chart(DADOS.locations, countryID)
            
            bot.sendPhoto(chat_id, open(f"test_{DADOS.locations[countryID]['country_code']}.png",'rb'))
        else:
            
            bot.sendPhoto(chat_id, open("world.png",'rb'))
##########################################
    if msg['text'].split(' ',1)[0] == '/info':
        bot.sendChatAction(chat_id, 'typing')
        if len(msg['text'].split(' ',1)) == 2: # Filtered by country code
            countryID=DADOS.ids.index(msg['text'].split(' ',1)[1])
            
            bot.sendMessage(chat_id, parse_mode='Markdown', text='\
            *'+str(DADOS.locations[countryID]['country'])+'*\
            \n- Total confirmed cases until today: '+str(DADOS.locations[countryID]['latest']['confirmed'])+'\
            \n- Total deaths until today:  '+str(DADOS.locations[countryID]['latest']['deaths']))
        else: # World total cases
            bot.sendMessage(chat_id, parse_mode='Markdown', text='\
            *World*\
            \n- Total confirmed cases until today: '+str(DADOS.total['confirmed'])+'\
            \n- Total deaths until today: '+str(DADOS.total['deaths']))
##########################################

bot.message_loop(recebendoMsg)

while True:
    pass
