import bitly_api
import sys
from selenium import webdriver
import selenium.common.exceptions
import time
#import tinyurl_shortbox
import Logger
logger = Logger.Logger(name='My_Logger')
def main(file_path):
	with open('./BITLY_ACCESS_TOKEN', 'r') as f:
		bitly_token = f.readline().rstrip('\n')
	bitly = bitly_api.Connection(access_token=bitly_token)

	driver = webdriver.PhantomJS()
	driver.get('http://expirebox.com/')
	file_upload = driver.find_element_by_id('fileupload')  #finding the file upload element
	logger.addLog ("Uploading file please wait")
	i=0 
	while True :
		try : 
			file_upload.send_keys(file_path)  #uploading file
			break 
		except Exception as e :
			if i >= 2 :
				driver.quit()
				return 0
			i +=1
			logger.addLog ("Got error : {}".format(str(e)))
			time.sleep(4)
			driver.get('http://expirebox.com/')
			file_upload = driver.find_element_by_id('fileupload')  #finding the file upload element
	time.sleep(2)
	while True :
		try :
			del_button = driver.find_element_by_xpath("//button[@class='btn btn-danger btndel']")
			del_button.click()
			logger.addLog ("Upload Complete")
			break
		except selenium.common.exceptions.ElementNotVisibleException :
			if i >= 3 :
				driver.quit()
				return 0
			i += 1
			logger.addLog("Got Element not visible error")
			time.sleep(1)
			pass
		except http.client.RemoteDisconnected :
			logger.addLog("Got http.client.RemoteDisconnected error recalling the function")
			driver.quit()
			return 3

	time.sleep(5)
	driver.switch_to_window(driver.window_handles[1])  #switching to the new tab which have links
	del_link = driver.current_url + "?proceed=1" #getting delete file link
	# getting download link
	down_link = driver.find_element_by_xpath("//a[@class='btn btn-xs btn-success btn-download']").get_attribute('href')
	#shortening urls
   # file_name = input("Enter a link name for : tinyurl.com/abc (Leave blank to use default filename) : ")
  #if file_name is "" : 
	# file_name = file_path.split('/')[-1][0:5]
	# original_file_name = file_name
	# count = 1
	links = {"down": "" , "del" : ""}
	# flag = 1
	links['down'] =bitly.shorten(down_link)['url']
	links['del'] =bitly.shorten(del_link)['url']
		#links['down'] = tinyurl_shortbox.shorten(down_link , "SB-"+file_name)
		#links['del'] = tinyurl_shortbox.shorten(del_link , "del-"+file_name)
		# if links['down'] != 1:
		# 	flag = 0
		# file_name = original_file_name + str(count)
		# count = count + 1
	driver.quit()
	logger.addLog (links)
	return links 
if __name__ == "__main__":
	main(sys.argv[1])
