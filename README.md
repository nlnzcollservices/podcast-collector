#Podcasts
## Table of Contents
1. [General Info](#general-info)
2. [Technologies](#technologies)
3. [Installation](#installation)
4. [Collaboration](#collaboration)
5. [FAQs](#faqs)
## General Info
***
This script is aimed to harvest podcasts' episodes based on rss feed, collect metadata, make and  update bibliographic records with enriched metadata in Exlibris Alma, prepare SIPs for Exlibris Rosetta and manage submitted episodes.
### Pipeline
![Podcasts](/documentation/Podcasts.png)
## Technologies
***
A list of technologies used within the project:
* [Python](https://www.python.org/downloads/release/python-370/): Version  3.7.2 
* [Google Spreadsheets APIs](https://developers.google.com/sheets/api/quickstart/python): Version current
* [JHOVE](https://jhove.openpreservation.org/getting-started/): Vesion Rel. 1.24.1
* [Exiftool](https://exiftool.org/): Version 12.10
* [PyExifTool](https://smarnach.github.io/pyexiftool/) : Version 0.1.1
* [Downloader](https://github.com/nlnzcollservices/file-downloader): Version downloader_light_modified
* [Rosetta sip factory](https://github.com/NLNZDigitalPreservation/rosetta_sip_factory): Version 0.1.9
* [beautifulsoup4](https://https://www.crummy.com/software/BeautifulSoup/bs4/doc/): Version 4.9.1
* [configparser](https://docs.python.org/3/library/configparser.html): Version 5.0.0
* [dateparser](https://pypi.org/project/dateparser/): Version 0.7.6
* [feedparser](https://pypi.org/project/feedparser/): Version 5.2.1
* [gspread](https://gspread.readthedocs.io/en/latest/): Version 3.6.0
* [httplib2](https://pypi.org/project/httplib2/): Version 0.18.1
* [lxml](https://pypi.org/project/lxml/): Version 4.5.2
* [nltk](https://pypi.org/project/nltk/): Version 3.5
* [openpyxl](https://pypi.org/project/openpyxl/): Version 3.0.4
* [peewee](http://docs.peewee-orm.com/en/latest/): Version 3.13.3
* [pymarc](https://pypi.org/project/pymarc/): Version 4.0.0
* [requests](https://pypi.org/project/requests/): Version 2.24.0
* [urllib3](https://pypi.org/project/urllib3/): Version 1.25.9

## Installation
***

Make sure that you installed all the modules and tools specified in the previous section. 

Exiftool and Jhove should be able to be called from command line.(If not make sure that the foldeers with these tools is in your path. Use sysdm.cpl for Windows)  

You have your own client_secrets.json file as result of the process of enabling requests to the Google Sheets API. (Quickstart link is above in technology section)

Clone the repository from GitHub. 
```
$ git clone https://github.com/nlnzcollservices/podcasts
```
Enter the scripts directory
```
$ cd podcasts/scripts
```
Open settings.py for editing (for cmd)
```
$ notepad settings.py
```
Change all the full paths on yours

Folders where Exlibris Rosetta takes the SIPs from production and sandbox in setting path section
```
rosetta_folder = r"your\production\Rosetta\path"
rosetta_sb_folder = r"your\sandbox\Rosetta\path"
```
Folder with Downloader in git section
```
git_folder = r"your_git_path\file-downloader"
```
Folder with secrets in credentials section
```
secrets_and_credentials_fold = r'path\to\your\secret\folder'
```
Save it. Close.
Move modified with your keys for Alma and Google Sheets secret file to  "path\to\your\secret\folder"
```
$ cd ..
$ move secrets "path\to\your\secret\folder"

```
Make sure that your client_secrets.json file is also in the same folder

Fingers crossed and run it.
```
$ cd scripts
$ python podcasts.py
```
## Collaboration
***
Ideas how to collaborate.
> quote. 


## FAQs
***
A list of frequently asked questions
1. **First question**
_Answer_ 


