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
        bot.sendMessage(chat_id, 'Olá '+msg['from']['first_name']+', digite algum comando para que eu possa executá-lo')
##########################################
    if msg['text'].split(' ',1)[0] == '/opts':
        global add
        add=msg['text'].split(' ',1)[1]
##########################################
    if msg['text'].split(' ',1)[0] == '/plot':
        bot.sendMessage(chat_id, 'Ok, processando o gráfico...')
        os.system("gnuplot -e '\
        set terminal png;\
        set output \""+str(chat_id)+"_"+msg['from']['first_name']+".png\";\
        set grid;\
        "+str(add)+";\
        p "+msg['text'].split(' ',1)[1]+" w l lw 3'")
        bot.sendPhoto(chat_id, open(str(chat_id)+"_"+msg['from']['first_name']+".png",'rb'))
##########################################
    if msg['text'].split(' ',1)[0] == '/splot':
        bot.sendMessage(chat_id, 'Ok, processando o gráfico...')
        os.system("gnuplot -e '\
        set terminal png;\
        set output \""+str(chat_id)+"_"+msg['from']['first_name']+".png\";\
        set grid;\
        set isosamples 50;\
        "+str(add)+";\
        sp "+msg['text'].split(' ',1)[1]+"'")
        bot.sendPhoto(chat_id, open(str(chat_id)+"_"+msg['from']['first_name']+".png",'rb'))
##########################################
    if msg['text'].split(' ',1)[0] == '/heatmap':
        bot.sendMessage(chat_id, 'Ok, processando o gráfico...')
        os.system("gnuplot -e '\
        set terminal png;\
        set output \""+str(chat_id)+"_"+msg['from']['first_name']+".png\";\
        unset key;\
        set pm3d map;\
        set isosamples 100;\
        set samples 1000;\
        "+str(add)+";\
        sp "+msg['text'].split(' ',1)[1]+" w pm3d'")
        bot.sendPhoto(chat_id, open(str(chat_id)+"_"+msg['from']['first_name']+".png",'rb'))
##########################################

bot.message_loop(recebendoMsg)

while True:
    pass
