import csv
import peewee
from datetime import datetime
from podcast_models import Podcast, Episode, File
import csv
import peewee
from peewee import *

# Assuming your database and model definitions are correctly set up as previously mentioned

def export_data_to_csv(csv_file_path="complete_podcasts_data.csv"):
    headers = [
        'Podcast Name', 'Serial MMS', 'Serial POL', 'Serial Holding', 'RSS Link', 'Location', 'Access Policy',
        'Publish Link To Record', 'Automated Flag', 'Last Issue', 'Template Name', 'Episode ID', 'Episode Title',
        'Subtitle', 'Description', 'Date', 'Episode Link', 'Tags', 'Date Harvested', 'Harvest Link', 'F100',
        'F600 First', 'F600 Second', 'F600 Third', 'F610 First', 'F610 Second', 'F610 Third', 'F650 First',
        'F650 Second', 'F650 Third', 'F650 Forth', 'F655', 'F700 First', 'F700 Second', 'F700 Third', 'F710 First',
        'F710 Second', 'F710 Third', 'Tick', 'MIS MMS', 'SIP', 'MIS POL', 'Holdings', 'Item', 'Receive', 'IE Num',
        'Epis Numb', 'Epis Seas', 'Updated', 'File ID', 'File Path', 'MD5 Sum', 'MD5 From Site', 'File Type',
        'File Size', 'Size Original'
    ]

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()

        for pod in Podcast.select():
            for ep in Episode.select().where(Episode.podcast == pod):
                files = File.select().where(File.episode == ep)
                for fl in files:
                    row = {
                        'Podcast Name': pod.podcast_name, 'Serial MMS': pod.serial_mms, 'Serial POL': pod.serial_pol,
                        'Serial Holding': pod.serial_holding, 'RSS Link': pod.rss_link, 'Location': pod.location,
                        'Access Policy': pod.access_policy, 'Publish Link To Record': pod.publish_link_to_record,
                        'Automated Flag': pod.automated_flag, 'Last Issue': pod.last_issue, 'Template Name': pod.template_name,
                        'Episode ID': ep.id, 'Episode Title': ep.episode_title, 'Subtitle': ep.subtitle,
                        'Description': ep.description, 'Date': ep.date, 'Episode Link': ep.episode_link,
                        'Tags': ep.tags, 'Date Harvested': ep.date_harvested, 'Harvest Link': ep.harvest_link,
                        'F100': ep.f100, 'F600 First': ep.f600_first, 'F600 Second': ep.f600_second,
                        'F600 Third': ep.f600_third, 'F610 First': ep.f610_first, 'F610 Second': ep.f610_second,
                        'F610 Third': ep.f610_third, 'F650 First': ep.f650_first, 'F650 Second': ep.f650_second,
                        'F650 Third': ep.f650_third, 'F650 Forth': ep.f650_forth, 'F655': ep.f655,
                        'F700 First': ep.f700_first, 'F700 Second': ep.f700_second, 'F700 Third': ep.f700_third,
                        'F710 First': ep.f710_first, 'F710 Second': ep.f710_second, 'F710 Third': ep.f710_third,
                        'Tick': ep.tick, 'MIS MMS': ep.mis_mms, 'SIP': ep.sip, 'MIS POL': ep.mis_pol,
                        'Holdings': ep.holdings, 'Item': ep.item, 'Receive': ep.receive, 'IE Num': ep.ie_num,
                        'Epis Numb': ep.epis_numb, 'Epis Seas': ep.epis_seas, 'Updated': ep.updated,
                        'File ID': fl.id, 'File Path': fl.filepath, 'MD5 Sum': fl.md5sum, 'MD5 From Site': fl.md5from_site,
                        'File Type': fl.file_type, 'File Size': fl.filesize, 'Size Original': fl.size_original
                    }
                    writer.writerow(row)

    print(f"Data successfully exported to {csv_file_path}")

if __name__ == '__main__':
    export_data_to_csv()
