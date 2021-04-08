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
import os
my_files = []

# time  = mktime(dt.strptime("Nov 06 2019", "%b %d %Y").timetuple())

# q = Podcast.update(last_issue= time).where(Podcast.podcast_name == "Hauraki drive")
# q.execute()

# q = Podcast.update(rss_link= "https://www.spreaker.com/show/2825204/episodes/feed").where(Podcast.podcast_name == "Bhuja podcast")
# q.execute()
# # # q = File.delete().where(File.filepath == r"Y:\NDHA\pre-deposit_prod\LD_Proj\podcasts\files\Business is boring\media-keuo4y6f-bib_zincovery_jonathan_ring_090920.mp3")
# # # q.execute()
# q = Episode.delete().where(Episode.podcast == 110)
# q.execute()
# # #q = File.update(filepath = "D:\\Documents\\2019_Projects\\Pawaii\\podscasts_regular\\files\\Crave!\\crave080.mp3").where(File.id == 166)
# #q.execute()

# q = Podcast.update(rss_link = "https://www.spreaker.com/show/4359300/episodes/feed").where(Podcast.podcast_name == "Bosses in lockdown")
# q.execute()



# q = Podcast.update(serial_pol = "POL-129320").where(Podcast.serial_pol == "POL-129320 ")
# q.execute()

#q = Podcast.update(podcast_name = "True crime New Zealand").where(Podcast.podcast_name == "True crime New Zealand : a NZ crime podcast")
#q.execute()


# q = Episode.update(podcast = 101).where(Episode.podcast==37)
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


	# os.rename(os.path.join(dire,el), "".join(os.path.join(dire,el).split("track_G799B1_static1_squarespace_com_static_5b958f42e2ccd190d7d93e8a_t_")))
count =0
podcasts = Podcast.select()#.where(Podcast.podcast_name == "Access Granted NZ")
for pod in podcasts:
	#!!!!!!!!!!Do not remove. Should be deleted from Alma!!!!!Love podcast and Dirt Church ['9919046572802836','9919046573002836']:
	#!!!!Back to the disc-player not in report
	#!!!Coronavirus podcast maybe 1 missing 49 in rss and 48 in report
	#The creative spear could not grab anything
	#if pod.podcast_name in ["Dont give up your day job","Stirring the pot","You're gonna' die in bed"]:
	#if pod.podcast_name not in ["DOC sounds of science podcast","Every stupid question", "Taringa", "Crave!","Seeds","B-side stories","Advanced analytics","All Blacks","On the rag","Business is boring","The real pod","Papercuts","The Offspin podcast","Musician's Map","Stirring the pot","Ciaran McMeeken","Indigenous Urbanism","Plunket parenting","Alchemy","Never Repeats podcast","The Rubbish trip","Chris and Sam podcast","A moment in crime","Human-robot interaction podcast","Actually interesting","Ardie Savea podcast","Back to the disc-player podcast","Better off read","Boners of the heart podcast","Breeder's digest","CIRCUIT cast","Coronavirus NZ","Coronavirus podcast","Cult popture","Dietary requirements","Dont give up your day job","Dirt Church Radio","Frogshark podcast","Gone by lunchtime","History of Aotearoa New Zealand podcast","Hosting","How to save the world","Just me being me no apology","Love this podcast","NZ tech podcast with Paul Spain","Phoenix city","Polidicks","Snacks and chats","Stupid Questions for Scientists","Taxpayer talk","The Frickin Dangerous Bro Show","The creative spear","The fold","The good citizen","The good timeline","The lip","The male gayz","The watercooler","The worst idea of all time","Top writers radio show","True crime New Zealand","Walk out boys","Retrogasmic","A Neesh audience","Animal matters","Book bubble","Democracy Project","Goodfellow podcast","Selfie reflective","The Angus Dunn","UC science radio"]:
	#if "NBL" in pod.podcast_name:#The Best Sequ
#1604745343 -c
# 1611153244
	#if pod.podcast_name in ["Going viral"]:
	if pod.id == 117:
	
			print("#"*50)
			print(pod.id)
			print(pod.podcast_name)
			print(pod.rss_link)
			# # print(pod.location)
			# # print(pod.serial_pol)
			# # print(pod.last_issue)
			# 	# print(pod.location)
			# print(pod.serial_mms)
			# print(pod.serial_pol)
			# print(podcasts_dict[pod.podcast_name]["template_name"])

			# q=Podcast.update(last_issue = 1615827600).where(Podcast.id ==pod.id)
			# q.execute()
			# try:
			# q= Podcast.update(template_name= "mis_Podcast_Library_loudhailer.xml").where(Podcast.id ==pod.id )
			# q.execute()
			# except KeyError:
			# 	pass
			#print(pod.last_issue)
			# print(dt.fromtimestamp(int(pod.last_issue)).strftime('%B %d %Y'))
# 			print(pod.rss_link)
# # 			print(pod.template_name)


# # # 		#if pod.podcast_name in ["CIRCUIT cast"]:
			episodes = Episode.select().where(Episode.podcast==pod.id)
			for ep in episodes:
					print(ep.episode_title)
					# new_title = re.sub('[(\U0001F600-\U0001F92F|\U0001F300-\U0001F5FF|\U0001F680-\U0001F6FF|\U0001F190-\U0001F1FF|\U00002702-\U000027B0|\U0001F926-\U0001FA9F|\u200d|\u2640-\u2642|\u2600-\u2B55|\u23cf|\u23e9|\u231a|\ufe0f)]+','',ep.episode_title)
					# new_title = new_title.rstrip(" ")
					# # q= Episode.update(episode_title = new_title).where(Episode.id == ep.id)
					# q.execute()
					print(ep.description)
					# new_description = re.sub('[(\U0001F600-\U0001F92F|\U0001F300-\U0001F5FF|\U0001F680-\U0001F6FF|\U0001F190-\U0001F1FF|\U00002702-\U000027B0|\U0001F926-\U0001FA9F|\u200d|\u2640-\u2642|\u2600-\u2B55|\u23cf|\u23e9|\u231a|\ufe0f)]+','',ep.description)
					# new_description = new_description.rstrip("")
					# q= Episode.update(description = new_description).where(Episode.id == ep.id)
					# q.execute()
				# 	print(ep.episode_link)
				# 	print(ep.harvest_link)
				# # if ep.date<  mktime(dt.strptime("Apr 06 2020", "%b %d %Y").timetuple()):
				# 	print(dt.fromtimestamp(int(ep.date)).strftime('%B %d %Y'))
					# print(ep.harvest_link)
					# print(ep.episode_link)
				#if ep.id == 7258:
# 				#!!!!!!!!!!Do not remove. Should be deleted from Alma!!!!!Love podcast and Dirt Church ['9919046572802836','9919046573002836']:
# 				# 	print(pod.podcast_name)
				# if "Bosses in Lockdown:" in ep.episode_title:

				# if "The importance of diversity and inclusion" in ep.episode_title:
					# q = Episode.update(podcast = 110).where(Episode.id == ep.id)
					# q.execute()
		# # 		
					#print(count)
# 				#if ep.id in list(range(4817,4913)):
# # 				#if ep.id in [4198]:
# 				#if ep.sip:# and ep.mis_mms in mms_list:
# # # 				#print(ep.mis_mms)
# # # 				#if ep.mis_mms and ep.sip == False:
# # # 				#if ep.mis_mms in mis_mms_list:
# 			#		print("!!!!!!!!!!!!!!!!!!!!!!!!")
					# print(pod.podcast_name)
					

					# print(ep.date)
					# # # print(ep.ie_num)
					# # # print(ep.sip)
					# # # print(ep.item)

					# print(ep.tick)
					# q = Episode.update(sip=False).where(Episode.id == ep.id)
					# q.execute()

					#print(ep.mis_mms)
# # 					print(ep.id)
# 					#print(ep.mis_mms)
# # 					print(ep.sip)
# # # # 					print(ep.description)
# # # # 					print(ep.episode_link)
# # # 					print(ep.harvest_link)




					files = File.select().where(File.episode == ep.id)
					for fl in files:
						#if "files\Bhuja podcast" in fl.filepath:
							# q = Episode.update(podcast = 102).where(Episode.id == ep.id)
							# q.execute()
							# q = File.update(filesize=os.path.getsize(fl.filepath)).where(File.id ==fl.id)
							# q.execute()
							# q= File.update(filepath=r"Y:\ndha\pre-deposit_prod\LD_working\podcasts\files\New Zealand Initiative\OH_Magic_Talk_ETS_1_Feb2_021.mp3").where(File.id == fl.id)
							# q.execute()
							# q= File.update(filepath=r"Y:\ndha\pre-deposit_prod\LD_Proj\podcasts\files\Kiwi yarns\TIM_LIGHTBOURNE_SECOND_EDIT.mp3").where(File.id == fl.id)
							# q.execute()
							# print(fl.filesize)
							print(fl.filepath)
							# # new_filename = "".join(fl.filepath.split("track_G799B1_static1_squarespace_com_static_5b958f42e2ccd190d7d93e8a_t_"))
							# # q= File.update(filepath=new_filename).where(File.id == fl.id)
							# # q.execute()	
							# print(fl.filepath)
							# print(os.path.getsize(fl.filepath))
# # 					# 		print(fl.md5sum)
# 					# 		print(fl.episode)

