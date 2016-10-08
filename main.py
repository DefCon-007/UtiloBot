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
import bitly_api
import json
import Logger
import fb_reg
import twitter_reg
import tweet_checker
import fb_main
import sys
import html
import sendEmail
from random import randint  #to get a random integer
logger = Logger.Logger(name='My_Logger')
with open('./ACCESS_TOKEN', 'r') as f:
	token = f.readline().rstrip('\n')
# with open('./GOOGLE_KEY', 'r') as f:
# 	google_api = f.readline().rstrip('\n')
with open('./BITLY_ACCESS_TOKEN', 'r') as f:
	bitly_token = f.readline().rstrip('\n')

#send the proper inline keyboard when user sends /youtube
def youtube_keyboard(bot , update):
	#keyBut = [{'text': 'Search YouTube'} , {'text' :'Download video via url'}]
	#replyKeyboardMakeup = {'keyboard': [keyBut], 'resize_keyboard': True, 'one_time_keyboard': True}
	Iniline_key = [{'text': "Search YouTube" , 'callback_data' : '1_ser'} , {'text': "Download video via URL" , 'callback_data' : '2_dwn'}]
	Inline_keyboard = {'inline_keyboard': [Iniline_key] }
	message_obj = bot.sendMessage(chat_id=update.message.chat_id ,reply_markup = Inline_keyboard ,text = "Choose what you want to do")	
#function that handles the youtube search i.e. open it in a new thread
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
#Function that searches given query on youtube
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
#this function sends the search results to the user
def sending_search_result(bot , update , search_result,flag_search=0 ,prev=0 , later=1,msg_id=0 ,chat_id=0):
	
	if prev != 0 :
		prev_text = "Previous"
	else : 
		prev_text = "Nothing More"
	if later < len(search_result) -1 :
		later_text = "Next" 
	else :
		later_text = "Nothing More" 
	message = ""
	i = 0
	index = prev
	while (i<2) :
		try :
			if 'description' not in search_result[index].keys() : #checking if description is present for the video
				search_result[index]['description'] = " "
		except IndexError:
			return 0
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
#this function downloadls youtube video with the given url
def youtube_download_via_url(base_url):
	logger.addLog ("Starting web driver")
	driver = webdriver.PhantomJS(service_args=['--load-images=false'])
	logger.addLog ("Webdriver started")
	bitly = bitly_api.Connection(access_token=bitly_token)
	url_error = False
	if base_url.find("http") < 0 and base_url.find("youtu") >= 0:
		base_url = "http://" + base_url
	else:
		url_error = True
	if base_url.find("://youtu.be/") > 3:
		base_url = base_url.replace("youtu.be/", "getlinkyoutube.com/watch?v=")
	elif base_url.find("youtube.com/watch") > 6:
		base_url = base_url.replace("youtube" , "getlinkyoutube")  #changing supplied youtube url to redirect it to youtubemultidownload
	else:
		url_error = True
	if url_error:
		logger.addLog("Incorrect URL provided: " + base_url)
		bot.sendMessage(chat_id=chat_id, text="Sorry, I can't recognize your link T_T")
		return 0
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
			i+=1
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
#this function handles the downloading of youtube videos via URL
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
#start of file handling functions, These functions return the file object of the supplied file
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
	bot.sendMessage(chat_id=update.message.chat_id,text="I got your voice clip\nI will just copy this file to my secure servers.\nI dont trust telegram file servers that much !!!!\nI will give you a deletion link in case you want your file deleted from my server\nBoth the download and upload link will be available for maximum 2 days")
	logger.addLog("Starting thread for voice")
	Thread(target=link_sender, args=(bot, update.message.chat_id, file_id, "voice_", "voc")).start()
def file_image(bot,update) :
	bot.sendMessage(chat_id=update.message.chat_id,text="I got the image\nI will just copy this file to my secure servers.\nI dont trust telegram file servers that much !!!!\nI will give you a deletion link in case you want your file deleted from my server\nBoth the download and upload link will be available for maximum 2 days")
	file_id = update.message.photo[0]['file_id']
	logger.addLog("Starting thread for image")
	Thread(target=link_sender, args=(bot, update.message.chat_id, file_id, "img_","img")).start()
#end of file handling fuctions
#this functions download,uploads and send back the short url to the supplied file
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
#main function which run when /facebook is sent
def facebook_start(bot,update) :
	global Flag
	bot.sendMessage(chat_id=update.message.chat_id , text="Please send the id(s) of the facebook page(s) you wish to subscribe.")
	Flag = "fb_reg"
#this functions is lauched from main in a thread to scrape facebook pages
def facebook_sender_handler(bot,logger):
	while True :
		logger.addLog('Starting facebook scraping',"Facebook")
		fb_main.main(bot,logger)
		logger.addLog("facebook Going to sleep","Facebook") 
		time.sleep(600)	
#main function which runs when /twitter is sent
def twitter_start(bot,update) :
	global Flag 
	bot.sendMessage(chat_id=update.message.chat_id , text="Please send the handle(s) of the twitter account(s) you wish to subscribe.")
	Flag = "twitter_reg"	
#this function is launched from main to scrape twitter handles 
def twitter_sender_helper(bot ,logger) :
	while True :
		logger.addLog('Starting twitter scraping',"Twitter")
		tweet_checker.main(bot,logger)
		logger.addLog("Twitter Going to sleep","Twitter") 
		time.sleep(600)	
#this function gets the facebook and twitter subscription
def user_subs_fb_twitter(bot,update):
	try : 
		fb_users_data = json.load(open('FB/users.json','r'))
		fb_flag = False
		for fb_user in fb_users_data :
			if fb_user['chat_id'] == update.message.chat_id :
				subs_pages_list = fb_user['page']
				fb_flag = True
				break
	except FileNotFoundError :
		logger.addLog("Unable to find users.json")
	except Exception as e:
		logger.addLog("While opening fb users got error : {}".format(e))
	try :
		twitter_user_data = json.load(open('Twitter/user_data.json','r'))
		tw_flag =False 
		for user in twitter_user_data :
			if user['chat_id'] == update.message.chat_id :
				twitter_subs_handle_list = user['handles']
				tw_flag = True 
				break
	except FileNotFoundError :
		logger.addLog("Unable to find user_data.json")
	except Exception as e:
		logger.addLog("While opening twitter users got error : {}".format(e))

	msg = "" 
	if fb_flag :
		msg = msg + "<strong>You are subscribed to following Facebook pages :</strong>\n{}\n".format(', '.join(subs_pages_list))
	else :
		msg = msg + "<strong>You are not subscribed to any Facebook page</strong>\n"
	if tw_flag :
		msg = msg + "<strong>You are subscribed to following Twitter Handles :</strong>\n@{}\n".format(' ,@'.join(twitter_subs_handle_list))
	else :
		msg = msg + "<strong>You are not subscribed to any Twitter Handle</strong>\n"
	bot.sendMessage(chat_id=update.message.chat_id , text = msg , parse_mode='html')
#handles all the callback_data sent by inline query keyboard
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
	elif update.callback_query['data'].startswith('joke'): #this means user wants to hear a joke
		query = update.callback_query['data'].split("_")
		if query[1] == "CN" :
			Thread(target=get_joke_chuck , args=(bot,update.callback_query['message']['chat']['id'], query[-1])).start()
	elif update.callback_query['data'].startswith('mail'): #sending mail
		try :
			mail_json = json.load(open('mail_sub_{}'.format(update.callback_query['message']['chat']['id']) , 'r') )
			if update.callback_query['data'].split('_')[1] == 'y' : #user chose  yes 
					bot.sendMessage(chat_id=update.callback_query['message']['chat']['id'] ,text="Sending mail ...")
					logger.addLog("Sending the mail")
					# mail_json = json.load('mail_sub_{}'.format(update.callback_query['message']['chat']['id']))
					Thread(target=sendEmail.sendMail, args=(mail_json['id'] , mail_json['text']  , mail_json['sub'] ,)).start()
					file_local_path = os.path.abspath("./{}".format('mail_sub_{}'.format(update.callback_query['message']['chat']['id']))) #getting full file path
					os.remove(file_local_path)  #removing the file
					bot.sendMessage(chat_id=update.callback_query['message']['chat']['id'] ,text="Mail sent successfully")
					logger.addLog("mail sent")
			else :
				#bot.sendMessage(chat_id=update.callback_query['message']['chat']['id'] ,text="Aborting the mail")
				file_local_path = os.path.abspath("./{}".format('mail_sub_{}'.format(update.callback_query['message']['chat']['id'])))  # getting full file path
				os.remove(file_local_path)  # removing the file
				bot.sendMessage(chat_id=update.callback_query['message']['chat']['id'], text="Mail has been successfully discarded")
				logger.addLog("Sending mail canceled ")
		except Exception as e:
			logger.addLog(e)
			bot.sendMessage(chat_id=update.callback_query['message']['chat']['id'] ,text="Session ended.. Please send /mail to send a mail.")

#starting of the command handelling functions

#This handles the welcome message when someone starts the chat first time with the bot
def start(bot, update):
	welcome_message_1 = [
	  "Hi ",
	  "Hola ",
	  "Hey ",
	  "Hey there, "
	]

	welcome_message_2 = [
	  "! Looks like we haven't met before.",
	  "! Looks like this is our first meet.",
	  "! How are you doing.",
	]

	welcome_message_3 = [
	  " Send /help to know my secrets."
	]
	rand_index1 = randint(0,len(welcome_message_1) -1)
	rand_index2 = randint(0,len(welcome_message_2) -1)
	rand_index3 = randint(0,len(welcome_message_3) -1)
	first_name = update.message.from_user.first_name
	msg = welcome_message_1[rand_index1] + first_name + welcome_message_2[rand_index2]+ welcome_message_3[rand_index3]
	bot.sendMessage(chat_id=update.message.chat_id, text=msg)			
#this return the available joke types when user sends /joke
def handle_jokes(bot,update):
	joke_buttons = [[{'text':"Chuch Norris nerdy joke" , 'callback_data' : 'joke_CN_nerdy'}],[{'text':'Chuch Norris explicit joke' , 'callback_data' : 'joke_CN_explicit'}]]
	joke_keyboard = {'inline_keyboard': joke_buttons }
	bot.sendMessage(chat_id=update.message.chat_id , text="Choose which joke you want" , reply_markup =joke_keyboard)
	#Thread(target=get_joke_chuck , args=(bot,update.message.chat_id,)).start()
#this function handles Chuck jokes
def get_joke_chuck(bot,chat_id,category):
	base_url = "http://api.icndb.com/jokes/random?limitTo=[{}]".format(category)
	logger.addLog("Getting Joke","joke")
	try :
		joke_json = requests.get(base_url).json()
		logger.addLog("Successfully got the joke")
		joke_msg = html.unescape(joke_json['value']['joke'])  #decoding the html encoding in the joke
		bot.sendMessage(chat_id=chat_id , text=joke_msg)
	except :
		logger.addLog("Unable to get joke {} ".format(sys.exc_info()[0]))
		bot.sendMessage(chat_id=chat_id, text="Sorry Unable to fetch joke")
#this is the mail mail fuction which takes information to send step by step to send the mail 
def send_mail(bot,update) :
	global Flag
	bot.sendMessage(chat_id=update.message.chat_id , text="Want to share some information with someone but don't wanna use your email address so you are at right place.\nSend the email id(s) to whom you wish to send the email. In case of multiple ids separate them with comma(,)")
	Flag = "mail_id"
#this takes a confirmation to send the mail
def mail_confirm(bot,chat_id,mail_msg):
	buttons = [{'text': "Yes" , 'callback_data' : 'mail_y'} , {'text': "No" , 'callback_data' : 'mail_n'}]
	Inline_keyboard = {'inline_keyboard': [buttons] }
	bot.sendMessage(chat_id=chat_id ,reply_markup = Inline_keyboard ,text = "The E-mail is as follows :\n{}\n\nShould I send it ?".format(mail_msg) , parse_mode='html' ,disable_web_page_preview=True)
#this return the user same text what he/she sent
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
	elif Flag == "fb_reg" :
		logger.addLog ("Got the request to add facebook pages")
		Flag = None
		pages = update.message.text.split(',')
		logger.addLog("Staring fb_adding thread")
		Thread(target =fb_reg.main, args = (pages,update.message.chat_id,bot,logger)).start()
	elif Flag == "twitter_reg" :
		logger.addLog ("Got the request to add twitter handles","Twitter")
		Flag = None
		handles = update.message.text.split(',')
		logger.addLog("Staring twitter_adding thread" ,"Twitter")
		Thread(target =twitter_reg.main, args = (handles,update.message.chat_id,bot,logger)).start()
	elif Flag == "mail_id" :
		logger.addLog ("Got the email ids to send mail ")
		ids = update.message.text.split(',')
		json.dump({'id':ids} , open('mail_sub_{}'.format(update.message.chat_id),'w'))
		bot.sendMessage(chat_id=update.message.chat_id , text="Please Send the subject of your email")
		Flag = "mail_sub"
	elif Flag == "mail_sub" :  #getting the mail subject
		bot.sendMessage(chat_id=update.message.chat_id , text="Please Send the main body of your email")
		logger.addLog ("Got the subject to send mail from ")
		mail_json = json.load(open('mail_sub_{}'.format(update.message.chat_id),'r'))
		mail_json['sub'] = update.message.text
		json.dump(mail_json,open('mail_sub_{}'.format(update.message.chat_id),'w')) 
		Flag = "mail_text"
	elif Flag == "mail_text" :
		logger.addLog("Got the mail text")
		Flag = None
		mail_json = json.load(open('mail_sub_{}'.format(update.message.chat_id),'r'))
		mail_json['text'] = "{}\n\nSent via - Utilo Bot (The advanced telegram bot.Learn more at telegram.me/UtiloBot)".format(update.message.text )
		json.dump(mail_json,open('mail_sub_{}'.format(update.message.chat_id),'w'))
		mail_msg = "<strong>Subject</strong> :{}\n<strong>Body</strong> :{}\n<strong>Recipents : </strong>{}".format(mail_json['sub'],mail_json['text'],', '.join(mail_json['id']))
		mail_confirm(bot,update.message.chat_id,mail_msg)
	else :
		bot.sendMessage(chat_id=update.message.chat_id, text=update.message.text)
	# ne = bot.editMessageText(message_id=int(message_obj.message_id) , chat_id=update.message.chat_id,text="This is updated message")
	# logger.addLog (ne.message_id)
#this return the user the same sticekr which he/she sent
def echo_sticker(bot,update):
	bot.sendSticker(chat_id=update.message.chat_id,sticker=update.message.sticker.file_id)
#return a help message when one someone send /help
def bot_help(bot,update):
	bot.sendMessage(chat_id=update.message.chat_id,text="<strong>1. Using file link generator : </strong>\nSimply "
														"send your file to the bot and rest bot will see.You can record or send a video , "
														"capture or send a image , send audio files. Inshort  you can send any kind of file. You can "
														"also send  voice clips.\n<strong> 2. Using Youtube functionality </strong>\nSend <strong>/youtube</strong>" 
														"to download a video via URL or to first search a video on youtube an then download.\n<strong>3. Subscribing to facebook pages</strong>\n"
														"Send <strong>/facebook</strong> and follow the bot instrutions.\n<strong>4. Subscribing to twitter handles</strong>\n"
														"Send <strong>/twitter</strong> and follow the onscreen instrustions to subscribe to twitter handles.\n"
														"Note : Current refresh rate for facebook pages and twitter handles is 10 minutes.\n"
														"<strong>5. Getting hilarious jokes</strong>\nSend <strong>/joke</strong> to read hilarious Chuck Norris jokes.\n"
														"<strong>6. Sending mail</strong>\nSend <strong>\mail</strong> to send a email to one or multiple people on behalf of you "
														"via Utilo.",parse_mode="HTML")
#this function handles the mysubscription command
def subs_handler (bot,update):
	Thread(target=user_subs_fb_twitter , args=(bot,update,)).start()


#ending of the command handling functions

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


bot_for_thread = telegram.Bot(token=token)
Thread(target=facebook_sender_handler , args=(bot_for_thread,logger,)).start()  #starting thread to scrape facebook pages
Thread(target=twitter_sender_helper , args=(bot_for_thread,logger,)).start()  #starting thread to scrape facebook pages
Flag = None
you_obj = None
updater = Updater(token=token)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
#creating handlers
start_handler = CommandHandler('start', start)
youtube_handler = CommandHandler('youtube' , youtube_keyboard)
help_handler = CommandHandler('help' , bot_help) 
facebook_handler = CommandHandler('facebook',facebook_start)
twitter_handler = CommandHandler('twitter',twitter_start)
joke_handler = CommandHandler('joke',handle_jokes)
mail_handler = CommandHandler('mail',send_mail)
subscription_handler = CommandHandler('mysubscription',subs_handler)
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
dispatcher.add_handler(help_handler)
dispatcher.add_handler(joke_handler)
dispatcher.add_handler(mail_handler)
dispatcher.add_handler(subscription_handler)
dispatcher.add_handler(facebook_handler)
dispatcher.add_handler(twitter_handler)
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
