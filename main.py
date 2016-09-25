import telegram
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from telegram.ext import CommandHandler,CallbackQueryHandler,Updater,MessageHandler, Filters
import logging
import urllib.request
import main_short
import os 
from threading import Thread
from selenium import webdriver
import selenium.common.exceptions
import requests
from bs4 import BeautifulSoup
#from pyshorteners import Shortener
import bitly_api
import json
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
		print (url)
		try :
			source_code=requests.get(url)  #getting page source
		except requests.exceptions.ProxyError:
			return 0
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
					print (video['name'])
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
	print ("Video download thread started")
	if flag == 0 :
		bot.sendMessage(chat_id=update.message.chat_id,text="Awesome !! I got the video link.. Just wait few seconds !!")
	main_json = youtube_download_via_url(url)   # ********* Add here check for wrong link ***************
	video_list = main_json['videos']
	print ("I got the video links as follows : ")
	print (video_list)
	#sending available quality
	button_list = []
	for video in video_list :
		button_list.append([{'text':video['ext'] + video["quality"] , 'callback_data': "vid_url" + video["short_url"]}])
	quality_keyboard={'inline_keyboard':button_list}
	if flag == 0 :
		bot.sendMessage(chat_id=update.message.chat_id ,reply_markup = quality_keyboard ,text = "Choose the quality")
	else :
		bot.sendMessage(chat_id=chat_id ,reply_markup = quality_keyboard ,text = "Choose the quality for {}".format(main_json['name']))
def youtube_download_via_url(base_url):
	print ("Starting web driver")
	driver = webdriver.PhantomJS(service_args=['--load-images=false'])
	print ("Webdriver started")
	bitly = bitly_api.Connection(access_token=bitly_token)
	base_url = base_url.replace("youtube" , "getlinkyoutube")  #changing supplied youtube url to redirect it to youtubemultidownload
	base_url = base_url.replace("https" , "http")
	print (base_url)
	driver.get(base_url)
	print (driver.current_url)
	while True :
		try:
			name = driver.find_element_by_xpath("//h1[@class='title-video']").text
			break
		except selenium.common.exceptions.NoSuchElementException:
			print ("wait")
	print ("Getting detalis for {}".format(name))
	# quality_list = driver.find_element_by_xpath("//*[@id='Download_Quality']/ul").find_elements_by_tag_name('li')
	videos = []
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
	#print ("For {}".format(quality_list[0].text))
	# resoulution = quality_list[1].find_elements_by_tag_name('a')
	# for res in resoulution :
	# 	if res.get_attribute('class') == "btn btn-success" :
	# 		continue
	# 	# shorten_url = bitly.shorten(res.get_attribute('href'))['url']
	# 	# print (shorten_url)
	# 	videos.append({"ext":"Mp4 : " , "quality" : res.text , "short_url" : bitly.shorten(res.get_attribute('href'))['url'] })
	# 	#print (res.get_attribute('href'))
	# #getting all the 3gp's
	# #print ("For {}".format(quality_list[-2].text))
	# resoulution = quality_list[-1].find_elements_by_tag_name('a')
	# #shortener = Shortener('Google', api_key=google_api)  #initialising link shortener
	# #shortener = Shortener('Tinyurl')
	# for res in resoulution :
	# 	# shorten_url = bitly.shorten(res.get_attribute('href'))['url']
	# 	# print (shorten_url)
	# 	videos.append({"ext":"3gp : " , "quality" : res.text , "short_url" : bitly.shorten(res.get_attribute('href'))['url'] })
	you_json = {'name' : name , 'videos' : videos}
	driver.quit()
	return you_json 

# def send_video(chat_id , file_name,bot):
# 	full_path = os.path.abspath("./{}".format(file_name))
# 	print(full_path)
# 	bot.sendDocument(chat_id=chat_id , document = full_path)
def link_sender(bot , update):
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
	Thread(target = link_sender , args = (bot , update )).start()
	#print (bot.getFile(update.message.document.file_id))
def youtube_keyboard(bot , update):
	#keyBut = [{'text': 'Search YouTube'} , {'text' :'Download video via url'}]
	#replyKeyboardMakeup = {'keyboard': [keyBut], 'resize_keyboard': True, 'one_time_keyboard': True}
	Iniline_key = [{'text': "Search YouTube" , 'callback_data' : '1_ser'} , {'text': "Download video via URL" , 'callback_data' : '2_dwn'}]
	Inline_keyboard = {'inline_keyboard': [Iniline_key] }
	message_obj = bot.sendMessage(chat_id=update.message.chat_id ,reply_markup = Inline_keyboard ,text = "Choose what you want to do")
def inline_query(bot ,update) :
	global Flag
	#bot.answerCallbackQuery(text = "HII")
	#print (update.callback_query)
	if update.callback_query['data'] == "1_ser" :  #this means user selected the search option 
		print("Search")
		bot.sendMessage(chat_id=update.callback_query['message']['chat']['id'] ,text="Send whatever you want to search on YouTube and after '-' no. of pages you want to search (e.g. : Selena Gomez - 2)")
		Flag = "1_ser"
	elif update.callback_query['data'] == "2_dwn" :  #this means user selected the download via url option
		bot.sendMessage(chat_id=update.callback_query['message']['chat']['id'] ,text="Send the video url (e.g. : https://www.youtube.com/watch?v=abcxyz)")
		Flag = "2_dwn"
		#download_video_via_url()
	elif update.callback_query['data'].startswith('vid_url'):  #sending the short url of the specified quality
		video_url = update.callback_query['data'][7:]
		bot.sendMessage(chat_id=update.callback_query['message']['chat']['id'] ,text=video_url)
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
		bot.sendMessage(chat_id=update.callback_query['message']['chat']['id'] ,text="Downloading please wait !!!")
		down_link = update.callback_query['data'].split('_')[1]	
		Thread(target = handelling_download_via_url , args = (bot,update,down_link,1,update.callback_query['message']['chat']['id'])).start()
def echo(bot, update):
	global Flag
	#if update.message.text == "Download video via url" :
	if Flag == "2_dwn" :  #this means user selected the download via url option and sent the url
		print ("Got the video link")
		Flag = None
		Thread(target = handelling_download_via_url , args = (bot,update,update.message.text,)).start()
	elif Flag == "1_ser" :
		print ("Got the search query")
		Flag = None
		Thread(target = handelling_youtube_search , args = (bot , update ,)).start()
	else :
		bot.sendMessage(chat_id=update.message.chat_id, text=update.message.text)
	# ne = bot.editMessageText(message_id=int(message_obj.message_id) , chat_id=update.message.chat_id,text="This is updated message")
	# print (ne.message_id)
def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized:
    	print (1)
        # remove update.message.chat_id from conversation list
    except BadRequest:
    	print (2)
        # handle malformed requests - read more below!
    except TimedOut:
    	print (3)
        # handle slow connection problems
    except NetworkError:
    	print (4)
        # handle other connection problems
    except ChatMigrated as e:
    	print (5)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
    	print (6)
        # handle all other telegram related errors

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
dispatcher.add_error_handler(error_callback)
doc_handler = MessageHandler([Filters.document], documents)
dispatcher.add_handler(doc_handler)
updater.start_polling()
