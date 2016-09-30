import json 
from tweet_checker import validating_handle,log_in,getting_last_tweet_id
def handle_check(handle_list,api) :
	valid_handle = []
	invalid_handle = []
	for handle in handle_list :
		if validating_handle(handle , api) :
			valid_handle.append(handle)
		else :
			invalid_handle.append(handle)
	ret_json = {'valid' : valid_handle , 'invalid' : invalid_handle}
	return ret_json
def updating_user_data(handle_list,chat_id) :
	flag = True
	try :
		user_data = json.load(open('Twitter/user_data.json' , 'r')) 
	except FileNotFoundError :
		flag = False
	if flag :  #this means a previous user_data.json file is present 
		usr_flag = True
		for user in user_data :
			if user['chat_id'] == chat_id :   #checking if the user is already present
				user['handles'].extend(handle_list)  #adding new handles
				user['handles'] = list(set(user['handles']))  #removing duplicate handles
				usr_flag = False 
				break
		if usr_flag : 
			user_data.append({'handles' : handle_list , 'chat_id' : chat_id})
		
	else : #this means user.json file is not present
		user_data = [{'handles' : handle_list , 'chat_id' : chat_id}]
	json.dump(user_data,open('Twitter/user_data.json','w'))
def add_handle_for_scrapping(handle_list,chat_id,api) :
	flag = True
	try :
		handle_data = json.load(open('Twitter/twitter.json' , 'r')) 
	except FileNotFoundError :
		flag = False
	if flag :    #this means twitter .json is present
		for handle in handle_list :
			dup_flag = True
			for data in handle_data :
				if data['handle'] == handle :
					data['subs'].append(chat_id)
					dup_flag = False
			if dup_flag : 
				handle_data.append({'handle' : handle , 'tweets':"", 'last_tweet_id' : getting_last_tweet_id(handle,api,1) , 'subs' : [chat_id]})  #this means the handle is not present in the file
	else :
		handle_data = []
		for handle in handle_list :
			handle_data.append({'handle' : handle , 'tweets':"", 'last_tweet_id' : getting_last_tweet_id(handle,api,1) , 'subs' : [chat_id]})
	json.dump(handle_data,open('Twitter/twitter.json','w'))
def main(handle_list,chat_id,bot,log):
	global logger
	logger =log
	api = log_in()
	checked_handle = handle_check(handle_list,api) 
	valid_handle = checked_handle['valid']
	invalid_handle = checked_handle['invalid']
	if len(valid_handle) != 0 :
		add_handle_for_scrapping(valid_handle,chat_id,api) #adding valid handles to twitter.json
		updating_user_data(valid_handle,chat_id)
		msg = "Congratulations ! You have been subscribed to following handle(s) : \n"
		for index,handle in enumerate(valid_handle) :
			msg = msg + "{}. {}\n".format(str(index+1),handle) 
		bot.sendMessage(chat_id=chat_id , text=msg)
	if len(invalid_handle) != 0 :
		msg = "Sorry ! Following handle(s) supplied by you were invalid :\n"
		for index,handle in enumerate(invalid_handle) :
			msg = msg + "{}. {}\n".format(str(index+1),handle) 
		bot.sendMessage(chat_id=chat_id , text=msg)