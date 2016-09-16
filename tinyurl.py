from bs4 import BeautifulSoup
from urllib.request import urlopen
count = 0
def shorten(long_url, alias,count=0):
	URL = "http://tinyurl.com/create.php?source=indexpage&url=" + long_url + "&submit=Make+TinyURL%21&alias=" + alias
	response = urlopen(URL)
	soup = BeautifulSoup(response, 'html.parser')
	check_error = soup.p.b.string
	if "The custom alias" in check_error:
		return None
	else:
		return (soup.find_all('div', {'class': 'indent'})[1].b.string)

