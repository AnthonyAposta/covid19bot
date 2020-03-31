# TODO or ideas
# - [x] /info
#   - [ ] top countries infected and deltas in /info
# - [x] /graph
# - [x] /list
# - [x] /help
# - [ ] /map
# - [ ] /daily_subscribe
# - [ ] /news

import COVID19Py
import telepot
import numpy as np
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
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
    comandos = msg['text'].split(' ')

    return usr_name, comandos


def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    bot.sendChatAction(from_id, 'upload_photo')

    days          = query_data.split(' ')[0]
    countryID_str = query_data.split(' ')[1]
    if countryID_str != None:
        countryID = int(countryID_str)
        try:
            bot.sendPhoto(from_id, open(f"charts/chart{days}_{DADOS.locations[countryID]['country_code']}.png",'rb'))
        except:
            Chart([DADOS.locations[countryID]], days)
            bot.sendPhoto(from_id, open(f"charts/chart{days}_{DADOS.locations[countryID]['country_code']}.png",'rb'))
    else:
        #try:
        bot.sendPhoto(from_id, open(f"charts/world.png",'rb'))

        #except:
            #Chart(DADOS.locations[countryID], days)
            #bot.sendPhoto(from_id, open(f"charts/world.png",'rb'))
            
    
def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    usr_name, comandos = process_msg(msg)

    print(chat_id, f"{usr_name}: {msg['text']}")
##########################################
    if comandos[0] == '/start':
        bot.sendMessage(chat_id, f"Hello {usr_name}, Worldwide statiscs about COVID-19. type /help for a guide")
##########################################
    if comandos[0] == '/chart':
        if len(comandos) > 2:
            countryID = [np.where(DADOS.ids == comandos[i].upper())[0][0] for i in range(1,len(comandos))]

            name = 'compare_'
            for i in range(1,len(comandos)):
                name += comandos[i].upper()

            try:
                bot.sendPhoto(chat_id, open(f"charts/chart_{name}.png",'rb'))
            except:
                Chart([DADOS.locations[i] for i in countryID])
                bot.sendPhoto(chat_id, open(f"charts/chart_{name}.png",'rb'))
        elif len(comandos) == 2:
            countryID = np.where(DADOS.ids == comandos[1].upper())[0][0]

            bot.sendMessage(chat_id, 'Ok, now choose how many days you want to see:',
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="10 days",                   callback_data=f"10 {countryID}"),
                                 InlineKeyboardButton(text="30 days",                   callback_data=f"30 {countryID}")],
                                [InlineKeyboardButton(text="60 days",                   callback_data=f"60 {countryID}"),
                                 InlineKeyboardButton(text="All days since first case", callback_data=f"0  {countryID}")]]))
        else:
            bot.sendMessage(chat_id, 'Ok, now choose how many days you want to see:',
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="10 days",                   callback_data=f"10 None"),
                                 InlineKeyboardButton(text="30 days",                   callback_data=f"30 None")],
                                [InlineKeyboardButton(text="60 days",                   callback_data=f"60 None"),
                                 InlineKeyboardButton(text="All days since first case", callback_data=f"0  None")]]))
        
##########################################
    if comandos[0] == '/info':
        bot.sendChatAction(chat_id, 'typing')
        if len(comandos) == 2: # Filtered by country code
            countryID=np.where(DADOS.ids == comandos[1].upper())[0][0]
            
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
    if comandos[0] == '/list':
        bot.sendChatAction(chat_id, 'typing')

        message = []
        for location in DADOS.locations:
            string = f"{location['country_code']}:\t{location['country']}"
            if string not in message:
                message.append(string)

        bot.sendMessage(chat_id, text="Countries list:\n"+'\n'.join(message))
##########################################
    if comandos[0] == '/help':
        bot.sendChatAction(chat_id, 'typing')
            
        bot.sendMessage(chat_id, parse_mode='Markdown', text="*The list of available commands is:*\n\n\n/help - to see this message\n\n/info <country code> - shows the latest informations and stats for the covid19 for a specific country. By default, the global status is shown\n\n/chart <country code 1> <country code 2> ... - deploy a time evolution chart of covid19, the command will bring a keyboard to choose how many days you want to see, if passed more than one country, it will show a comparison between selected countries \n\n/list - shows the available countries and their respective code")
##########################################

MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query}).run_as_thread()

while 1:
    time.sleep(10)
