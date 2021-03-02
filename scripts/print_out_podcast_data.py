import peewee
import requests

from podcast_models import Podcast, Episode, File
from datetime import datetime as dt
from time import mktime
import datetime as DT
from datetime import time
from bs4 import BeautifulSoup as bs
from podcast_dict import podcasts_dict
import os
my_files = []

# time  = mktime(dt.strptime("Jan 02 1971", "%b %d %Y").timetuple())

# q = Podcast.update(last_issue= 1593604800).where(Podcast.podcast_name == "Taringa")
# q.execute()


# # # q = File.delete().where(File.filepath == r"Y:\NDHA\pre-deposit_prod\LD_Proj\podcasts\files\Business is boring\media-keuo4y6f-bib_zincovery_jonathan_ring_090920.mp3")
# # # q.execute()
# q = Episode.delete().where(Episode.id == 3968)
# q.execute()
# # #q = File.update(filepath = "D:\\Documents\\2019_Projects\\Pawaii\\podscasts_regular\\files\\Crave!\\crave080.mp3").where(File.id == 166)
# #q.execute()

# q = Episode.update(mis_mms = "9919046572902836").where(Episode.episode_title == "Episode 127 - Ian Evans")
# q.execute()
# 


# q = Podcast.update(serial_pol = "POL-119744").where(Podcast.podcast_name == "Gone by lunchtime")
# q.execute()

#q = Podcast.update(podcast_name = "True crime New Zealand").where(Podcast.podcast_name == "True crime New Zealand : a NZ crime podcast")
#q.execute()


# q = Episode.update(sip = False).where(Episode.id==4320)
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


	if pod.podcast_name == "Selfie reflective":

			print("#"*50)
			print(pod.id)
			print(pod.podcast_name)
				# print(pod.location)
				# print(pod.serial_mms)
				# print(pod.serial_pol)
			# print(podcasts_dict[pod.podcast_name]["template_name"])

			# q=Podcast.update(last_issue = mktime(dt.strptime("26 September 2019", "%d %B %Y").timetuple())).where(Podcast.id ==pod.id)
			# q.execute()
			# try:
			# 	q= Podcast.update(location= podcasts_dict[pod.podcast_name]["url"]).where(Podcast.id ==pod.id )
			# 	q.execute()
			# except KeyError:
			# 	pass
			#print(pod.last_issue)
			# print(dt.fromtimestamp(int(pod.last_issue)).strftime('%B %d %Y'))
			# print(pod.rss_link)
			# print(pod.template_name)


# 		#if pod.podcast_name in ["CIRCUIT cast"]:
			episodes = Episode.select().where(Episode.podcast==pod.id)
			for ep in episodes:

				#!!!!!!!!!!Do not remove. Should be deleted from Alma!!!!!Love podcast and Dirt Church ['9919046572802836','9919046573002836']:
				# 	print(pod.podcast_name)

				#if ep.episode_title "Gaytravaganza" in ep.episode_title:
					# q = Episode.update(mis_mms = '9919046572702836').where(Episode.id == ep.id)
					# q.execute()
			# 		print(count)
				#if ep.id in list(range(4817,4913)):
# 				#if ep.id in [4198]:
				#if ep.sip:# and ep.mis_mms in mms_list:
# # 				#print(ep.mis_mms)
# # 				#if ep.mis_mms and ep.sip == False:
# # 				#if ep.mis_mms in mis_mms_list:
			#		print("!!!!!!!!!!!!!!!!!!!!!!!!")
					print(ep.episode_title)
					print(ep.mis_mms)
# 					print(ep.id)
					#print(ep.mis_mms)
# 					print(ep.sip)
# # # 					print(ep.description)
# # # 					print(ep.episode_link)
# # 					print(ep.harvest_link)




# 					files = File.select().where(File.episode == ep.id)
# 					for fl in files:
# 						# if fl.filepath == r"Y:\ndha\pre-deposit_prod\LD_Proj\podcasts\files\The worst idea of all time\media-kl7g4rtt-twioat_s5e21_-_emmanuelle_in_space_7_v2.mp3":
# # 						# 	q = File.update(filesize=os.path.getsize(fl.filepath)).where(File.id ==fl.id)
# # 						# 	q.execute()
# # 							print(fl.filesize)
# 							print(fl.filepath)
# # 							print(os.path.getsize(fl.filepath))
# # 					# 		print(fl.md5sum)
# 					# 		print(fl.episode)

