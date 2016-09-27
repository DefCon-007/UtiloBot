import telegram
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from telegram.ext import CommandHandler,CallbackQueryHandler,Updater,MessageHandler, Filters
import logging
import urllib.request
import main_short
import os
import time
from threading import Thread
from selenium import webdriver
import selenium.common.exceptions
import requests
from bs4 import BeautifulSoup
#from pyshorteners import Shortener
import bitly_api
import json
import Logger
logger = Logger.Logger(name='My_Logger')
with open('./ACCESS_TOKEN', 'r') as f:
	token = f.readline().rstrip('\n')
# with open('./GOOGLE_KEY', 'r') as f:
# 	google_api = f.readline().rstrip('\n')
with open('./BITLY_ACCESS_TOKEN', 'r') as f:
	bitly_token = f.readline().rstrip('\n')
def youtube_search (name,page) :
	a=0
	results = []
	while a<int(page):
		url="https://www.youtube.com/results?search_query="+name+"&page=" + str(a+1)
		logger.addLog (url)
		i=0
		while True :
			try :
				source_code=requests.get(url)  #getting page source
				break
			except requests.exceptions.ProxyError:
				logger.addLog("Got requests.exceptions.ProxyError in searching")
				if i >=3 :
					return 0
				i+=1
				time.sleep(2)
		text_source=source_code.text #converting it to text file
		soup=BeautifulSoup(text_source,'html.parser')  # making soup object
		for main_div in soup.findAll('div',{'class' : 'yt-lockup-content'}) :  #getting main div tag for the video
			video = {}
			flag =0
			for badges in main_div.findAll('div',{'class' : 'yt-lockup-badges'}) : #getting the badges (a check for channels and live videos)
				badge_ul = badges.find('ul')
				for badge_li in badge_ul.findAll('li') :
					badge_span = badge_li.find('span')
					if badge_span.text == "Channel"  or badge_span.text == "Live now" :
						flag =1 
						break
			if flag == 1 :
				continue
			for heading in main_div.findAll('h3',{'class' : 'yt-lockup-title '}) : #getting video name
				flag =0 
				for name_link in heading.findAll('a') :
					if name_link.get('href').find("list") != -1 :  #to get only the video links
						flag =1
						continue
					video['name'] = name_link.string  #getting name
					video['video_link'] = "https://www.youtube.com"+name_link.get('href')
				if flag == 1 :
					continue
				for duration in heading.findAll('span') :
					video['duration'] = duration.string[3:-1].replace('Duration: ' , "")  #getting video duration
			if flag == 1:
				continue
			for uploader_div in main_div.findAll('div',{'class' : 'yt-lockup-byline'}) :
				for uploader_a in uploader_div.findAll('a') :    
					video['uploader'] = uploader_a.string   #getting uploader name
					video['uploader_link'] = "https://www.youtube.com"+uploader_a.get('href')  #getting uploader channel's url
			for date_n_views_div in main_div.findAll('div',{'class' : 'yt-lockup-meta'}) :
				for date_n_views_ul in date_n_views_div.findAll('ul') :
					date_n_views_li = date_n_views_ul.findAll('li') 
					video['time'] = date_n_views_li[0].string
					video['views'] = date_n_views_li[1].string.replace(' views' ,"")
			for desc_div in main_div.findAll('div',{'class' : 'yt-lockup-description yt-ui-ellipsis yt-ui-ellipsis-2'}) :
				video['description'] = desc_div.text  #getting short description
			results.append(video)
		a+=1
	return results

def handelling_youtube_search(bot,update):
	query_list = update.message.text.split('-')
	try :
		page = int(query_list[1].replace(" ",""))
	except ValueError :
		bot.sendMessage(chat_id=update.message.chat_id , text= "Uh-ho you supplied <strong>{}</strong> which is not a proper page number. Please try again".format(query_list[1].replace(" ","")),parse_mode="HTML")
		return 0
	except IndexError :
		bot.sendMessage(chat_id=update.message.chat_id , text= "OMG !!! You forgot to enter the pages. Its ok I will look on the first page for you.")
		page = 1
	search_result = youtube_search(query_list[0] , page)
	if search_result == 0 :
		bot.sendMessage(chat_id=update.message.chat_id , text= "There is some connection problem with Youtube.Please try again")
		return 0
	sending_search_result(bot=bot , update=update , search_result=search_result , flag_search=1)
def sending_search_result(bot , update , search_result,flag_search=0 ,prev=0 , later=1,msg_id=0 ,chat_id=0):
	
	if prev != 0 :
		prev_text = "Previous"
	else : 
		prev_text = "Nothing More"
	if later != len(search_result) -1 :
		later_text = "Next" 
	else :
		later_text = "Nothing More" 
	message = ""
	i = 0
	index = prev
	while (i<2) :
		if 'description' not in search_result[index].keys() : #checking if description is present for the video 
			search_result[index]['description'] = " "
		message = message + '''
		<strong>{}. {}</strong>
		<i>{}</i>
		<b>Duration : </b>{}
		<b>Views : </b>{}
		<b>Uploaded : </b>{}
		<b>Uploader : </b><a href="{}">{}</a>
		<b>Video URL : </b> <a href='{}'>Link</a>
		'''.format( (index+1),
					search_result[index]['name'],
					search_result[index]['description'],
					search_result[index]['duration'],
					search_result[index]['views'],
					search_result[index]['time'],
					search_result[index]['uploader_link'],
					search_result[index]['uploader'],
					search_result[index]['video_link']
					)
		i = i+1
		index = index+1
	search_key = [{'text': prev_text , 'callback_data' : "ser_p{}_l{}".format(prev,later) } , {'text': later_text , 'callback_data' : "ser_l{}_p{}".format(later,prev) }]
	downlaod_button_1 = [{'text': "Download video no. {}".format(prev+1) , 'callback_data': "srdwn_{}".format(search_result[prev]['video_link'])}]
	downlaod_button_2 = [{'text': "Download video no. {}".format(prev+2), 'callback_data': "srdwn_{}".format(search_result[prev+1]['video_link'])}]
	results_keyboard = {'inline_keyboard': [search_key,downlaod_button_1,downlaod_button_2] }
	if flag_search == 1 : #this means this is the first time this function is called
		message_object = bot.sendMessage(chat_id=update.message.chat_id ,text = message , disable_web_page_preview=True , parse_mode="HTML",reply_markup = results_keyboard)
		res_json = {'msg_id' : message_object.message_id , "chat_id":update.message.chat_id, 'search_result':search_result}
		json.dump(res_json ,open("{}".format(update.message.chat_id) , "w") )
	else :
		try :
			bot.editMessageText(message_id=int(msg_id) , chat_id=int(chat_id),text = message , disable_web_page_preview=True , parse_mode="HTML",reply_markup = results_keyboard)
		except telegram.error.BadRequest as e :
			if e == "Bad Request: message is not modified" :
				pass
	#bot.sendMessage(chat_id=update.message.chat_id ,reply_markup = Inline_keyboard ,text = "Choose what you want to do")

def handelling_download_via_url(bot,update,url,flag=0,chat_id=0):
	logger.addLog ("Video download thread started")
	if flag == 0 :  #this means user used the download via url option
		chat_id = update.message.chat_id
		bot.sendMessage(chat_id=chat_id, text="Awesome !! I got the video link.. Just wait for few seconds !!")
		bot.sendMessage(chat_id=chat_id, text="<strong>NOTE : There are some problems with server right now so your video might not get downloaded. !!</strong>",parse_mode="HTML")
	main_json = youtube_download_via_url(url)   # ********* Add here check for wrong link ***************
	if main_json == 0 : #unable to open the video site
		bot.sendMessage(chat_id=chat_id,text="Sorry I was unable to download video due to some issues. Please try again later")
		return 0
	elif main_json == 2 : #video site opened but no links for download found
		bot.sendMessage(chat_id=chat_id,text="There are some problems with video you selected. Please choose a different video")
		return 0
	video_list = main_json['videos']
	logger.addLog ("I got the video links as follows : ")
	logger.addLog (video_list)
	#sending available quality
	button_list = []
	for video in video_list :
		button_list.append([{'text':video['ext'] + video["quality"] , 'callback_data': "vid_url" + video["short_url"]}])
	quality_keyboard={'inline_keyboard':button_list}
	if flag == 0 :
		bot.sendMessage(chat_id=chat_id ,reply_markup = quality_keyboard ,text = "Choose the quality for {}".format(main_json['name']))
	else :
		bot.sendMessage(chat_id=chat_id ,reply_markup = quality_keyboard ,text = "Choose the quality for {}".format(main_json['name']))
def youtube_download_via_url(base_url):
	logger.addLog ("Starting web driver")
	driver = webdriver.PhantomJS(service_args=['--load-images=false'])
	logger.addLog ("Webdriver started")
	bitly = bitly_api.Connection(access_token=bitly_token)
	base_url = base_url.replace("youtube" , "getlinkyoutube")  #changing supplied youtube url to redirect it to youtubemultidownload
	base_url = base_url.replace("https" , "http")
	logger.addLog (base_url)
	driver.get(base_url)
	logger.addLog (driver.current_url)
	i=0
	while True :
		try:
			name = driver.find_element_by_xpath("//h1[@class='title-video']").text
			break
		except selenium.common.exceptions.NoSuchElementException:
			if i ==3 :
				driver.get(base_url)
				logger.addLog("opening the url again")
			elif i >=4 :
				logger.addLog("Stoping download due to NoElementEception")
				driver.quit()
				return 0

			time.sleep(1)
			logger.addLog (driver.current_url)
			logger.addLog ("wait")
	logger.addLog ("Getting detalis for {}".format(name))
	# quality_list = driver.find_element_by_xpath("//*[@id='Download_Quality']/ul").find_elements_by_tag_name('li')
	videos = []
	while True :
		for qua_div in driver.find_elements_by_xpath("//div[@class='col-md-4 downbuttonbox']"):
			anchor = qua_div.find_element_by_tag_name('a')
			url = anchor.get_attribute('href')  #getting video url
			url = url.replace("%20-%20[www.getlinkyoutube.com]","")  #removing getlinkyoutube from file name
			span =qua_div.find_element_by_tag_name('span')
			quality = span.text  # getting video url
			if "Mp4" in quality :
				videos.append({"ext":"Mp4 : " , "quality" : quality[4:] , "short_url" : bitly.shorten(url)['url'] })
			if "3gp" in quality :
				videos.append({"ext":"3gp : " , "quality" : quality[4:] , "short_url" : bitly.shorten(url)['url'] })
			if "m4a" in quality :
				videos.append({"ext":"m4a : " , "quality" : quality[4:], "short_url" : bitly.shorten(url)['url'] })

			# videos.append({"ext":"Mp4 : " , "quality" : quality[5:] , "short_url" : bitly.shorten(url)['url'] })
			# vid_json['quality'] = quality[5:]
			# vid_json['url'] = url
			# video.append(vid_json)
	#		videos.append({"ext":"Mp4 : " , "quality" : res.text , "short_url" : bitly.shorten(res.get_attribute('href'))['url'] })
	#getting all the mp4's
	#logger.addLog ("For {}".format(quality_list[0].text))
	# resoulution = quality_list[1].find_elements_by_tag_name('a')
	# for res in resoulution :
	# 	if res.get_attribute('class') == "btn btn-success" :
	# 		continue
	# 	# shorten_url = bitly.shorten(res.get_attribute('href'))['url']
	# 	# logger.addLog (shorten_url)
	# 	videos.append({"ext":"Mp4 : " , "quality" : res.text , "short_url" : bitly.shorten(res.get_attribute('href'))['url'] })
	# 	#logger.addLog (res.get_attribute('href'))
	# #getting all the 3gp's
	# #logger.addLog ("For {}".format(quality_list[-2].text))
	# resoulution = quality_list[-1].find_elements_by_tag_name('a')
	# #shortener = Shortener('Google', api_key=google_api)  #initialising link shortener
	# #shortener = Shortener('Tinyurl')
	# for res in resoulution :
	# 	# shorten_url = bitly.shorten(res.get_attribute('href'))['url']
	# 	# logger.addLog (shorten_url)
	# 	videos.append({"ext":"3gp : " , "quality" : res.text , "short_url" : bitly.shorten(res.get_attribute('href'))['url'] })
		if i >= 3:
			logger.addLog("Unable to get video links")
			driver.quit()
			return 2
		if len(videos) == 0 :
			time.sleep(1)
			i+=1
		else :
			break
	you_json = {'name' : name , 'videos' : videos}
	driver.quit()
	return you_json

# def send_video(chat_id , file_name,bot):
# 	full_path = os.path.abspath("./{}".format(file_name))
# 	logger.addLog(full_path)
# 	bot.sendDocument(chat_id=chat_id , document = full_path)
def link_sender(bot,chat_id,file_id,file_name,flag="doc"):
	logger.addLog ("Starting file download Thread")
	file_url = bot.getFile(file_id)['file_path']  #getting file download url
	if flag == "aud" :
		#for audio
		file_name = file_name + ".{}".format(file_url.split('/')[-1].split('.')[-1])  #getting audio extensior

	if flag == "img" or flag=="vid" or flag == "voc":
		file_name = file_name + file_url.split('/')[-1]
		#for image
		sf = 0
	i=0
	logger.addLog ("Concerned file : {}".format(file_name) )
	while True :
		try :
			logger.addLog("downloading File")
			urllib.request.urlretrieve(file_url , "./{}".format(file_name))    # downloading file

			break
		except urllib.error.URLError :
			if i>=2 :
				bot.sendMessage(chat_id=chat_id,text="I was unable to download the file. Please try again later")
				return 0
			i+=1
			time.sleep(2)
			logger.addLog("File download error : urllib.error.URLError")

	logger.addLog("file downloaded")
	file_local_path = os.path.abspath("./{}".format(file_name))  #getting absolute path of the file
	links = main_short.main(file_local_path)   #uploading and shortening the file
	if links == 0 :
		links = main_short.main(file_local_path)   #trying for uploading and shorting the file again
		if links == 0 :
			logger.addLog("Unable to download file: replying with error msg Return Code 0")
			bot.sendMessage(chat_id=chat_id, text="I was unable to process {}. Please try again later".format(file_name))
			os.remove(file_local_path)
			return 0
	elif links == 3 :
		links = main_short.main(file_local_path)  # trying for uploading and shorting the file again
		if links == 3 or links == 0 :
			logger.addLog("Unable to download file: replying with error msg return code 3")
			bot.sendMessage(chat_id=chat_id,text="I was unable to process {}. Please try again later".format(file_name))
			os.remove(file_local_path)
			return 0
	bot.sendMessage(chat_id=chat_id, text="For the file {} \nDownload link : {}\nDeletion link : {}".format(file_name,links['down'],links['del']) , disable_web_page_preview=True)
	os.remove(file_local_path)
def start(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")
# def get_file () :
# 	bot.getFile(chat_id=update.message.chat_id , )
def documents(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text="I got {}\nI will just copy this file to my secure servers.\nI dont trust telegram file servers that much !!!!\nI will give you a deletion link in case you want your file deleted from my server\nBoth the download and upload link will be available for maximum 2 days".format(update.message.document.file_name))
	logger.addLog("Starting thread for document")
	Thread(target = link_sender , args = (bot , update.message.chat_id ,update.message.document.file_id, update.message.document.file_name)).start()
	#logger.addLog (bot.getFile(update.message.document.file_id))
def file_audio(bot,update):
	file_id = update.message.audio.file_id
	title = update.message.audio.title
	bot.sendMessage(chat_id=update.message.chat_id,text="I got {}\nI will just copy this file to my secure servers.\nI dont trust telegram file servers that much !!!!\nI will give you a deletion link in case you want your file deleted from my server\nBoth the download and upload link will be available for maximum 2 days".format(title))
	#print(update.message.audio.duration)
	#print (update.message.audio.mime_type)
	#print (bot.getFile(update.message.audio.file_id)['file_path'])
	logger.addLog("Starting thread for audio")
	Thread(target=link_sender, args=(bot, update.message.chat_id, file_id, title,"aud")).start()
def file_video(bot,update):
	file_id = update.message.video.file_id
	bot.sendMessage(chat_id=update.message.chat_id,text="I got the video\nI will just copy this file to my secure servers.\nI dont trust telegram file servers that much !!!!\nI will give you a deletion link in case you want your file deleted from my server\nBoth the download and upload link will be available for maximum 2 days")
	logger.addLog("Starting thread for video")
	Thread(target=link_sender, args=(bot, update.message.chat_id, file_id, "vid_", "vid")).start()
def file_voice(bot,update):
	file_id = update.message.voice.file_id
	bot.sendMessage(chat_id=update.message.chat_id,text="I got the your voice clip\nI will just copy this file to my secure servers.\nI dont trust telegram file servers that much !!!!\nI will give you a deletion link in case you want your file deleted from my server\nBoth the download and upload link will be available for maximum 2 days")
	logger.addLog("Starting thread for voice")
	Thread(target=link_sender, args=(bot, update.message.chat_id, file_id, "voice_", "voc")).start()
def file_image(bot,update) :
	bot.sendMessage(chat_id=update.message.chat_id,text="I got the image\nI will just copy this file to my secure servers.\nI dont trust telegram file servers that much !!!!\nI will give you a deletion link in case you want your file deleted from my server\nBoth the download and upload link will be available for maximum 2 days")
	file_id = update.message.photo[0]['file_id']
	logger.addLog("Starting thread for image")
	Thread(target=link_sender, args=(bot, update.message.chat_id, file_id, "img_","img")).start()


# photo_selector_button = []
	# for photo in update.message.photo :
	# 	file_id = photo['file_id']
	# 	file_url = bot.getFile(file_id)['file_path']  #getting file url to get a file name
	# 	file_name = file_url.split('/')[-1]
	# 	#photo_selector_button.append([{'text':"Size {} bytes".format(photo['file_size']) , 'callback_data':'downpic_{}_{}_{}'.format(update.message.chat_id,file_id,file_name)}])
	# 	photo_selector_button.append([{'text': "Size {} bytes".format(photo['file_size']),'callback_data': 'downpic_{}_{}_{}'.format("a", file_id,"a")}])
	# photo_selector_keyboard = {'inline_keyboard' : photo_selector_button}
	# bot.sendMessage(chat_id=update.message.chat_id, reply_markup=photo_selector_keyboard,text="For which photo you want links : " )
	# print (update.message.photo[0])
	# file_id = update.message.photo[0]['file_id']
	# file_url = bot.getFile(file_id)['file_path']
	# file_name = file_url.split('/')[-1]
	# print (file_url)
	# urllib.request.urlretrieve(file_url, "./{}".format(file_name))
def youtube_keyboard(bot , update):
	#keyBut = [{'text': 'Search YouTube'} , {'text' :'Download video via url'}]
	#replyKeyboardMakeup = {'keyboard': [keyBut], 'resize_keyboard': True, 'one_time_keyboard': True}
	Iniline_key = [{'text': "Search YouTube" , 'callback_data' : '1_ser'} , {'text': "Download video via URL" , 'callback_data' : '2_dwn'}]
	Inline_keyboard = {'inline_keyboard': [Iniline_key] }
	message_obj = bot.sendMessage(chat_id=update.message.chat_id ,reply_markup = Inline_keyboard ,text = "Choose what you want to do")
def inline_query(bot ,update) :
	global Flag
	#bot.answerCallbackQuery(text = "HII")
	#logger.addLog (update.callback_query)
	if update.callback_query['data'] == "1_ser" :  #this means user selected the search option 
		logger.addLog("Search")
		bot.sendMessage(chat_id=update.callback_query['message']['chat']['id'] ,text="Send whatever you want to search on YouTube and after '-' no. of pages you want to search (e.g. : Selena Gomez - 2)")
		Flag = "1_ser"
	elif update.callback_query['data'] == "2_dwn" :  #this means user selected the download via url option
		bot.sendMessage(chat_id=update.callback_query['message']['chat']['id'] ,text="Send the video url (e.g. : https://www.youtube.com/watch?v=abcxyz)")
		Flag = "2_dwn"
		#download_video_via_url()
	elif update.callback_query['data'].startswith('vid_url'):  #sending the short url of the specified quality
		video_url = update.callback_query['data'][7:]
		bot.sendMessage(chat_id=update.callback_query['message']['chat']['id'] ,text=video_url ,disable_web_page_preview=True)
	elif update.callback_query['data'].startswith('ser'):  #this is for search navigation of the youtube results
		text= update.callback_query['data'].split('_')[1]
		text_other = update.callback_query['data'].split('_')[2]
		main_json = json.load( open("./{}".format(update.callback_query['message']['chat']['id']),"r"))
		if text[0] == 'p' :
			prev = int(text[1:])
			if prev == 0 :
				sending_search_result(bot,update,main_json['search_result'],prev=prev ,later=prev+1,msg_id=main_json['msg_id'] , chat_id=main_json['chat_id'])
			else :
				prev = prev-2
				later = prev + 1
				sending_search_result(bot,update,main_json['search_result'],prev=prev,later=later,msg_id=main_json['msg_id'],chat_id=main_json['chat_id'])
		else :
			later = int(text[1:])
			#prev = int(text_other[1:])
			if later >= len(main_json['search_result']) - 1 :
				later = len(main_json['search_result']) - 1
				sending_search_result(bot,update,main_json['search_result'],prev=later-1 ,later=later, msg_id=main_json['msg_id'],chat_id=main_json['chat_id'])
			else :
				later = later+2
				prev = later -1 
				sending_search_result(bot,update,main_json['search_result'],prev=prev,later=later,msg_id=main_json['msg_id'],chat_id=main_json['chat_id'])	
	elif update.callback_query['data'].startswith('srdwn'):  #user selected download after searching
		bot.sendMessage(chat_id=update.callback_query['message']['chat']['id'],text="Downloading please wait !!! This might take some time but believe me waiting is worth it !!")
		bot.sendMessage(chat_id=update.callback_query['message']['chat']['id'],text="<strong> NOTE : There are some problems with server right now so your video might not get downloaded. !!</strong>",parse_mode="HTML")
		down_link = update.callback_query['data'].split('_')[1]	
		Thread(target = handelling_download_via_url , args = (bot,update,down_link,1,update.callback_query['message']['chat']['id'])).start()
def echo(bot, update):
	global Flag
	#if update.message.text == "Download video via url" :
	if Flag == "2_dwn" :  #this means user selected the download via url option and sent the url
		logger.addLog ("Got the video link")
		Flag = None
		Thread(target = handelling_download_via_url , args = (bot,update,update.message.text,)).start()
	elif Flag == "1_ser" :
		logger.addLog ("Got the search query")
		Flag = None
		Thread(target = handelling_youtube_search , args = (bot , update ,)).start()
	else :
		bot.sendMessage(chat_id=update.message.chat_id, text=update.message.text)
	# ne = bot.editMessageText(message_id=int(message_obj.message_id) , chat_id=update.message.chat_id,text="This is updated message")
	# logger.addLog (ne.message_id)
def echo_sticker(bot,update):
	bot.sendSticker(chat_id=update.message.chat_id,sticker=update.message.sticker.file_id)
def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized:
    	logger.addLog (1)
        # remove update.message.chat_id from conversation list
    except BadRequest:
    	logger.addLog (2)
        # handle malformed requests - read more below!
    except TimedOut:
    	logger.addLog (3)
        # handle slow connection problems
    except NetworkError:
    	logger.addLog (4)
        # handle other connection problems
    except ChatMigrated as e:
    	logger.addLog (5)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
    	logger.addLog (6)
        # handle all other telegram related errors

Flag = None
you_obj = None
updater = Updater(token=token)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
#creating handlers
start_handler = CommandHandler('start', start)
youtube_handler = CommandHandler('youtube' , youtube_keyboard)
inline_query_handler = CallbackQueryHandler(inline_query)
echo_handler = MessageHandler([Filters.text], echo)
doc_handler = MessageHandler([Filters.document], documents)
img_handler = MessageHandler([Filters.photo],file_image)
audio_handler = MessageHandler([Filters.audio],file_audio)
video_handler = MessageHandler([Filters.video],file_video)
voice_handler = MessageHandler([Filters.voice],file_voice)
echo_sticker_handler = MessageHandler([Filters.sticker],echo_sticker)
#adding handlers to dispatcher
dispatcher.add_handler(start_handler)
dispatcher.add_handler(youtube_handler)
dispatcher.add_handler(inline_query_handler)
dispatcher.add_handler(echo_handler)
dispatcher.add_error_handler(error_callback)
dispatcher.add_handler(doc_handler)
dispatcher.add_handler(img_handler)
dispatcher.add_handler(audio_handler)
dispatcher.add_handler(video_handler)
dispatcher.add_handler(voice_handler)
dispatcher.add_handler(echo_sticker_handler)
updater.start_polling()
