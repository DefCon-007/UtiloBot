import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
import logging
from telegram.ext import MessageHandler, Filters
import urllib.request
import main_short
import os 
with open('./ACCESS_TOKEN', 'r') as f:
    token = f.readline().rstrip('\n')
def start(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")
def get_file () :
	bot.getFile(chat_id=update.message.chat_id , )
def tpp (bot,update) :
	bot.sendMessage(chat_id=update.message.chat_id, text="I am also so bored!!! SO what are you upto ???? ")
def documents(bot, update):
	#Downloading file 
	file_url = bot.getFile(update.message.document.file_id)['file_path']
	urllib.request.urlretrieve(file_url , "./files/{}".format(update.message.document.file_name))
	file_local_path = os.path.abspath("./files/{}".format(update.message.document.file_name))
	bot.sendMessage(chat_id=update.message.chat_id, text="I got the file\nLet me just upload it to my server first.\nI dont trust telegram file servers that much !!!!\nI will give you a deletion link in case you want your file deleted from expire.com server")
	links = main_short.main(file_local_path)   #uploading and shorting the file
	bot.sendMessage(chat_id=update.message.chat_id, text="For the file {} \nDownload link : {}\nDeletion link : {}".format(update.message.document.file_name,links['down'],links['del']))
	os.remove(file_local_path)
	#print (bot.getFile(update.message.document.file_id))
updater = Updater(token=token)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
start_handler = CommandHandler('start', start)
new_handler = CommandHandler('tp', tpp)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(new_handler)

def echo(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=update.message.text)

echo_handler = MessageHandler([Filters.text], echo)
dispatcher.add_handler(echo_handler)

doc_handler = MessageHandler([Filters.document], documents)
dispatcher.add_handler(doc_handler)
updater.start_polling()
