
#How to add a new podcast guide

## Table of Contents
1. [Preparation](#preparation)
2. [Methods of obtaining a template from ExLibris Alma](#methods-of-obtaining-a-template-from-exLibris-alma)
3. [Adding inforamtion to podcast dictionary](#adding-inforamtion-to-podcast-dictionary)
4. [Making necessary changes to Alma record creating rools](#making-necessary-changes-to-alma-record-creating-rools)
5. [Possible rules for harvester and troubleshooting](#possible-rules-for-harvester-and-troubleshooting)

## Preparation
***
This podcast pipeline is based on information obrained from rss feeds. So existance of rss link is important. Though it is possible to use the script for podcasts without rss link, it require some manual data entry to google spreadsheet for each episode amd running an additional script afterwords each time.
Before starting the process of adding a new podcast make sure that the new podcast already has a serial record, purchase order attached to it and template in Alma.
## Methods of obtaining a template from ExLibris Alma
***
There are 3 (or more) ways to download a template:
#### Alma Enhancer and Tampermonkey FireFox add-on. 
Alma Enhancer is internal script so if you are  not in the Library use other methods.
Otherwise install Tampermonkey FireFox add-on.
Add Alma Enchancer script from Alma Enhancement Scripts folder to Tampermonkey(create new script and copy content of the files from the folder)
Use file download MARK as XML option.
Save the template in “assets”, “text templates” folder. 
Run   **text_to_xml.py** script from the script folder.
Check and copy the template to “assets”/“templates” folder.
#### Alma 
Create a record from a template
Add 245 field.
Save the record.
Create a set from the records.
Run a job to import a set
Separate the templates and save them by their own names in “assets”/“templates” folder.
Delete all the records.
#### Possible half python, half Alma  way.
Create a record
Add 245 field
Save the record
Keep the mms id.
Use python:
Get the records by mms via get API.
Save them as template in “assets”/“templates” folder.
Delete the records by mms via delete API or manually from GUI.

## Adding inforamtion to podcast dictionary
***
Open podcasts_dict.py  and add to podcast_dict variable the podcast metadata in the following format
```
"podcast_name:{"rss_filename":"link","url":"link","serial_mms":"99…", "serial_pol":"pol-…","publish_link_ro_record":True, "automated_flag":False,"access_policy":"100", "template":"template_name.xml"}
```
* Don't add special characters e.g. macrons in the the podcast_name value
* publish_link_to_record  should be turned False  if it should be concealed from public;
* automated_flag should be turned True if there is no cataloguing corrections required;
* access policy should be turned 200 for restricted access

## Making necessary changes to Alma record creating rools
***
Sometimes original title contains episode number and season. In this case to make a correct record in fields 245,490 and 830(810) new rules should be created.
Open **podcasts1_create_record.py** and add the podcast title to existing rules, if they are suit or create your own using the following example.
Example:
```
	if self.podcast_name in ["Advanced analytics"]:
		if ":" in self.episode_title:
			f245 = self.episode_title.split(":")[-1].lstrip(" ")
			f490v = self.episode_title.split(":")[0].rstrip(" ")
			f830v = str(f490v)
```
The above script is taking all episode titles for podcast with the name "Advanced analytics" which is sometimes originally in the following format
_"S3 E23: The Last Dance Ep1 NO SPOILERS!"_. The above script takes all the part after the colon for 245 field and first part for 490 and 830 (or 810 depends which one in the template) field.

## Possible rules for harvester and troubleshooting
***
After running the podcast.py script there are could be some errors or things to adjust in **podcsats0_harvester.py** script. 
A few rules can be and sometimes have to be added here as well.
Example:
```
		if self.podcast_name in ["Top writers radio show", "Dont give up your day job"]:
			self.episode_link = ""
```
*The above scipt is setting episode_links for these to podcsats as empty sting "". As it does not exist in rss feed*
