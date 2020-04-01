##### TODO or ideas #####
# - [x] Bot answer to any command: "Command not found. See /help."
# - [x] /info more than one country
# - [x] Comment code
# - [x] /chart <nothing>: make world chart
# - [x] top countries infected and deltas in /info
# - [ ] fix max number of countries
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


# Process the received message, spliting it in the user name and the command arguments 
def process_msg(msg):
    usr_name = msg['from']['first_name']
    comandos = msg['text'].split(' ')

    return usr_name, comandos


# To handle with the response from inline keyboard action
def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    bot.sendChatAction(from_id, 'upload_photo')

    days_str      = query_data.split(' ')[0]
    countryID_str = query_data.split(' ')[1]

    if countryID_str != 'None':
        countryID = int(countryID_str)
        countryCode = DADOS.locations[countryID]['country_code']

        if days_str == 'All':
            Chart([DADOS.locations[countryID]])
            bot.sendPhoto(from_id, open(f"charts/chart_{countryCode}.png",'rb'))
        else:
            Chart([DADOS.locations[countryID]], int(days_str))
            bot.sendPhoto(from_id, open(f"charts/chart{days_str}_{countryCode}.png",'rb'))
            
    else:
        if days_str == 'All':
            Chart(DADOS.locations)
            bot.sendPhoto(from_id, open(f"charts/chart_world.png",'rb'))
        else:
            Chart(DADOS.locations, int(days_str))
            bot.sendPhoto(from_id, open(f"charts/chart{days_str}_world.png",'rb'))

            
# Send a message asking from how many days the user want to see in the chart, showing a inline keyboard
def show_date_keyboard(chat_id, countryID=None):
    bot.sendMessage(chat_id, 'Ok, now choose how many days you want to see:', reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="10 days",                   callback_data=f"10 {countryID}"),
         InlineKeyboardButton(text="30 days",                   callback_data=f"30 {countryID}")],
        [InlineKeyboardButton(text="60 days",                   callback_data=f"60 {countryID}"),
         InlineKeyboardButton(text="All days since first case", callback_data=f"All {countryID}")]]))



######################### BOT COMMANDS ###########################

# show a welcome message and init the bot 
def start(chat_id, msg):
    usr_name, comandos = process_msg(msg)

    bot.sendMessage(chat_id, f"Hello {usr_name}, Worldwide statistics about COVID-19. type /help for a guide")

    
# make a graphics
def chart(chat_id, msg):
    usr_name, comandos = process_msg(msg)
    
    if len(comandos) > 2: # if the user pass more than two arguments to chart
        countryID = [np.where(DADOS.ids == comandos[i].upper())[0][0] for i in range(1,len(comandos))]

        # make a string with the country codes
        name = 'compare_'
        for i in range(1,len(comandos)):
            name += comandos[i].upper()
            
        try: # try send the chart if it is generated
            bot.sendPhoto(chat_id, open(f"charts/chart_{name}.png",'rb'))
        except: # if its not generated yet
            Chart([DADOS.locations[i] for i in countryID])
            bot.sendPhoto(chat_id, open(f"charts/chart_{name}.png",'rb'))
    elif len(comandos) == 2: # if the user pass just one argument (country)
        countryID = np.where(DADOS.ids == comandos[1].upper())[0][0]
        show_date_keyboard(chat_id, countryID)
    else:
        show_date_keyboard(chat_id)

        
# show informations
def info(chat_id, msg):
    usr_name, comandos = process_msg(msg)
    
    bot.sendChatAction(chat_id, 'typing')
    
    if len(comandos) > 2: # if the user pass more than two countries
        countryID = [np.where(DADOS.ids == comandos[i].upper())[0][0] for i in range(1,len(comandos))]

        message = []
        for i in countryID:
            message.append(f"*{DADOS.locations[i]['country']}*\
            \n- Total confirmed cases: {DADOS.locations[i]['latest']['confirmed']}\
            \n- Total deaths: {DADOS.locations[i]['latest']['deaths']}")
            
        bot.sendMessage(chat_id, parse_mode='Markdown', text='\n\n'.join(message))
    
    elif len(comandos) == 2: # Filtered by country code
        countryID=np.where(DADOS.ids == comandos[1].upper())[0][0]
        
        bot.sendMessage(chat_id, parse_mode='Markdown', text=f"\
        *{DADOS.locations[countryID]['country']}*\
        \n- Total confirmed cases: {DADOS.locations[countryID]['latest']['confirmed']}\
        \n- Total deaths: {DADOS.locations[countryID]['latest']['deaths']}")
        
    else: # World total cases
        bot.sendMessage(chat_id, parse_mode='Markdown', text=f"\
        *World*\
        \n- Total confirmed cases: {DADOS.total['confirmed']}\
        \n- Total deaths: {DADOS.total['deaths']}\
        \n\
        \n*Most infected countries:*\
        \n- {DADOS.ranked[0][0]}: {DADOS.ranked[0][1]}\
        \n- {DADOS.ranked[1][0]}: {DADOS.ranked[1][1]}\
        \n- {DADOS.ranked[2][0]}: {DADOS.ranked[2][1]}\
        \n- {DADOS.ranked[3][0]}: {DADOS.ranked[3][1]}\
        \n- {DADOS.ranked[4][0]}: {DADOS.ranked[4][1]}")


# show a list of all the countries available
def list_countries(chat_id, msg):
    usr_name, comandos = process_msg(msg)

    bot.sendChatAction(chat_id, 'typing')
    
    message = []
    for location in DADOS.locations:
        string = f"{location['country_code']}:\t{location['country']}"
        if string not in message:
            message.append(string)

    bot.sendMessage(chat_id, text="Countries list:\n"+'\n'.join(message))


# help message
def help_msg(chat_id, msg):
    usr_name, comandos = process_msg(msg)
    
    bot.sendChatAction(chat_id, 'typing')
            
    bot.sendMessage(chat_id, parse_mode='Markdown', text="*The list of available commands is:*\n\n\n\
    /help - to see this message\n\n\
    /info <country code 1> <country code 2> ... - shows the latest informations and stats for the covid19 for a set of specific countries. By default, the global status is shown\n\n\
    /chart <country code 1> <country code 2> ... - deploy a time evolution chart of covid19, the command will bring a keyboard to choose how many days you want to see, if passed more than one country, it will show a comparison between selected countries\n\n\
    /list - shows the available countries and their respective code")

###################################################################


# To receive and take action depending on the message or command
def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    usr_name, comandos = process_msg(msg)

    # show message send to bot
    print(chat_id, f"{usr_name}: {msg['text']}")
    
    if comandos[0] == '/start':
        start(chat_id, msg)

    elif comandos[0] == '/chart':
        chart(chat_id, msg)
        
    elif comandos[0] == '/info':
        info(chat_id, msg)
        
    elif comandos[0] == '/list':
        list_countries(chat_id, msg)
        
    elif comandos[0] == '/help':
        help_msg(chat_id, msg)

    else:
        bot.sendChatAction(chat_id, 'typing')
        bot.sendMessage(chat_id, parse_mode='Markdown', text="Command not found. Please, see the available option in /help.")

MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query}).run_as_thread()

while 1:
    time.sleep(10)
