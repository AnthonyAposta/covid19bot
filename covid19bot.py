# TODO or ideas
# - [ ] At principle options are: /help, /graph, /info
# - [ ] /map option
# - [ ] /news
# - [ ] /daily_subscribe

import telepot
import os
import subprocess
import time

token = os.getenv("COV19BOT_TOKEN")
bot = telepot.Bot(token)

add = ""

def recebendoMsg(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(chat_id, msg['from']['first_name']+":", msg['text'])
##########################################
    if msg['text'] == '/start':
        bot.sendMessage(chat_id, 'Hello '+msg['from']['first_name']+', I can show you the stats of the covid19 from all around the world.')
##########################################
    if msg['text'].split(' ',1)[0] == '/graph':
        bot.sendMessage(chat_id, 'Ok, I\'m doing it...')
        if len(msg['text'].split(' ',1)) == 2:
            bot.sendPhoto(chat_id, open(msg['text'].split(' ',1)[1]+".jpg",'rb'))
        else:
            bot.sendPhoto(chat_id, open("world.png",'rb'))
##########################################
    if msg['text'].split(' ',1)[0] == '/info':
        bot.sendMessage(chat_id, 'Ok, I\'m doing it...')
        if len(msg['text'].split(' ',1)) == 2 and msg['text'].split(' ',1)[1] == 'BR':
            bot.sendMessage(chat_id, parse_mode='Markdown', text='\
            *Brazil*\
            \n- Confirmed cases today:\
            \n- Death cases today:\
            \n- Confirmed cases cumulated:\
            \n- Death cases cumulated:')
        else:
            bot.sendMessage(chat_id, parse_mode='Markdown', text='\
            *World*\
            \n- Confirmed cases today:\
            \n- Death cases today:\
            \n- Confirmed cases cumulated:\
            \n- Death cases cumulated:')
##########################################

bot.message_loop(recebendoMsg)

while True:
    pass
