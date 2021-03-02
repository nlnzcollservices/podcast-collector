import requests
import gspread
import dateparser
from time import mktime
from bs4 import BeautifulSoup as bs
from datetime import datetime as dt
try:
	from settings import  logging, creds,podcast_sprsh
except:
	from settings_prod import  logging, creds, podcast_sprsh

from read_episode_from_googlesheet_to_db import ReadFromSpreadsheet
from database_handler import DbHandler
from podcasts_dict import podcasts_dict
logger = logging.getLogger(__name__)

def library_loudhailer_routine():

	logger.info("Scrping Library loudhailer")
	c = gspread.authorize(creds)
	gs = c.open_by_key(podcast_sprsh)
	#change if the name or id of the worksheet is different
	ws = gs.get_worksheet(0)
	logger = logging.getLogger(__name__)
	podcast_name = "Library loudhailer"
	my_db=DbHandler()
	time_dict = my_db.db_reader(["podcast_name", "last_issue"],[podcast_name],True)

	base_url = r"https://natlib.govt.nz"	
	#url = r"https://natlib.govt.nz/blog/tags/podcast"
	url = r"https://natlib.govt.nz/blog/categories/library-loudhailer"

	"""Harvests Library loudhailer website , populates google spreadsheet and runs spreadsheet reader"""

	r = requests.get(url)
	my_soup = bs(r.text, "lxml")



	episode_links = my_soup.find_all("div", {'class':'blog-card'})
	for link in episode_links:
		episode_link = base_url+link.find("a").attrs["href"]

		r = requests.get(episode_link)
		my_soup2 = bs(r.text, "lxml")
		#print(my_soup2)
		try:
			episode_download_link = base_url+my_soup2.find_all("audio")[0].attrs["src"]
		except:
			episode_download_link =""
		episode_title = my_soup2.find("h1").text
		date = my_soup2.find("span", {"class":"dove-gray"}).text
		logger.info(date)
		new_date = dateparser.parse(date)
		time_stamp = mktime(new_date.timetuple())

		if time_stamp > time_dict[0]["last_issue"]:
		# #print(new_date)
			new_date = new_date.strftime("%B %d %Y")
			description_html=my_soup2.find("div",{"class":"contentful-blog-content__body"})
			tags_list = ""
			tags = my_soup2.find("h3", {"class":"margin-top-0"}).parent.find_all("a")
			for tag in tags:
				tags_list+=tag.text+", "
			tags_list = tags_list.rstrip(", ").lstrip(",")
			plogger.info(tags_list)


			try:
				description1 = description_html.find("div",{"class":"summary-block"}).text.strip("\n")
			except:
				description1 = ""
			try:
				description2 = description_html.find("h2").text
			except:
				description2 = ""
			try:
				description3= description_html.find("p").text
			except:
				description3 = ""
			description = description1+description2+description3
			logger.info(description)
			connection_count = 0
			while not connection_count >= 5:
				connection_count +=1
				try:

					ws.append_row([podcast_name, podcasts_dict[podcasat_name]["serial_mms"], podcasts_dict[podcast_name]["rss_filename"], episode_title, description, episode_link,new_date, tags_list, episode_download_link])
					ws = gs.get_worksheet(0)
					logger.info("a new row appended")
					logger.info(row_count)
					start_row = ws.row_count
					finish_row = int(start_row) 
					rs = ReadFromSpreadsheet(start_row,finish_row)
					rs.get_metadata_from_row()
					break

				except gspread.exceptions.APIError as e:
					logger.error(str(e))
					sleep(10)

if __name__ == "__main__":
	library_loudhailer_routine()

