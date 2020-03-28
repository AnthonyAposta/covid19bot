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

def process_msg(msg):

    usr_name = msg['from']['first_name']
    comandos = msg['text'].split(' ',1)

    return usr_name, comandos

def recebendoMsg(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    usr_name, comandos = process_msg(msg)

    print(chat_id, f"{usr_name}:, {msg['text']}")
##########################################
    if comandos[0] == '/start':
        bot.sendMessage(chat_id, f"Hello {usr_name}, I can show you the stats of the covid19 from all around the world.")
##########################################
    if comandos[0] == '/graph':
        bot.sendChatAction(chat_id, 'upload_photo')
        
        if len(comandos) == 2:
            countryID = DADOS.ids.index(comandos[1])
            
            try:
                bot.sendPhoto(chat_id, open(f"charts/test_{DADOS.locations[countryID]['country_code']}.png",'rb'))
            except:
                Chart(DADOS.locations[countryID])
                bot.sendPhoto(chat_id, open(f"charts/test_{DADOS.locations[countryID]['country_code']}.png",'rb'))
        else:
            
            bot.sendPhoto(chat_id, open("world.png",'rb'))
##########################################
    if comandos[0] == '/info':
        bot.sendChatAction(chat_id, 'typing')
        if len(comandos) == 2: # Filtered by country code
            countryID=DADOS.ids.index(comandos[1])
            
            bot.sendMessage(chat_id, parse_mode='Markdown', text=f"\
            *{DADOS.locations[countryID]['country']}*\
            \n- Total confirmed cases until today: {DADOS.locations[countryID]['latest']['confirmed']}\
            \n- Total deaths until today: {DADOS.locations[countryID]['latest']['deaths']}")
        else: # World total cases
            bot.sendMessage(chat_id, parse_mode='Markdown', text=f"\
            *World*\
            \n- Total confirmed cases until today: {DADOS.total['confirmed']}\
            \n- Total deaths until today: {DADOS.total['deaths']}")
##########################################

bot.message_loop(recebendoMsg)

while True:
    pass
