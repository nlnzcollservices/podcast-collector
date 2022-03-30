import peewee
import requests
import re
from podcast_models import Podcast, Episode, File
from datetime import datetime as dt
from time import mktime
import datetime as DT
from datetime import time
from bs4 import BeautifulSoup as bs
from podcast_dict import podcasts_dict
from alma_tools import AlmaTools
# import wget
import os
my_files = []
my_api = AlmaTools("prod")
# my_time  = mktime(dt.strptime("Jul 15 2021", "%b %d %Y").timetuple())
# # # # # # print(dt.fromtimestamp(1615827600).strftime('%B %d %Y'))
# print(my_time)
# quit()


# q = Podcast.update(last_issue= my_time).where(Podcast.podcast_name  == "Kelli from the Tron")
# q.execute()
# q = Podcast.update(serial_pol= "POL-138668").where(Podcast.serial_pol == "POL-138668 ")
# q.execute()
# q = Podcast.update(template_name= "mis_Podcast_Paiges_space.xml").where(Podcast.template_name == "mis_Pocast_Paiges_space.xml")
# # q.execute()
# q = Podcast.update(rss_link= "https://feed.podbean.com/newzealandhistory/feed.xml").where(Podcast.rss_link == 'https://feed.podbean.com/newzealandhistory/feed.xm')
# q.execute()
# q = Podcast.update(location = "https://natlib.govt.nz/blog/categories/library-loudhailer-podcast").where(Podcast.location == "https://natlib.govt.nz/blog/categories/library-loudhailer")
# q.execute()
# # # q = File.delete().where(File.filepath == r"Y:\NDHA\pre-deposit_prod\LD_Proj\podcasts\files\Business is boring\media-keuo4y6f-bib_zincovery_jonathan_ring_090920.mp3")
# # # q.execute()
# q = Episode.update(episode_title = 'Mark Zuckerberg wants (your) Attention - with Alex Beattie').where(Episode.episode_title == "Mark Zuckerberg wants your Attention - with Alex Beattie")
# q.execute()
# # #q = File.update(filepath = "D:\\Documents\\2019_Projects\\Pawaii\\podscasts_regular\\files\\Crave!\\crave080.mp3").where(File.id == 166)
# #q.execute()
# q = Podcast.update(rss_link = "https://www.spreaker.com/show/4359300/episodes/feed").where(Podcast.podcast_name == "Bosses in lockdown")
# q.execute()
# q= Episode.delete().where(Episode.podcast == 103)
# q.execute()

# files = File.select()
# for fl in files:
# 	if "Bosses in lockdown" in fl.filepath:
# 		q = File.delete().where(File.id == fl.id)
# 		q.execute()
# q = Podcast.update(serial_pol = "POL-129320").where(Podcast.serial_pol == "POL-129320 ")
# q.execute()

# q = Podcast.update(location = "https://natlib.govt.nz/blog").where(Podcast.podcast_name == "Library loudhailer")
# q.execute()


# q = Episode.update(podcast = 36).where(Episode.id==6002)
# q.execute()

# q = File.update(filepath = r"Y:\ndha\pre-deposit_prod\LD_Proj\podcasts\files\Business is boring\048125fb-f1e0-4f8c-86e3-65e7cf174c54.mp3",md5sum = '520608f55395654eb1c346b12975f51f', filesize = "28462756").where(File.episode==3925)
# q.execute()

# mms_list = []
# mms_list2 = []
# path = r"Y:\ndha\pre-deposit_prod\server_side_deposits\prod\ld_scheduled\oneoff_audio"
# for el in os.listdir(path):
# 	for mms in os.listdir(os.path.join(path, el, "content", "streams")):
# 		mms_list += [mms]
# print(mms_list)
#title_list = ['Episode 93: Alex Monteith', 'Episode 92: Rangituhia Hollis', 'Episode 91: Martin Awa Clark Langdon, Rebecca Hobbs, Qiane Matata-Sipu', 'Episode 90: Laura Duffy And Aliyah Winter', 'Episode 88: Revisiting HADHAD Part 3: The schism of Liberalism', 'Episode 88: Revisiting HADHAD - Part 2: Language, Technology and Totalitarianism', 'Episode 88: Revisiting HADHAD part 1: Shooting the film, Horror as genre', 'Episode 87: an interview with M D Brown', 'Episode 89: Zack Steiner-Fox in conversation with Robbie Handcock', 'Episode 85: Never Waste A Crisis - a conversation with Judy Darragh, Ary Jansen, Lisa Reihana', 'Episode 84: an interview with Darcell Apelu', 'Episode 83 An Interview With John Walter', 'Episode 82: 2019 in review', 'Episode 81 Tanu Gago', 'Episode 80: An interview with Chevron Hassett', 'Episode 79 Serena Bentley', 'Episode 78: an interview with Alex Monteith', 'Episode 77: New strategies for Auckland Galleries', 'Episode 76: Auckland Art Fair 2019', 'Episode 75: An interview with Peter Wareing', 'Episode 74: An interview with Luke Fowler', 'Episode 73: Complicated Love - 2018 in review (part 1 Of 2)', 'Episode 73: Complicated Love - 2018 in review (part 2 Of 2)', 'CIRCUIT Cast re-post: George Clark on This is not film-making', 'Episode 72: An interview with Johan Grimonprez','Episode 71: 2017 End of Year wrap-up', 'Episode 70: PULSE/REPEAT, an interview with Priscilla Howe', 'Episode 69: Alexandre Larose', 'CIRCUIT Cast Episode 68: Tautai Pacific Arts / Christina Jeffery interview', 'Episode 67: an interview with Mercedes Vicente', 'Episode 66: Sam Hamilton', 'Episode 65: Fiona Amundsen', 'Episode 64: Acting Out', "Episode 63: Trudy Lane's Sunroom", 'Episode 62: Michael Nicholson', 'Episode 61: Common Ground with Mairi Gunn', "Episode 60: Cushla Donaldson's The Fairy Falls", "Episode 59: Jem Noble's Dream Dialects", 'Episode 58: Māoriland Film Festival - interview with Tainui Stephens', 'Episode 57: Trust Us Contemporary Art Trust', 'Episode 56: 2016 wrap up', 'Episode 55: Mike Heynes and Masons Screen', 'Episode 54: John Ward Knox', 'Episode 53: MEANWHILE Gallery', 'Episode 52: Coastline Paradox - Josette Chiang', 'Episode 51: Joyce Campbell', 'Episode 50: George Clark on Phantom Topologies', 'Episode 49: John Vea', 'Episode 48: Inhabiting Space', 'Episode 47: The Non-Living Agent', 'Episode 46: Janet Lilo', 'Episode 45: The Hoover Diaries', "Episode 44: Sonya Lacey's Infinitesimals", 'Episode 43: Auckland Art Fair', 'Episode 42: An interview with Clinton Watkins', 'Episode 41: An interview with Yuki Kihara', 'Episode 40: River of Fundament', 'Episode 39: Angela Tiatia survey at Māngere Arts Centre', 'Episode 38: Camille Henrot and high-tech Primitivism', 'Episode 37: Best of 2015', 'Episode 36: Sutthirat Supaprinya', "Episode 35: Writing Women's Experimental Film Histories", 'Episode 34: Blue Oyster Gallery', 'Episode 33: Digital timelines - an interview with Jae Hoon Lee', 'Episode 32: Demented Architecture', 'Episode 31: Christina Read on The Brain', 'Episode 30: Nova Paul (symposium preview #3)', 'Episode 29: Symposium preview #2 - an interview with Dirk De Bruyn', 'Episode 28: Symposium preview #1 - a conversation with Shannon Te Ao', 'Episode 27: Janine Randerson and Place Unmaking', 'Episode 26: Looking back to Zion - an interview with Bridget Reweti', 'Episode 25: Publications', 'Episode 24: "Smaller budgets, bigger ideas" - an interview with The Audio Foundation', 'Episode 23: An interview with Lisa Reihana', 'Episode 22: an interview with Billy Apple', 'Episode 21: Invisible Energy', 'Episode 20: The Performance Arcade', 'Episode 19: "Paintings to click by" - The Drowned World', 'Episode 18: Are you cuddling a Care Bear?', 'Episode 17: Tahi Moore and Light Show', 'Episode 16: An interview with Adnan Yildiz', 'Episode 15 - William Kentridge, Simon Denny, Gloria Knight', 'Episode 14 - Gavin Hipkins, Kim Paton, SPARK Festival', 'Episode 13 - Symposium interviews: George Clark, Simon Rees', 'Episode 12 - Kim Pieters, Terri Te Tau, Tonga i Onopooni: Tonga Contemporary', 'Episode 11 - Stuggorings and Fijetterings, MOAMOA, Art and Social Change', 'Episode 10 - Simon Starling, Maldives Exodus Caravan Show, Samin Son', 'Episode 9 - Sydney Biennale controversy, Cinema and Painting, Ken Jacobs', 'Episode 8 - Best of 2013', 'Episode 7 - Sound Full, MINA and Body Rock', 'Episode 6 - Francis Alys, Phil Dadson & CIRCUIT symposium', 'Episode 5 -Auckland Art Fair', 'Episode 4 - Beautiful Creatures, Pulp Fan Fiction and Online Sales', 'Episode 95: Connor Fitzgerald and Xi Li']
	
# for el in podcasts_dict:

# 	if podcasts_dict[el]["automated_flag"] ==True:
# 		my_list.append(el)
# print(my_list)
all_mms = []
podcasts = Podcast.select()#.where(Podcast.podcast_name == "Access Granted NZ")
for pod in podcasts:
	#!!!!!!!!!!Do not remove. Should be deleted from Alma!!!!!Love podcast and Dirt Church ['9919046572802836','9919046573002836']:
	#!!!!Back to the disc-player not in report
	#!!!Coronavirus podcast maybe 1 missing 49 in rss and 48 in report
	#The creative spear could not grab anything

	if  "Property"  in pod.podcast_name:
			# q = Podcast.update(serial_holding="22361981660002836").where(Podcast.id == pod.id)
			# q.execute()
	 #if pod.podcast_name  in ["76 small rooms"]:#Purpose fuelled performance',"Advanced analytics","UC science radio","Queenstown life","Windows on dementia","Animal matters","Selfie reflective", "The Angus Dunn"]:
	# #if pod.id == 109:
	#		print(pod.podcast_name)
			# print("#"*50)
			# print(pod.id)
			# print(pod.podcast_name)
			# print(pod.template_name)
			# print(pod.location)
			# print(pod.rss_link)
			# print(pod.serial_holding)
			# print(pod.location)
			# # print(pod.location)
			# print(pod.serial_pol)
			# # print(pod.last_issue)
			# 	# print(pod.location)
			# print(pod.serial_mms)
			# print(pod.serial_pol)

			episodes = Episode.select().where(Episode.podcast==pod.id)
			for ep in episodes:
				# print(ep.updated)
				if ep.mis_mms in ["9919157299102836"]:
				# if ep.episode_title.startswith("Everything You Need To Know About"):
					# mms_list+=ep.mis_mms
					print(ep.episode_title)
					print(pod.podcast_name)
					print(ep.mis_mms)
					print(ep.date_harvested)
					print(ep.ie_num)

					# print(dt.fromtimestamp(ep.date).strftime('%B %d %Y'))
					# print(ep.tick)
					# print(ep.sip)
					# print(ep.mis_mms)
					# print(ep.updated)
					# print(ep.ie_num)
					# print(ep.item)
					# q = Episode.update(ie_num=True).where(Episode.id==ep.id)
					# q.execute()
					# print(pod.serial_mms)



					# # print(ep.mis_mms)
					# print(ep.harvest_link)
					# print(ep.tick)
					# print(ep.f600_first)
					# print(ep.f610_first)
					# print(ep.f700_first)
					# print(ep.f700_second)
					# print(ep.f700_third)
					# # print(ep.f650_first)
					# # print(ep.f655)
					# print(ep.f710_first)
					# q = Episode.update(item=None).where (Episode.id==ep.id)
					# q.execute()


					# files = File.select().where(File.episode == ep.id)
					# for fl in files:
					# 	print(fl.filepath)
						


		# 				#if fl.md5sum == "7ee29280ef3ccca9769e622d7f630e23":
		# 				# if not  "f287913a-88eb-4d99-a224-c8a15e1df44a" in fl.filepath:
		# 				if len(files)>1:and pod.podcast_name not in fl.filepath:
		# 				# 	if "Purpose fuelled performance" in fl.filepath and pod.podcast_name == "Cooking the books":
		# 			# # 		
		# 			# # count+=1
		# 			# # 	#print("here")
		# 			# 	# if not "Dietary requirements" in fl.filepath:
		# 			# # 		print("here2")
		# 			# # 		print(ep.harvest_link)

								
		# 						print(ep.episode_title)
		# 						print(ep.id)
		# 						print(pod.podcast_name)
		# 						print(ep.mis_mms)
		# 						print(pod.serial_mms)
		# 						print(fl.filepath)
		# 						print(fl.filesize)
		# 						# if ep.episode_title in my_dict.keys():
		# 						# 	if not fl.filesize in my_dict[ep.episode_title]:
		# 						# 		my_dict[ep.episode_title] +=[fl.filesize]
		# 						# else:
		# 						# 	my_dict[ep.episode_title]=[fl.filesize]
		# 						# print(dt.fromtimestamp(int(ep.date)).strftime('%B %d %Y'))
		# 						# print(ep.harvest_link)

		# 			# 		# q = Episode.update(podcast = 102).where(Episode.id == ep.id)
		# 					# q.execute()
		# 					# q = File.update(filesize=os.path.getsize(fl.filepath)).where(File.id ==fl.id)
		# 					# q.execute()
		# 						# q= File.update(md5sum=r"Y:\ndha\pre-deposit_prod\LD_working\podcasts\files\CIRCUIT cast\pznO5UOwoFsa.128.mp3").where(File.id == fl.id)
		# 						# q.execute()
		# 					# q= File.update(filepath=r"Y:\ndha\pre-deposit_prod\LD_Proj\podcasts\files\Kiwi yarns\TIM_LIGHTBOURNE_SECOND_EDIT.mp3").where(File.id == fl.id)

		# 						# print(fl.filepath)
		# 						# # new_filename = "".join(fl.filepath.split("track_G799B1_static1_squarespace_com_static_5b958f42e2ccd190d7d93e8a_t_"))
		# 						# # q= File.update(filepath=new_filename).where(File.id == fl.id)
		# 						# # q.execute()	
		# 						# print(fl.filepath)
		# 						# print(os.path.getsize(fl.filepath))
		# # 					# 		print(fl.md5sum)
		# 					# 		print(fl.episode)
