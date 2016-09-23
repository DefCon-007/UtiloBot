import telegram
from telegram.ext import CommandHandler,CallbackQueryHandler,Updater,MessageHandler, Filters
import logging
import urllib.request
import main_short
import os 
from threading import Thread
from selenium import webdriver
import selenium.common.exceptions
#from pyshorteners import Shortener
import bitly_api
with open('./ACCESS_TOKEN', 'r') as f:
	token = f.readline().rstrip('\n')
# with open('./GOOGLE_KEY', 'r') as f:
# 	google_api = f.readline().rstrip('\n')
with open('./BITLY_ACCESS_TOKEN', 'r') as f:
	bitly_token = f.readline().rstrip('\n')
def youtube_download_via_url(url,):
	driver = webdriver.PhantomJS()
	bitly = bitly_api.Connection(access_token=bitly_token)
	url = url.replace("youtube" , "youtube1s")  #changing supplied youtube url to redirect it to youtubemultidownload
	driver.get(url)

	while True :
		try: 
			name = driver.find_element_by_xpath("//div[@id='Download_Image']").find_element_by_tag_name('h5').text  #gettting the name of the video
			break
		except selenium.common.exceptions.NoSuchElementException:
			pass
	quality_list = driver.find_element_by_xpath("//*[@id='Download_Quality']/ul").find_elements_by_tag_name('li')
#	print (len(quality_list))
	videos = []
	#getting all the mp4's
	#print ("For {}".format(quality_list[0].text))
	resoulution = quality_list[1].find_elements_by_tag_name('a')
	for res in resoulution :
		if res.get_attribute('class') == "btn btn-success" :
			continue
		# shorten_url = bitly.shorten(res.get_attribute('href'))['url']
		# print (shorten_url)
		videos.append({"ext":"Mp4 : " , "quality" : res.text , "short_url" : bitly.shorten(res.get_attribute('href'))['url'] })
		#print (res.get_attribute('href'))
	#getting all the 3gp's
	#print ("For {}".format(quality_list[-2].text))
	resoulution = quality_list[-1].find_elements_by_tag_name('a')
	#shortener = Shortener('Google', api_key=google_api)  #initialising link shortener
	#shortener = Shortener('Tinyurl')
	for res in resoulution :
		# shorten_url = bitly.shorten(res.get_attribute('href'))['url']
		# print (shorten_url)
		videos.append({"ext":"3gp : " , "quality" : res.text , "short_url" : bitly.shorten(res.get_attribute('href'))['url'] })
	return videos 

def send_video(chat_id , file_name,bot):
	full_path = os.path.abspath("./{}".format(file_name))
	print(full_path)
	bot.sendDocument(chat_id=chat_id , document = full_path)
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
def documents(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text="I got {}\nI will just copy this file to my secure servers.\nI dont trust telegram file servers that much !!!!\nI will give you a deletion link in case you want your file deleted from my server\nBoth the download and upload link will be available for maximum 2 days".format(update.message.document.file_name))
	Thread(target = link_sender , args = (bot , update ,)).start()
	#print (bot.getFile(update.message.document.file_id))
def youtube_keyboard(bot , update):
	#keyBut = [{'text': 'Search YouTube'} , {'text' :'Download video via url'}]
	#replyKeyboardMakeup = {'keyboard': [keyBut], 'resize_keyboard': True, 'one_time_keyboard': True}
	Iniline_key = [{'text': "Search YouTube" , 'callback_data' : '1_ser'} , {'text': "Download video via URL" , 'callback_data' : '2_dwn'}]
	Inline_keyboard = {'inline_keyboard': [Iniline_key] }
	bot.sendMessage(chat_id=update.message.chat_id ,reply_markup = Inline_keyboard ,text = "Choose what you want to do")
def inline_query(bot ,update) :
	global Flag
	#bot.answerCallbackQuery(text = "HII")
	#print (update.callback_query)
	if update.callback_query['data'] == "1_ser" :
		print("Search")
	elif update.callback_query['data'] == "2_dwn" :
		bot.sendMessage(chat_id=update.callback_query['message']['chat']['id'] ,text="Send the video url (e.g. : https://www.youtube.com/watch?v=abcxyz)")
		Flag = "2_dwn"
		#download_video_via_url()
	elif update.callback_query['data'].startswith('vid_url'):  #sending the short url of the specified quality
		video_url = update.callback_query['data'][7:]
		bot.sendMessage(chat_id=update.callback_query['message']['chat']['id'] ,text=video_url)
def echo(bot, update):
	global Flag
	#if update.message.text == "Download video via url" :
	if Flag == "2_dwn" :
		print ("Got the video link")
		bot.sendMessage(chat_id=update.message.chat_id,text="Awesome !! I got the video link.. Just wait few seconds !!")
		video_list = youtube_download_via_url(update.message.text)   # ********* Add here check for wrong link ***************
		#sending available quality
		button_list = []
		for video in video_list :
			button_list.append([{'text':video['ext'] + video["quality"] , 'callback_data': "vid_url" + video["short_url"]}])
		quality_keyboard={'inline_keyboard':button_list}
		bot.sendMessage(chat_id=update.message.chat_id ,reply_markup = quality_keyboard ,text = "Choose the quality")
		Flag = None
	else :
		bot.sendMessage(chat_id=update.message.chat_id, text=update.message.text)
Flag = None
you_obj = None
updater = Updater(token=token)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
start_handler = CommandHandler('start', start)
youtube_handler = CommandHandler('youtube' , youtube_keyboard)
inline_query_handler = CallbackQueryHandler(inline_query)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(youtube_handler)
dispatcher.add_handler(inline_query_handler)
echo_handler = MessageHandler([Filters.text], echo)
dispatcher.add_handler(echo_handler)

doc_handler = MessageHandler([Filters.document], documents)
dispatcher.add_handler(doc_handler)
updater.start_polling()
