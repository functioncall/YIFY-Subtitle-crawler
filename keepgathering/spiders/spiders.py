import scrapy
import urlparse
import subprocess
from scrapy.http import Request
from scrapy.selector import Selector

BASE_URL = "http://www.yifysubtitles.com/"

class DmozSpider(scrapy.Spider):
	"""
	This is the Spider class containing the spider details and its parsing methods.
	"""
	# Name of the Spider
	name = "dmoz"
	def __init__(self, **kwargs):
		"""
		This method initializes all the required variables
		"""
		# Get the name of the movie from the command line argument
		self.movie = kwargs.get('movie')
		self.allowed_domains = ["yifysubtitles.com"]
		self.start_urls = [
			"http://www.yifysubtitles.com/search?q={0}".format(self.movie)
			# "http://www.yifysubtitles.com/search?q=%s" % self.movie			
		]

	def parse(self, response):
		"""
		This is the first parse method which takes the html response object and generates the 
		new url for further parsing. We parse the page which contains the result after start_url is hit.
		"""
		# sel is the selector of the page that contains all the data of the web page
		sel = Selector(response)
		# Requests is a vector that will contain all the http request of the Spider
		requests = []
		
		# we iterate the return vector and for each object we select a piece of HTML 
		# code which contains the name and the url of the current category
		# With extract it is possible to extract the selected data from the selector 
		# into a Unicode string.
		for link in sel.xpath('//ul/li'):
			url = link.xpath('a/@href').extract()
			# Ignore null urls.
			if url != [] :
				# Creating an HTTP request message for the next page
				requests.append(Request(
					url = urlparse.urljoin(BASE_URL, str(url[0])), callback = self.parse_subcategory1))
		return requests

	def parse_subcategory1(self, response):
		"""
		This function is used to parse the page which contains the list of available subtitiles
		for the current movie.
		"""
		sel = Selector(response) # Selector for the current page
		requests = [] # request vector for the new http request

		# we iterate the return vector and for each object we select a piece of HTML 
		# code which contains the name and the url of the current category
		# With extract it is possible to extract the selected data from the selector 
		# into a Unicode string
		for link in sel.xpath('//*[@id="movie-info"]/div[2]/ul[2]/li'):
			url = link.xpath('a/@href').extract()
			name = link.xpath('a/span/text()').extract()[0]

			# Filter subtitles which are in English
			if name == 'English':
				# Creating an HTTP request message for the next page
				requests.append(Request(
					url = urlparse.urljoin(BASE_URL, str(url[0])), callback = self.parse_subcategory2))
		return requests

	def parse_subcategory2(self, response):
		"""
		This parsing method fetches all the subtitle zip files and downloads it using little wget magic.
		"""
		sel = Selector(response)
		for link in sel.xpath('//*[@id="movie-info-main"]/div[1]'):
			url = link.xpath('a/@href').extract()[0]
			subprocess.call(['wget','-nH', url, '-Psrt_files/'])
			pathToZip = '/home/zerobyte/Desktop/keepgathering/keepgathering/srt_files/*.zip'
			pathToOut = '/home/zerobyte/Desktop/keepgathering/keepgathering/srt_files/'
			unzip = ['unzip','-o',pathToZip,'-d',pathToOut]
			subprocess.call(unzip)
		return url