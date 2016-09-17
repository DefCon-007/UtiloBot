import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
import logging
from telegram.ext import MessageHandler, Filters
import urllib.request
import main_short
import os 
from threading import Thread
with open('./ACCESS_TOKEN', 'r') as f:
    token = f.readline().rstrip('\n')

def link_sender(bot , update ,file_local_path ):
	print ("Starting Thread")
	file_url = bot.getFile(update.message.document.file_id)['file_path']  #getting file download url 
	urllib.request.urlretrieve(file_url , "./{}".format(update.message.document.file_name))    # downloading file
	file_local_path = os.path.abspath("./{}".format(update.message.document.file_name))  #getting absolute path of the file 
	links = main_short.main(file_local_path)   #uploading and shorting the file
	bot.sendMessage(chat_id=update.message.chat_id, text="For the file {} \nDownload link : {}\nDeletion link : {}".format(update.message.document.file_name,links['down'],links['del']))
	os.remove(file_local_path)
def start(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")
def get_file () :
	bot.getFile(chat_id=update.message.chat_id , )
def tpp (bot,update) :
	bot.sendMessage(chat_id=update.message.chat_id, text="I am also so bored!!! SO what are you upto ???? ")
def documents(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text="I got {}\nI will just copy this file to my secure servers.\nI dont trust telegram file servers that much !!!!\nI will give you a deletion link in case you want your file deleted from my server\nBoth the download and upload link will be available for maximum 2 days".format(update.message.document.file_name))
	Thread(target = link_sender , args = (bot , update ,)).start()
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
