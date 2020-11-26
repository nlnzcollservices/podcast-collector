#How_to_add_a_new_podcast
## Table of Contents
1. [Preparation](#preparation)
2. [Methods of obtaining a template from ExLibris Alma](#methods)
3. [Add inforamtion to podcast dictionary](#podcast-dictionary-population)
4. [Collaboration](#collaboration)
5. [FAQs](#faqs)
## Methods of obtaining a template from ExLibris Alma
***
There are 3 ways to download a template:
### Alma Enhancer and Tampermonkey FireFox add-on.
File download MARK as XML option 
Save the template in “assets”, “text templates” folder 
Run   text_to_xml.py script from the script folder
Check and copy the template to “assets”, “templates” folder
### Alma 
Create a record from a template
Add 245 field
Save the record
Create a set from the records
Run a job to import a set
Separate the templates and save them by their own names in “assets”, “templates” folder
Delete all the records.
### Possible half python, half Alma  way.
Create a record
Add 245 field
Save the record
Keep the mms id.
Use python script:
Get the records by mms via get API.
Save them as template in “assets”, “templates” folder
Delete the records by mms vie delete API.

This script is aimed to harvest podcasts' episodes based on rss feed, collect metadata, make and  update bibliographic records with enriched metadata in Exlibris Alma, prepare SIPs for Exlibris Rosetta and manage submitted episodes.
### Add inforamtion to podcast dictionary
***
Open podcasts_dict.py  and add to podcast_dict variable the podcast metadata in the following format
'''
"podcast_name:{"rss_filename":"link","url":"link","serial_mms":"99…", "serial_pol":"pol-…","publish_link_ro_record":True, "automated_flag":False,"access_policy":"100", "template":"template_name.xml"}
'''
publish_link_to_record  should be turned False  if it should be concealed from public
automated_flag should be turned True if there is no cataloguing corrections required.
access policy should be turned 200 for restricted access.

## Make necessary changes in Alma record creating rools
***
Open podcasts1_create.py
Think how the title will be parsed depending if it contains episode number , season or other information not wishable for 245 marc field and add the podcast name to
existing rules or create your own.
Example:
'''
		if self.podcast_name in ["Advanced analytics"]:
			if ":" in self.episode_title:
				f245 = self.episode_title.split(":")[-1].lstrip(" ")
				f490v = self.episode_title.split(":")[0].rstrip(" ")
				f830v = str(f490v)
'''
The above script is taking all episode titles for podcast with the name "Podcast analytics" which is sometimes originally in the following format
"S3 E23: The Last Dance Ep1 NO SPOILERS!". The above script takes all the part after the colon for 245 field and first part for 490 and 830 (or 810 depends which one in the template) field.

## Possible rules for harvester and troubleshoting.
***
After running the podcast.py script there are could be some errors or things to adjust in podcsats0_harvester.py script. 
A few rules are added here as well.
Example:
'''
					if self.podcast_name in ["Top writers radio show", "Dont give up your day job"]:
						self.episode_link = ""
'''
The above scipt is setting episode_links for these to podcsats as empty sting "". As it does not exist in rss feed
