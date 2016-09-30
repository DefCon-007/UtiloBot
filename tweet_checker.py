"""
This script will run every say 5 minuetes to check for new tweets
It will save the results in twitter.json
The default value of flag will be 0 i.e. NO message to be sent for that user
If a new tweet will be found it will change flag to 0 i.e. message will be sent for this handle
It will save the tweets in a list 
"""
import tweepy
import time
from tweepy import OAuthHandler
import json
api = None 
def log_in ():
	global api
	twitter_credentials = json.load(open("./TWITTER_CONFIG.json","r"))
	#logging in to twitter
	access_token = twitter_credentials["access_token"]
	access_token_secret = twitter_credentials["access_token_secret"]
	consumer_key = twitter_credentials["consumer_key"]
	consumer_secret = twitter_credentials["consumer_secret"]
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth,wait_on_rate_limit=True)
	return api
def getting_last_tweet_id(twitter_handel,api=None , flag = 0):
	if api == None :
		api = log_in()
	try :
		last_tweet = api.user_timeline(screen_name=twitter_handel, count=flag+1)
		last_tweet_id = (last_tweet[flag].id)
		return last_tweet_id
   # except tweepy.error.TweepError:
	except Exception as e:
		logger.addLog("While getting last_tweet_id got error : ".format(e) , "Twitter")
		return False
def validating_handle(handle,api = None ):
	if api == None :
		api = log_in()
	try:
		api.get_user(screen_name=handle)
		return True
	except tweepy.error.TweepError as e:
		#print ("In validating handle error : ".format(e))
		return False
def twitter(handle , last_id):
	if api == None :
		log_in()
	while True :
		try :
			print ("GOt the last id : {}".format(last_id))
			new_tweets = api.user_timeline(screen_name=handle, since_id=last_id)
			tweets_text = []
			for tweet in new_tweets:
				tweets_text.append(tweet.text)
			print (tweets_text)  
			return tweets_text
			break
		except Exception as e:
			print ("While getting new tweets got the error : {}".format(e))
		# except tweepy.error.TweepError as e:
		# 	print (e)
		# 	print ("Tweepy limit reached : Waiting for 15 minutes")
		# 	time.sleep(900)
	
def send_msg(handle,tweets,chat_ids,bot):
	msg = "<strong>@{}</strong> tweeted : \n{}".format(handle,"\n\n".join(tweets))#converting tweets list into a message
	for chat_id in chat_ids :
		bot.sendMessage(chat_id=chat_id , text=msg , disable_web_page_preview=True ,parse_mode='html')
		logger.addLog ("Sent tweets of {}  to {} ".format(handle,chat_id),"Twitter")

def main(bot,log) :
	global logger
	logger = log
	try :
		handles = json.load(open("Twitter/twitter.json", "r")) 
	except FileNotFoundError:
		logger.addLog("Unable to find twitter.json")
		return 0 
	except Exception as e:
		logger.addLog("Got error while opening twitter.json :{}".format(e))
	for handle in handles :
		last_id = getting_last_tweet_id(handle["handle"])
		if last_id :		
			if (handle["last_tweet_id"] != last_id  ) :  #this means there are new tweets
				logger.addLog ("Got a new tweet for {}".format(handle['handle']),"Twitter")
				new_tweets = twitter(handle["handle"] , handle["last_tweet_id"]) 
				#handle["tweets"] =  new_tweets   # getting the latest tweets and saving them to json
				handle["last_tweet_id"] = last_id   # Changing last tweet id
				#handle["flag"] = 1  #changing flag value, this will tell for which handle we have to send the message
				send_msg(handle['handle'],new_tweets,handle['subs'],bot)  #sending new tweets
	json.dump(handles , open('Twitter/twitter.json','w'))
