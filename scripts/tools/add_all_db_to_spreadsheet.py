import os
import sys
import re
import feedparser
import podcastparser
import subprocess
import gspread
sys.path.insert(0, r'H:\GIT\file-downloader')
from downloader_light_modified import DownloadResource as Downloader
sys.path.insert(0, r"Y:\ndha\pre-deposit_prod\LD_working\alma_tools")
from alma_tools import AlmaTools
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from time import time, sleep, mktime
from datetime import datetime as dt
from podcast_dict import podcasts_dict, serials
from database_handler import DbHandler
from nltk.corpus import words
import nltk
from datetime import datetime
import dateparser

nltk.download('words')
##################################SSL  problem########################################
import ssl
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context
ssl._create_default_https_context = ssl._create_unverified_context
##############################################################################
try:
	from settings import  file_folder, report_folder, podcast_sprsh, logging,creds #!!!! report
except:
	from settings_prod import  file_folder, report_folder, podcast_sprsh, logging,creds
logger = logging.getLogger(__name__)

#######################################Creating google spreadsheet object#################################################


c = gspread.authorize(creds)
gs = c.open_by_key(podcast_sprsh)
#change if the name or id of the worksheet is different
worksheet = "from_db"
ws = gs.get_worksheet(0)

# rows_to_delete = [1743, 1741, 1739, 1737, 1735, 1733, 1731, 1729, 1727, 1725, 1723, 1721, 1719, 1717, 1715, 1713, 1711, 1709, 1707, 1705, 1703, 1701, 1699, 1697, 1695, 1693, 1691, 1689, 1687, 1685, 1683, 1681, 1679, 1677, 1675, 1673, 1671, 1669, 1667, 1665, 1663, 1661, 1659, 1657, 1655, 1653, 1651, 1649, 1647, 1645, 1643, 1641, 1639, 1637, 1635, 1633, 1631, 1629, 1627, 1625, 1623, 1621, 1619, 1617, 1615, 1613, 1611, 1609, 1607, 1605, 1603, 1601, 1599, 1597, 1595, 1593, 1591, 1589, 1587, 1585, 1583, 1581, 1579, 1577, 1575, 1573, 1571, 1569, 1567, 1565, 1563, 1561, 1559, 1557, 1555, 1553, 1551, 1549, 1547, 1545, 1543, 1541, 1539, 1537, 1535, 1533, 1531, 1529, 1527, 1525, 1523, 1521, 1519, 1517, 1515, 1513, 1511, 1509, 1507, 1505, 1503, 1501, 1499, 1497, 1495, 1493, 1491, 1489, 1487, 1485, 1483, 1481, 1479, 1477, 1475, 1473, 1471, 1469, 1467, 1465, 1463, 1461, 1459, 1457, 1455, 1453, 1451, 1449, 1447, 1445]
# for row in rows_to_delete:
#     ws.delete_rows(row)
db_handler = DbHandler()
# my_dictionary = db_handler.db_reader(["podcast_name"])
# print(my_dictionary)
# quit()

podcast_list = ["Dancing in your head"]


flag = False
db_handler = DbHandler()
my_dictionary = db_handler.db_reader(["podcast_name", "automated_flag", "serial_mms", "rss_link", "episode_title", "bib_title","bib_numbering","epis_numb" ,"epis_seas", "description", "episode_link", "date", "tags","harvest_link","date_harvested", "mis_mms"],podcast_list,True)
for el in my_dictionary:
	try:
		#print(el)
		if not el["automated_flag"] and not el["mis_mms"]:
			# if el["episode_title"] == "//071 Dr Ani Alana Kainamu":
			# 	flag = True
			# if flag :
				ws.append_row([el["podcast_name"],el["serial_mms"], el["rss_link"], el["episode_title"], el["bib_title"],el["bib_numbering"],el["epis_seas"], el["epis_numb"], el["description"], el["episode_link"], dt.fromtimestamp(int(el["date"])).strftime('%B %d %Y'), el["tags"], el["harvest_link"], el["date_harvested"].strftime('%B %d %Y')])

	except Exception as e:
		print(str(e))
		print("!!!!!!!!!!")
		print(el)
		if "Quota" in str(e):
			quit()

								


