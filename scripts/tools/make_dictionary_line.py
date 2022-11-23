from alma_tools import AlmaTools
import pymarc
import io
import re
import feedparser

"""
This script makes dictionary lines for podcast pipeline from text file.
Text file lines should be in the following format
Consume this MMS ID 9919142671902836 PO POL-174121
And produces the following dictionary format
#"A Neesh audience" : {'rss_filename': 'https://www.spreaker.com/show/4467635/episodes/feed', 'url': 'https://www.spreaker.com/show/a-neesh-audience', 'serial_mms': '9918987273002836', 'serial_pol': 'POL-126894', 'publish_link_ro_record': True, 'automated_flag': False, 'parsed_title':'A Neesh Audience', 'access_policy': '100', 'template_name': 'mis_Podcast_Neesh_audience.xml'} ,

"""
filename = r"Y:\ndha\pre-deposit_prod\LD_working\podcasts\assets\new_podcasts_11_2022.txt"
with open(filename, "r") as f:
	data= f.read()
new_dict = {}

for el in data.split("\n")[:-1]:
	po_line = None
	title = None
	mms = None
	
	el = el.replace("’","'")
	po_line = el.split(" ")[-1]
	title = el.split(" MMS ID")[0]
	print(title, po_line)
	mms = el.split("MMS ID ")[1].split(" PO ")[0]
	my_alma = AlmaTools("prod")
	my_alma.get_bib(mms)
	my_rec = pymarc.parse_xml_to_array(io.StringIO(my_alma.xml_response_data))[0]

	try:
		urls = my_rec.get_fields("856")
		my_url = str(urls[-1]["u"])#.rstrip("/#")

	except:
		print(my_rec)

	my_alma.get_po_line(po_line)
	receiving_note = re.findall(r"<receiving_note>(.*?)</receiving_note>", my_alma.xml_response_data)[0]
	rss_link = 	re.search(r"(?P<url>https?://[^\s]+)", receiving_note).group("url")
	url = "https://www.iod.org.nz"
	parsed_dict = feedparser.parse(rss_link)
	parsed_title = parsed_dict["feed"]["title"]
	new_dict[title]={'rss_filename': rss_link, 'url': my_url, 'serial_mms': mms, 'serial_pol': po_line, 'publish_link_ro_record': True, 'automated_flag': False, 'access_policy': '100', 'parsed_title': parsed_title, 'template_name': "mis_Podcast_"+ title.replace("'","").replace(",","").replace("&","and").replace(".","").replace(" ","_") + ".xml"} 
	print(new_dict)
