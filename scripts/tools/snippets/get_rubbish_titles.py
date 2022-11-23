import requests
from bs4 import BeautifulSoup as bs
import dateparser
links = ["http://therubbishtrip.co.nz/podcast/podcast-14-caroline-millie-vinnies-re-sew","http://therubbishtrip.co.nz/podcast/podcast-13-rick-brown-the-seagull-centre-thames","http://therubbishtrip.co.nz/podcast/podcast-12-nicky-francis-do-gooder","http://therubbishtrip.co.nz/podcast/podcast-11-gretta-carney-hapi","http://therubbishtrip.co.nz/podcast/podcast-10-franziska-von-hunerbein-crop-swap-aotearoa/ ","http://therubbishtrip.co.nz/podcast/podcast-9-james-denton-goodfor-wholefoods-refillery/ ","http://therubbishtrip.co.nz/podcast/podcast-8-carrie-and-jay-inspire-wellness-whangamata ","http://therubbishtrip.co.nz/podcast/podcast-7-phil-mccabe-solscape-and-kiwis-against-seabed-mining/ ","http://therubbishtrip.co.nz/podcast/podcast-6-robert-scott-reclaimed-timber-traders/ ","http://therubbishtrip.co.nz/podcast/podcast-5-nandor-tanczos-the-waste-minimisation-act-2008/ ","http://therubbishtrip.co.nz/podcast/podcast-4-colin-and-gabrielle-kemplen-transition-matamata-the-kiwi-bottle-drive","http://therubbishtrip.co.nz/podcast/podcast-3-chats-at-the-repair-cafe-with-kapiti-menzshed-and-kapiti-community-centre","http://therubbishtrip.co.nz/podcast/podcast-2-eryn-gribble-and-renee-rushton-newtown-community-cultural-centre","http://therubbishtrip.co.nz/podcast/te-kawa-robb-para-kore-and-sustainable-coastlines"]
for link in links:
	#print(link)
	r = requests.get(link)
	my_soup = bs(r.text,"lxml")
	# title = my_soup.find_all("h1")[0]
	# desctiption = my_soup.find_all("div", {"class": "single-content"})[0]
	date = my_soup.find_all("div", {"class": "entry-date date updated"})[0].text
	#print(type(date))
	new_date = dateparser.parse(date,settings = {'DATE_ORDER': 'DMY'}).strftime("%B %d %Y")
	#print(title.text)
	print(new_date)
