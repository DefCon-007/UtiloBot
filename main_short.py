import bitly_api
import sys
from selenium import webdriver
import selenium.common.exceptions
import time
#import tinyurl_shortbox
def main(file_path):
	with open('./BITLY_ACCESS_TOKEN', 'r') as f:
		bitly_token = f.readline().rstrip('\n')
	bitly = bitly_api.Connection(access_token=bitly_token)

	driver = webdriver.Chrome()
	driver.get('http://expirebox.com/')
	file_upload = driver.find_element_by_id('fileupload')  #finding the file upload element
	print ("Uploading file please wait")
	file_upload.send_keys(file_path)  #uploading file
	while True :
		try :
			del_button = driver.find_element_by_xpath("//button[@class='btn btn-danger btndel']")
			del_button.click()
			print ("Upload Complete")
			break
		except selenium.common.exceptions.ElementNotVisibleException :
			time.sleep(1)
			pass
	time.sleep(5)
	driver.switch_to_window(driver.window_handles[1])  #switching to the new tab which have links
	del_link = driver.current_url + "?proceed=1" #getting delete file link
	# getting download link
	down_link = driver.find_element_by_xpath("//a[@class='btn btn-xs btn-success btn-download']").get_attribute('href')
	#shortening urls
   # file_name = input("Enter a link name for : tinyurl.com/abc (Leave blank to use default filename) : ")
  #if file_name is "" : 
	file_name = file_path.split('/')[-1][0:5]
	original_file_name = file_name
	count = 1
	links = {"down": "" , "del" : ""}
	flag = 1
	while flag:
		links['down'] =bitly.shorten(down_link)['url']
		links['del'] =bitly.shorten(del_link)['url']
		#links['down'] = tinyurl_shortbox.shorten(down_link , "SB-"+file_name)
		#links['del'] = tinyurl_shortbox.shorten(del_link , "del-"+file_name)
		if links['down'] != 1:
			flag = 0 
		file_name = original_file_name + str(count)
		count = count + 1 
	driver.quit()
	print (links)
	driver.quit()
	return links 
if __name__ == "__main__":
	main(sys.argv[1])
