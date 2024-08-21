# Podcast Collector
## Table of Contents
1. [Project description](#project-description)
2. [Technologies](#technologies)
3. [Installation](#installation)
4. [Collaboration and integration](#collaboration-and-integration)
5. [FAQs](#faqs)
## Project description
***
This pipeline is used by the legal deposit team at the National Library of New Zealand to collect podcasts in scope for New Zealand legal deposit.
It monitors podcast RSS feeds to collect the audio files for new episodes and descriptive metadata about them. 

For some podcast titles, the pipeline then presents the harvested metadata for each episode to our cataloguers using a Google Sheet, allowing them to enrich the metadata before further automated processing. For other podcast titles, this manual enrichment step is not required.

Records for the newly-collected episodes are then created in Alma and submission information packages (SIPs) are created for ingest to Rosetta.

### Pipeline
![Podcasts](/documentation/Podcasts.png)
## Technologies
***
A list of technologies used within the project:
* [Python](https://www.python.org/downloads/release/python-370/): Version  3.7.2 
* [Google Spreadsheets APIs](https://developers.google.com/sheets/api/quickstart/python): Version current
* [AlmaTools](https://github.com/nlnzcollservices/alma-tools): Vesion 3
* [Exiftool](https://exiftool.org/): Version 12.10
* [PyExifTool](https://smarnach.github.io/pyexiftool/) : Version 0.1.1


## Installation
***

Make sure that you installed all the modules and tools specified in the previous section. 

Exiftool and Jhove should be able to be called from command line. (If not make sure that the folders with these tools is in your path. Use sysdm.cpl for Windows)  

To enable requests to the Google Sheets API, you should get your own credentials stored in a client_secrets.json file. (See--Quickstart link in technology section above)

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
Change all the full paths to yours

Folders where Exlibris Rosetta takes the SIPs from production and sandbox in the setting paths section
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
Save it, close and run. (It will create a project folder tree)
```
$ python settings.py
```
Move modified with your keys for Alma and Google Sheets secret file to  "path\to\your\secret\folder"
```
$ cd ..
$ move secrets "path\to\your\secret\folder"

```
Make sure that your client_secrets.json file is also in the same folder

Run podcasts_models.py to create db.

```
$ cd scripts
$ python podcasts_models.py

```
Cross fingers and run!
```
$ python podcasts.py
```
## Collaboration and integration

It is also possible to attach other scripts to the existing pipline. 
It could be useful for backlogs or for those podcasts which do not have rss feeds.
For this purpose should be written anoter python website harvester which should do the next actions:
- manages to download files to existing "files" folder structure;
- populates existing __podcsat.db__ (use  _DbHandler.table_creator(talbe_name, {table_data})_ method in __database_handler.py__);
- inserts rows to the existing google spreadsheet. See example from __podcasts0_harvester.py__ bellow.
```
c = gspread.authorize(creds)
gs = c.open_by_key(podcast_sprsh)
ws = gs.get_worksheet(0)
...
ws.append_row([podcast_name, serial_mms, "",episode_title, description, episode_link, episode_date in'%B %d %Y'format, tags, episode_download_link])
 ```
 See also 
 ![google_spreadsheet_requirements.md](/documentation/google_spreadsheet_requirements.md)
 
		







