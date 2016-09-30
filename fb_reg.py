import json 
import facepy
from facepy import GraphAPI
with open('./FB_ACCESS_TOKEN', 'r') as f:
    access_token = f.readline().rstrip('\n')
graph = GraphAPI(access_token)
#checking if all the pages are valid 
def page_check(page_list,logger) :
	wrong_page = list()  
	correct_page = list()
	page_names = list()
	for page in page_list :
		logger.addLog("Now checking for {}".format(page))
		try :
			response = graph.get(page)
			correct_page.append(page)
			page_names.append({'id':page,'name':response['name']})
		except facepy.exceptions.OAuthError:
			wrong_page.append(page)
		except facepy.exceptions.FacebookError :
			pass
	return ({'page':correct_page , 'wrong':wrong_page , 'names':page_names})
		# try :
		# 	response['error']['code'] == 803 
		# 	print ("wrong id")
		# 	wrong_id.append(page)
		# 	page_list.remove(page)
		# except :
		# 	print ('{} is correct'.format(page))
		# 	pass
def add_pages_for_scrapping(page_list,chat_id):
	flag = True
	try :
		pages_data = json.load(open('FB/pages.json','r'))
	except FileNotFoundError :
		flag = False
	if flag :  
		for page in page_list :
			dup_flag = True
			for page_data in pages_data :
				if page_data['id'] == page['id'] :
					page_data['subs'].append(chat_id)
					dup_flag = False
			if dup_flag :
				pages_data.append({'id' : page['id'] ,'name':page['name'], 'last_post' : 'None' , 'subs' : [chat_id]})
	else :
		pages_data = []
		for page in page_list :
			pages_data.append({'id':page['id'], 'name':page['name'] , 'last_post' : 'None' , 'subs':[chat_id]})
	json.dump(pages_data,open('FB/pages.json','w'))
def page_adder(page_list,chat_id):
	flag = True
	try :
		user_data = json.load(open('FB/users.json','r'))
	except FileNotFoundError :
		flag = False
	#checking if the chat id is already present in the json file 
	if flag :
		usr_flag = True
		for user in user_data :
			if user['chat_id'] == chat_id :
				user['page'].extend(page_list)  #adding new pages
				user['page'] = list(set(user['page']))  #removing duplicate pages
				usr_flag = False 
				break
		if usr_flag : 
			user_data.append({'page' : page_list , 'chat_id' : chat_id})
		
	else : #this means user.json file is not present
		user_data = [{'page' : page_list , 'chat_id' : chat_id}]
	json.dump(user_data,open('FB/users.json','w'))
def main(page_list,chat_id,bot,logger):
	logger.addLog("Checking for pages " ,"Facebook")
	pages_json = page_check(page_list,logger)  #checking if the supplied page id(s) were correct and removing the wrong ones
	logger.addLog("Got the response as : {}".format(pages_json) , "Facebook")
	if len(pages_json['page']) != 0 :
		page_adder(pages_json['page'],chat_id)  #addding the correct id(s)
		add_pages_for_scrapping(pages_json['names'],chat_id)
		subscribed = "Congratulations you have been subscribed to following page(s) :\n"
		for page in pages_json['names'] :
			subscribed = subscribed + "<strong>{}</strong> : {}\n".format(page['id'],page['name'])
		bot.sendMessage(chat_id=chat_id , text=subscribed ,parse_mode="HTML")
	if len(pages_json['wrong']) != 0 : 
		#sending back the wrong page ids
		msg = "Following page id(s) were wrong :\n{}".format('\n'.join(pages_json['wrong']))  
		bot.sendMessage(chat_id=chat_id , text=msg)
