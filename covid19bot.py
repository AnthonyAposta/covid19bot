##### TODO or ideas #####
#
# - [ ] /map
# - [ ] /news

import COVID19Py
import telepot
import numpy as np
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import os
import subprocess
import time
from database import Database, Chart, subs_db
import schedule

token = os.getenv("COV19BOT_TOKEN")

bot = telepot.Bot(token)

SUBS = subs_db()
print("* Subscribers database updated")

DADOS = Database()
print("* Database updated")

print("Ready!")


# Process the received message, spliting it in the user name and the command arguments 
def process_msg(msg):
    usr_name = msg['from']['first_name']
    comandos = msg['text'].split(' ')

    return usr_name, comandos


# To handle with the response from inline keyboard action
def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

    days_str      = query_data.split(' ')[0]
    countryID_str = query_data.split(' ')[1]
    group_id      = int(query_data.split(' ')[2])

    bot.sendChatAction(group_id, 'upload_photo')

    if countryID_str != 'None':
        countryID = int(countryID_str)
        countryCode = DADOS.locations[countryID]['country_code']

        if days_str == 'All':
            Chart([DADOS.locations[countryID]], EXP=True)
            bot.sendPhoto(group_id, open(f"charts/chart_{countryCode}.png",'rb'))
        else:
            Chart([DADOS.locations[countryID]], int(days_str), EXP=True)
            bot.sendPhoto(group_id, open(f"charts/chart{days_str}_{countryCode}.png",'rb'))
            
    else:
        if days_str == 'All':
            Chart(DADOS.locations, WORLD=True)
            bot.sendPhoto(group_id, open(f"charts/chart_world.png",'rb'))
        else:
            Chart(DADOS.locations, int(days_str), WORLD=True)
            bot.sendPhoto(group_id, open(f"charts/chart{days_str}_world.png",'rb'))

            
# Send a message asking from how many days the user want to see in the chart, showing a inline keyboard
def show_date_keyboard(chat_id, countryID=None):
    bot.sendMessage(chat_id, 'Ok, now choose how many days you want to see:', reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="10 days",                   callback_data=f"10 {countryID} {chat_id}"),
         InlineKeyboardButton(text="30 days",                   callback_data=f"30 {countryID} {chat_id}")],
        [InlineKeyboardButton(text="60 days",                   callback_data=f"60 {countryID} {chat_id}"),
         InlineKeyboardButton(text="All days since first case", callback_data=f"All {countryID} {chat_id}")]]))


# show informations
def send_subscribe_msg():
    subscribers = SUBS.subscribers()

    for sub in subscribers:
        chat_id = sub[0]
        info(chat_id)
        

######################### BOT COMMANDS ###########################

# show a welcome message and init the bot 
def start(chat_id, msg):
    usr_name, comandos = process_msg(msg)

    bot.sendMessage(chat_id, f"Hello {usr_name}, Worldwide statistics about COVID-19. type /help for a guide")

# make a graphics
def chart(chat_id, msg):
    usr_name, comandos = process_msg(msg)
    
    if len(comandos) > 2: # if the user pass more than two arguments to chart

        try:
            countryID = [np.where(DADOS.ids == comandos[i].upper())[0][0] for i in range(1,len(comandos))]

            # make a string with the country codes
            name = 'compare_'
            for i in range(1,len(comandos)):
                name += comandos[i].upper()
                
            
            # if its not generated yet
            Chart([DADOS.locations[i] for i in countryID], COMPARATIVE=True)
            bot.sendPhoto(chat_id, open(f"charts/chart_{name}.png",'rb'))
        
        except:
            bot.sendChatAction(chat_id, 'typing')
            bot.sendMessage(chat_id, text="Country code not found. Please check /list.\n")
    
    elif len(comandos) == 2: # if the user pass just one argument (country)
        
        try:
            countryID = np.where(DADOS.ids == comandos[1].upper())[0][0]
            show_date_keyboard(chat_id, countryID)
        
        except:
            bot.sendChatAction(chat_id, 'typing')
            bot.sendMessage(chat_id, text="Country code not found. Please check /list.\n")
    
    else:
        show_date_keyboard(chat_id)


# make a graphics
def chart2(chat_id, msg):
    usr_name, comandos = process_msg(msg)
    
    if len(comandos) >= 2: # if the user pass more than two arguments to chart
        
        try:
            countryID = [np.where(DADOS.ids == comandos[i].upper())[0][0] for i in range(1,len(comandos))]

            # make a string with the country codes
            name = 'traj_'
            for i in range(1,len(comandos)):
                name += comandos[i].upper()
                
            
            try:
                Chart([DADOS.locations[i] for i in countryID], TRAJECTORY=True)
                bot.sendPhoto(chat_id, open(f"charts/chart_{name}.png",'rb'))
            
            except:
                bot.sendChatAction(chat_id, 'typing')
                bot.sendMessage(chat_id, text="Number of cases is less than 100.\n")

        
        except:
            bot.sendChatAction(chat_id, 'typing')
            bot.sendMessage(chat_id, text="Country code not found. Please check /list.\n")

        
    else:
        bot.sendChatAction(chat_id, 'typing')
        bot.sendMessage(chat_id, text="This command needs arguments.\n")

        
        
# show informations
def info(chat_id, msg={'from': {'first_name': ''}, 'text': ''}):
    usr_name, comandos = process_msg(msg)
    
    bot.sendChatAction(chat_id, 'typing')
    
    if len(comandos) > 2: # if the user pass more than two countries

        try:
            countryID = [np.where(DADOS.ids == comandos[i].upper())[0][0] for i in range(1,len(comandos))]

            message = []
            for i in countryID:
                message.append(f"*{DADOS.locations[i]['country']}*\
                \n- Total confirmed cases: {DADOS.locations[i]['latest']['confirmed']}\
                \n- Total deaths: {DADOS.locations[i]['latest']['deaths']}")
                
            bot.sendMessage(chat_id, parse_mode='Markdown', text='\n\n'.join(message))
        
        except:
            bot.sendChatAction(chat_id, 'typing')
            bot.sendMessage(chat_id, text="Country code not found. Please check /list.\n")
    
    elif len(comandos) == 2: # Filtered by country code

        try:
            countryID=np.where(DADOS.ids == comandos[1].upper())[0][0]
            
            bot.sendMessage(chat_id, parse_mode='Markdown', text=f"\
            *{DADOS.locations[countryID]['country']}*\
            \n- Total confirmed cases: {DADOS.locations[countryID]['latest']['confirmed']}\
            \n- Total deaths: {DADOS.locations[countryID]['latest']['deaths']}")
        
        except:
            bot.sendChatAction(chat_id, 'typing')
            bot.sendMessage(chat_id, text="Country code not found. Please check /list.\n")
        
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


# subscription to daily /info
def subscribe(chat_id, msg):
    usr_name, comandos = process_msg(msg)
    
    status = SUBS.add(chat_id, usr_name)

    if status == 0 :
        bot.sendChatAction(chat_id, 'typing')
        bot.sendMessage(chat_id, text="Ok, now you are subscribed to @cov19brbot.\n")
    else :
        bot.sendChatAction(chat_id, 'typing')
        bot.sendMessage(chat_id, text="You are already subscribed.\n")        
        

# unsubscription to daily /info
def unsubscribe(chat_id, msg):
    usr_name, comandos = process_msg(msg)
    
    status = SUBS.remove(chat_id, usr_name)

    if status == 0 :
        bot.sendChatAction(chat_id, 'typing')
        bot.sendMessage(chat_id, text="Ok, you have been unsubscribed from @cov19brbot.\n")
    else :
        bot.sendChatAction(chat_id, 'typing')
        bot.sendMessage(chat_id, text="You are already unsubscribed.\n")


# help message
def help_msg(chat_id, msg):
    usr_name, comandos = process_msg(msg)
    
    bot.sendChatAction(chat_id, 'typing')
            
    bot.sendMessage(chat_id, parse_mode='Markdown', text="*The available commands are:*\n\n\n\
    /help - to see this message\n\n\
    /info br us it ... - shows the latest informations and stats for the covid19 for a set of specific countries. By default, the global status is shown. See /list.\n\n\
    /chart br us it ... - deploy a time evolution chart of covid19, the command will bring a keyboard to choose how many days you want to see, if passed more than one country, it will show a comparison between selected countries\n\n\
    /chart2 br us it ... - This command charts the new confirmed cases of COVID-19 in the past week vs. the total confirmed cases to date. When plotted in this way, exponential growth is represented as a straight line that slopes upwards. Notice that almost all countries follow a very similar path of exponential growth. For more information, look at: https://aatishb.com/covidtrends/\n\n\
    /subscribe - to subscribe to daily notifier\n\n\
    /unsubscribe - to unsubscribe you from the daily notifier\n\n\
    /list - shows the available countries and their respective code")

###################################################################


# To receive and take action depending on the message or command
def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    usr_name, comandos = process_msg(msg)

    # show message send to bot
    print(chat_id, f"{usr_name}: {msg['text']}")
    
    if comandos[0] == '/start' or comandos[0] == '/start@cov19brbot':
        start(chat_id, msg)

    elif comandos[0] == '/chart' or comandos[0] == '/chart@cov19brbot':
        chart(chat_id, msg)

    elif comandos[0] == '/chart2' or comandos[0] == '/chart2@cov19brbot':
        chart2(chat_id, msg)    
        
    elif comandos[0] == '/info' or comandos[0] == '/info@cov19brbot':
        info(chat_id, msg)
        
    elif comandos[0] == '/list' or comandos[0] == '/list@cov19brbot':
        list_countries(chat_id, msg)

    elif comandos[0] == '/subscribe' or comandos[0] == '/subscribe@cov19brbot':
        subscribe(chat_id, msg)

    elif comandos[0] == '/unsubscribe' or comandos[0] == '/unsubscribe@cov19brbot':
        unsubscribe(chat_id, msg)
        
    elif comandos[0] == '/help' or comandos[0] == '/help@cov19brbot':
        help_msg(chat_id, msg)

    else:
        bot.sendChatAction(chat_id, 'typing')
        bot.sendMessage(chat_id, parse_mode='Markdown', text="Command not found. Please, see the available option in /help.")


# schedule to send message every day at 11:00 UTC 
schedule.every().day.at("11:00").do(send_subscribe_msg)
        
MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query}).run_as_thread()

while 1:
    time.sleep(10)
    DADOS.run_update()
