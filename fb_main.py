from fbscraper import get_aggregated_feed as get_id
import json
def message_sender (page,bot,old_id) :
	posts = json.load(open('FB/page_json/{}.json'.format(page['id']) , 'r'))
	for post in posts :
		if post['id'] == old_id :
			break
		else :
			for subscribers in page['subs'] :
				try :
					pic = post['pic'] 
				except KeyError :
					pic = False
					#msg = "<strong>{}</strong>{}\nPosted on : {} at {} \n<a href='https://www.facebook.com/{}'>View the post</a>".format(page['name'],post['message'],post['real_date'],post['real_time'],post['id'])
				if pic :
					msg = "<a href='{}'>Image</a>\n<strong>{}</strong>\n{}\nPosted on : {} at {} \n<a href='https://www.facebook.com/{}'>View the post</a>".format(pic,page['name'],post['message'],post['real_date'],post['real_time'],post['id'])
				else :
					msg = "<strong>{}</strong>\n{}\nPosted on : {} at {} \n<a href='https://www.facebook.com/{}'>View the post</a>".format(page['name'],post['message'],post['real_date'],post['real_time'],post['id'])
					
	#				print("<a href={}>Image</a>\n{}\nPosted on : {} at {} \n<a href='https://www.facebook.com/{}'>View the post</a>".format(post['pic'],post['message'],post['real_date'],post['real_time'],post['id']))
				bot.sendMessage(chat_id=subscribers , text = msg , parse_mode = 'HTML',disable_web_page_preview=True)
def main(bot,logger) :
	try :
		pages = json.load(open('FB/pages.json','r'))
	except FileNotFoundError :
		return 0 
	for page in pages :
		new_id = get_id(page['id'],logger)
		if new_id != page['last_post'] : #It means something new was posted
			message_sender(page,bot,page['last_post'])
			page['last_post'] = new_id
	json.dump(pages,open('FB/pages.json','w'))