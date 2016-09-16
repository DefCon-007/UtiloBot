import tinyurl
import sys
from selenium import webdriver
import selenium.common.exceptions
import time
from selenium.webdriver.common.proxy import *
def main(file_path):
	driver = webdriver.Chrome()
	driver.get('http://expirebox.com/')
	file_upload = driver.find_element_by_id('fileupload')  #finding the file upload element
	#print ("Uploading file please wait")
	file_upload.send_keys(file_path)  #uploading file
	while True :
		try :
			del_button = driver.find_element_by_xpath("//button[@class='btn btn-danger btndel']")
			del_button.click()
		   # print ("Upload Complete")
			break
		except selenium.common.exceptions.ElementNotVisibleException :
			time.sleep(1)
			pass
	driver.switch_to_window(driver.window_handles[1])  #switching to the new tab which have links
	del_link = driver.current_url + "?proceed=1" #getting delete file link
	# getting download link
	down_link = driver.find_element_by_xpath("//a[@class='btn btn-xs btn-success btn-download']").get_attribute('href')
	#shortening urls
   # file_name = input("Enter a link name for : tinyurl.com/abc (Leave blank to use default filename) : ")
  #if file_name is "" : 
	file_name = file_path.split('/')[-1][0:5]
	count = 1
	links = {"down": "X" , "del" : "X"}
	while links['down']:
		links['down'] = tinyurl.shorten(down_link , "SB-"+file_name)
		links['del'] = tinyurl.shorten(del_link , "del-"+file_name)
		file_name = file_name + str(count)
		count = count + 1 
	driver.quit()
	print (links)
	return links 
if __name__ == "__main__":
	main(sys.argv[1])
