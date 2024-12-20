import peewee
import os
import csv
import requests
from podcast_models import Podcast, Episode, File
from datetime import datetime as dt
from time import mktime
import datetime as DT
from datetime import time
import dateparser
from bs4 import BeautifulSoup as bs
from podcast_dict import podcasts_dict
# from settings import logging, database_content_filename


# logger = logging.getLogger(__name__)


class DbHandler():

    """
        This class manages database operations.

        Attributes
        ----------

        my_id (str) - id in db table
        self.req_list (list) - list of fields required
        self.returning (bool) - used in reading_db method, set True by defaul meaning that returns back list of dictionaries from db
        self.podcast_name (str) - podcast name
        self.serial_mms (str) - serial mms
        self.serial_pol (str) - serial_pol
        self.rss_link (str) - rss link
        self.location (str) - podcast link
        self.access_policy (str) - access policy normally set 100 for open source
        self.publish_link_to_record (bool) - gives a chance to hide link to the episodes of particular podcast. Set True by default.
        self.automated_flag (bool) - could process podcast without writing to spreadsheet. Set False by default.
        self.last_issue (int) - timestamp  from the date of the last issue harvested
        self.episode_title (str) - episode_title
        self.subtitle (str) - eposode subtitle
        self.bib_title (str) - splitted part of rss title, which will go to 245
        self.bib_numbering (str) - splitted part of rss title, which will go to additional 520 a
        self.description (str) - episode description
        self.date (int) - timestamp for episode published date 
        self.episode_link(str) - link to episode
        self.tags(str) - tags if exist
        self.date_harvested(int) - timestamp for date when podcast was harvested
        self.harvest_link (str) - link to download mp3 
        self.f600_first (str) - metadata for 600 field from spreadsheet
        self.f600_second (str) - metadata for 600 field from spreadsheet
        self.f600_third (str) - metadata for 600 field from spreadsheet
        self.f610_first (str) - metadata for 610 field from spreadsheet
        self.f610_second (str) - metadata for 610 field from spreadsheet
        self.f610_third (str) - metadata for 610 field from spreadsheet
        self.f650_first (str) - metadata for 650 field from spreadsheet
        self.f650_second (str) - metadata for 650 field from spreadsheet
        self.f650_third (str) - metadata for 650 field from spreadsheet
        self.f650_forth (str) - metadata for 650 field from spreadsheet
        self.f655(str) - metadata for 655 field from spreadsheet
        self.f700_first (str) - metadata for 700 field from spreadsheet
        self.f700_second (str) - metadata for 700 field from spreadsheet
        self.f700_third (str) - metadata for 700 field from spreadsheet
        self.f710_first (str) - metadata for 710 field from spreadsheet
        self.f710_second (str) - metadata for 710 field from spreadsheet
        self.f710_third (str) - metadata for 710 field from spreadsheet
        self.tick (bool) - could be set False if metadata was not updated with cataloguing information manually entered to the spreadsheet or True after updating
        self.cataloguer (str) - name of a person, who is working on the episode
        self.mis_mms (str) - mono in series mms id
        self.mis_pol (str) - PO_line
        self.holdings (str) - holding id
        self.item (str) - item pid
        self.receive (bool) - set True after item is received
        self.ie_num (str) - ie number after injesting to Rosetta
        self.filepath (str) - path to downloaded file
        self.md5sum (str) - fixity
        self.md5from_(str) - original fixity if exists
        self.file_type (str) - file type (extension)
        self.full_dict (dict) - contains full information from db for particular episode
        self.returning_dict (dict) - contains information from db with required fields only
        self.returning_list (list) - contains dictionaries wwith required information about episodes


        Methods
        -------
        delete_done_from_db(self)
        get_podcast_id(self, podcast_name)
        table_creator(self, table, my_data)
        update_from_spreadsheet(self, episode_title, bib_title, bib_numbering, description,  f600_first, f600_second, f600_third, f610_first, f610_second, f610_third, f650_first, f650_second, f650_third, f650_forth, f655_first, f700_first, f700_second, f700_third,  f710_first, f710_second, f710_third, tick, cataloguer)
        update_the_last_issue(self)
        insert_the_last_issue(self, podcast_name, last_issue)
        ticked_titles(self)
        db_update_ie(self, ie_num, episode_id)
        db_update_holding(self, mms_id, holding_id)
        db_update_updated(self, mms_id)
        db_update_item_id(self, mms_id, item_pid)
        db_update_mms(self, mms_id, episode_title)
        db_update_sip(self, episode_title)
        db_reader(self, req_list, podcast_names=None, returning=True)

    """


    def __init__(self):

        self.my_id = None
        self.req_list = None
        self.returning = None
        self.podcast_name = None
        self.serial_mms = None
        self.serial_pol = None
        self.rss_link = None
        self.location = None
        self.access_policy = None
        self.publish_link_to_record = None
        self.automated_flag = None
        self.last_issue = None
        self.podcast = None
        self.episode_title = None
        self.subtitle = None
        self.bib_title = None
        self.bib_numbering = None
        self.description = None
        self.date = None
        self.episode_link = None
        self.tags = None
        self.date_harvested = None
        self.harvest_link = None
        self.f600_first = None
        self.f600_second = None
        self.f600_third = None
        self.f610_first = None
        self.f610_second = None
        self.f610_third = None
        self.f650_first = None
        self.f650_second = None
        self.f650_third = None
        self.f650_forth = None
        self.f655 = None
        self.f700_first = None
        self.f700_second = None
        self.f700_third = None
        self.f710_first  = None 
        self.f710_second = None
        self.f710_third = None
        self.tick = None
        self.cataloguer = None
        self.mis_mms = None
        self.mis_pol = None
        self.holdings = None
        self.item = None
        self.receive = None
        self.ie_num = None
        self.episode = None
        self.filepath = None
        self.md5sum = None
        self.md5from_site = None
        self.file_type = None
        self.full_dict = {}
        self.returning_dict = {}
        self.returning_list = []
        self. podcast_names = None
        if self.podcast_names:
            self.podcast_names = podcast_namess
        else: 
            self.podcast_names = podcasts_dict.keys()

    def delete_done_from_db(self):

        episodes = Episode.select()
        for epis in episodes:
            if epis.item and epis.holdings and epis.ie_num and epis.updated:
                q = File.delete().where(File.episode == epis.id)
                q.execute()
                q = Episode.delete().where(Episode.id == epis.id)
                q.execute()

    def get_podcast_id(self, podcast_name):

        podcasts= Podcast.select().where(Podcast.podcast_name == podcast_name)
        for podcast in podcasts:
            return podcast.id

    def table_creator(self, table, my_data):

        logger.info("create table {}".format(table))
        logger.info(my_data)
        if table == "Podcast":
            my_id = Podcast.create(podcast_name=my_data["podcast_name"], serial_mms = my_data["serial_mms"], rss_link = my_data["rss_filename"], serial_pol = my_data["serial_pol"], access_policy = my_data["access_policy"], automated_flag = my_data["automated_flag"], publish_link_ro_record = my_data["publish_link_ro_record"], last_issue = 0, template_name = my_data["template_name"],location = my_data["location"])
        if table == "Episode":
            my_id =Episode.create(podcast=my_data["podcast"], episode_title=my_data["episode_title"], bib_title = my_data["bib_title"], bib_numbering = my_data["bib_numbering"], description=my_data["description"], date_harvested = my_data["date_harvested"],date=my_data["date"], harvest_link = my_data["harvest_link"], episode_link = my_data["episode_link"], epis_numb = my_data["epis_numb"], epis_seas = my_data["epis_seas"], tick = my_data["tick"])            
        if table == "File":
            my_id =File.create(episode = my_data["episode"], filepath = my_data["filepath"], md5sum = my_data["md5sum"], md5sum_from_file = my_data["md5_from_file"],  filesize =my_data["filesize"], size_original = my_data["size_original"], file_type = my_data["file_type"])
        self.my_id = my_id


    def update_from_spreadsheet(self, podcast_name, episode_title, bib_title, bib_numbering, description, f600_first, f600_second, f600_third, f610_first, f610_second, f610_third, f650_first, f650_second, f650_third, f650_forth, f655_first, f700_first, f700_second, f700_third, f710_first, f710_second, f710_third, tick, cataloguer):

        podcast = Podcast.get(Podcast.podcast_name == podcast_name)
        
        # Perform the update
        q = (Episode
             .update(
                 bib_title=bib_title,
                 bib_numbering=bib_numbering,
                 description=description,
                 f600_first=f600_first,
                 f600_second=f600_second,
                 f600_third=f600_third,
                 f610_first=f610_first,
                 f610_second=f610_second,
                 f610_third=f610_third,
                 f650_first=f650_first,
                 f650_second=f650_second,
                 f650_third=f650_third,
                 f650_forth=f650_forth,
                 f655=f655_first,
                 f700_first=f700_first,
                 f700_second=f700_second,
                 f700_third=f700_third,
                 f710_first=f710_first,
                 f710_second=f710_second,
                 f710_third=f710_third,
                 tick=tick,
                 cataloguer=cataloguer
             )
             .where((Episode.episode_title == episode_title) & (Episode.podcast == podcast))
            )
        q.execute()




    def update_the_last_issue(self):

        """Updates db with the maximum date as timestamp of all the episode as the last_issue for each podcast name"""


        logger.info("Updating the last issues....")
        podcasts = Podcast.select()
        for pod in podcasts:
            logger.debug(pod.podcast_name)
            episodes = Episode.select().where(Episode.podcast == pod.id)
            max_date = pod.last_issue
            for epis in episodes:
                logger.debug(epis.episode_title)
                try:
                    if int(epis.date) > max_date:
                        max_date = int(epis.date)
                except ValueError:
                    epis.date = mktime(dateparser.parse(epis.date).timetuple())
                    if int(epis.date) > max_date:
                        max_date = int(epis.date)

            logger.debug(max_date)
            if pod.last_issue != max_date:
                q = Podcast.update(last_issue = max_date).where(Podcast.id == pod.id)
                q.execute()

    def update_the_last_issue_named(self, podcast_name):

        """Updates db with the maximum date as timestamp of all the episode as the last_issue for given podcast name"""


        logger.info("Updating the last issue " + podcast_name)
        podcasts = Podcast.select().where(Podcast.id == podcast_name)
        for pod in podcasts:
            logger.debug(pod.podcast_name)
            episodes = Episode.select().where(Episode.podcast == pod.id)
            max_date = pod.last_issue
            for epis in episodes:
                logger.debug(epis.episode_title)
                try:
                    if int(epis.date) > max_date:
                        max_date = int(epis.date)
                except ValueError:
                    epis.date = mktime(dateparser.parse(epis.date).timetuple())
                    if int(epis.date) > max_date:
                        max_date = int(epis.date)

            logger.debug(max_date)
            if pod.last_issue != max_date:
                q = Podcast.update(last_issue = max_date).where(Podcast.id == pod.id)
                q.execute()

    def insert_the_last_issue(self, podcast_name, last_issue):

        """
        Converts input last issue to time stamp and updates db by podcast name with new last_issue
        Args: 
        my_date (str): date of the last podcast, example format "September 26 2019"
        podcast_name(str): name of the podcast to change the last issue
        last_issue(str): my_date as a timpestamp
        Returns:
        None
        """
        logger.info("Inserting the last issue in db")
        last_issue = mktime(dt.strptime(last_issue, "%B %d %Y").timetuple())
        # logger.debug(last_issue)
        # logger.debug(podcast_name)
        q = Podcast.update(last_issue = last_issue).where(Podcast.podcast_name == podcast_name)
        q.execute()

    def db_get_title_by_mms(self, mms):

        episodes  = Episode.select()
        self.titles = []
        for ep in episodes:
            if ep.mis_mms == mms:
                self.titles.append(ep.episode_title)
        return self.titles

    def db_get_podcast_name_title_by_mms(self, mms):

        self.titles_names = []
        podcasts = Podcast.select()
        for pod in podcasts:
            episodes = Episode.select()
            for ep in episodes:
                if ep.mis_mms == mms:
                    self.titles_names.append((ep.episode_title, pod.podcast_name))
        return(self.titles_names)


    def ticked_titles(self):

        self.titles_done = []
        episodes = Episode.select()
        for ep in episodes:
            if ep.tick == True:
                self.titles_done.append(ep.episode_title)
        return self.titles_done

    def db_update_ie(self, ie_num, episode_id):

        """Updating Alma representation number ie_num in db"""

        q = Episode.update(ie_num= ie_num).where(Episode.id == episode_id)
        q.execute()

    def db_update_holding(self, mms_id, holding_id):

        """Updating Alma holding in db"""
        q = Episode.update(holdings = holding_id ).where(Episode.mis_mms == mms_id)
        q.execute()

    def db_update_updated(self, mms_id):

        """Updating Alma updated statement in db"""
        q = Episode.update(updated = True).where(Episode.mis_mms == mms_id)
        q.execute()

    def db_update_item_id(self, mms_id, item_pid):

        """Updating Alma item id in db"""
        logger.debug("Updating item in db")
        print(mms_id)
        print(item_pid)
        q = Episode.update(item = item_pid ).where(Episode.mis_mms == mms_id)
        q.execute()

    def db_update_item_id_serials(self, episode_title, item_pid):

        """Updating Alma item id in db"""
        logger.debug("Updating item in db")
        q = Episode.update(item = item_pid ).where(Episode.episode_title == episode_title)
        q.execute()

    def db_update_mms(self, mms_id, episode_title, podcast_id):

        """ Updating Alma mms id in db"""
        q = Episode.update(mis_mms = mms_id ).where(Episode.episode_title == episode_title, Episode.podcast == podcast_id)
        q.execute()

    def db_update_sip(self, episode_title, podcast_name):
        podcasts = Podcast.select()
        for pod in podcasts:
            if pod.podcast_name == podcast_name:
                episodes = Episode.select()
                for ep in episodes:
                    if ep.episode_title == episode_title:
                        q = Episode.update(sip = True).where(Episode.id == ep.id)
                        q.execute()

    def db_update_sip_to_false(self, episode_title, podcast_name):

        podcasts = Podcast.select()
        for pod in podcasts:
            if pod.podcast_name == podcast_name:
                episodes = Episode.select()
                for ep in episodes:
                    if ep.episode_title == episode_title:
                        q = Episode.update(sip = False).where(Episode.id == ep.id)
                        q.execute()

    def db_update_template_name(self, podcast_name, template_name):

        q = Podcast.update(template_name= template_name).where(Podcast.podcast_name == podcast_name)
        q.execute()


    def db_delete_episodes_and_files_by_episode_id(self, episode_id):

      
        try:
            podcasts = Podcast.select()#.where(Podcast.last_issue < 1685534400.0)
            for pod in podcasts:
                episodes = Episode.select().where(Episode.podcast==pod.id)
                for ep in episodes:
                   if ep.id == episode_id:
                        print(ep.mis_mms)
                        print(ep.episode_title)
                        files = File.select().where(File.episode == ep.id)
                        for fl in files:
                            q = File.delete().where(File.id==fl.id)
                            q.execute()
                        q = Episode.delete().where(Episode.id==ep.id)
                        q.execute()
            return "Deleted"
        except:
            return "Failed"

    def db_update_templates_from_dictionary(self):

        for podc in podcasts_dict:
            new_template_name = podcasts_dict[podc]["template_name"]  
            podcasts = Podcast.select()
            for pod in podcasts:
                if podc == pod.podcast_name:
                    print("#"*50)
                    print(pod.podcast_name)
                    print(new_template_name)
                    q=Podcast.update(template_name=new_template_name).where(Podcast.id==pod.id)
                    q.execute()
                    print("updated")

    def db_update_automated_flag_from_dictionary(self):

        for podc in podcasts_dict:
            new_flag = podcasts_dict[podc]["automated_flag"]  
            podcasts = Podcast.select()
            for pod in podcasts:
                if podc == pod.podcast_name:
                    print("#"*50)
                    print(pod.podcast_name)
                    print(new_flag)
                    q=Podcast.update(automated_flag=new_flag).where(Podcast.id==pod.id)
                    q.execute()
                    print("updated")

    def db_update_rss_from_dictionary(self):

        for podc in podcasts_dict:
            new_rss = podcasts_dict[podc]["rss_filename"]  
            podcasts = Podcast.select()
            for pod in podcasts:
                if podc == pod.podcast_name:
                    print("#"*50)
                    print(pod.podcast_name)
                    print(new_rss)
                    q=Podcast.update(rss_link=new_rss).where(Podcast.id==pod.id)
                    q.execute()
                    print("updated")

    def export_to_csv(self):

        """This function export content of the database to "database_content.csv" file"""

        # Get the data from the database
        db_data = self.db_reader(["podcast_name","serial_mms", "serial_pol","serial_holding","rss_link","episode_title", "episode_id","location","access_policy","automated_flag","last_issue","template_name","date","episode_link","harvest_link","tags","description","date_harvested", "mis_mms", "holdings", "item", "filepath", "md5sum", "md5from_site", "filesize", "file_type"])

        # Write the data to the CSV file
        with open(database_content_filename, mode='w', newline='', encoding='utf-8') as csv_file:
            fieldnames = ["podcast_name","serial_mms", "serial_pol","serial_holding","rss_link","episode_title", "episode_id","location","access_policy","automated_flag","last_issue","template_name","date","episode_link","harvest_link","tags","description","date_harvested", "mis_mms", "holdings", "item", "filepath", "md5sum", "md5from_site", "filesize", "file_type"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            # Write the header
            writer.writeheader()

            # Write the data
            for row in db_data:
                writer.writerow(row)

        print(f"Database content exported to {database_content_filename}")

    def db_reader(self, req_list, podcast_names=None, returning=True):

        """
        Extracting information from db

        Arguments:
            req_list (list) - required data 
            podcast_names(list) - names of podcasts
            returning (bool) - set True if return or False to print
        """
        logger.debug("Reading DB")
        self.full_dict = {}
        self.returning_dict = {}
        self.returning_list = []
        self.req_list = req_list
        self.returning = returning
        self. podcast_names = podcast_names
        #print(podcast_names)
        if not self.podcast_names:
            self.podcast_names = []
            podcasts = Podcast.select() 
            for pod in podcasts:
                #print(pod.podcast_name)
                self.podcast_names.append(pod.podcast_name)

        for podc_name in self.podcast_names:
            podcasts = Podcast.select()
            for pod in podcasts:
                self.podcast_name = pod.podcast_name
                #print(self.podcast_name)
                if self.podcast_name == podc_name:
                    self.podcast_id = pod.id
                    self.serial_mms = pod.serial_mms
                    self.serial_pol = pod.serial_pol
                    self.rss_link = pod.rss_link
                    self.serial_holding= pod.serial_holding
                    self.location = pod.location
                    self.access_policy = pod.access_policy
                    self.publish_link_to_record = pod.publish_link_to_record
                    self.automated_flag = pod.automated_flag
                    self.last_issue = pod.last_issue
                    self.template_name = pod.template_name
                    self.full_dict["podcast_id"] = self.podcast_id
                    self.full_dict["podcast_name"]= self.podcast_name
                    self.full_dict["serial_mms"]= self.serial_mms
                    self.full_dict["serial_pol"]= self.serial_pol
                    self.full_dict["serial_holding"] = self.serial_holding
                    self.full_dict["rss_link"] = self.rss_link
                    self.full_dict["location"] = self.location
                    self.full_dict["access_policy"]= self.access_policy
                    self.full_dict["publish_link_to_record"] = self.publish_link_to_record
                    self.full_dict["automated_flag"] =  self.automated_flag
                    self.full_dict["last_issue"] = self.last_issue
                    self.full_dict["template_name"] = self.template_name
                    episodes = Episode.select().where(Episode.podcast==pod.id)
                    self.returning_dict = {}
                    for ep in episodes:
                        self.episode_id = ep.id
                        self.returning_dict = {}
                        self.episode_title = ep.episode_title
                        self.bib_title = ep.bib_title
                        self.bib_numbering = ep.bib_numbering
                        self.subtitle = ep.subtitle
                        self.description = ep.description
                        self.date = ep.date
                        self.episode_link = ep.episode_link  
                        self.tags = ep.tags
                        self.date_harvested = ep.date_harvested
                        self.harvest_link = ep.harvest_link

                        self.full_dict["episode_id"] = self.episode_id
                        self.full_dict["episode_title"]= self.episode_title
                        self.full_dict["bib_title"] = self.bib_title
                        self.full_dict["bib_numbering"] = self.bib_numbering
                        self.full_dict["subtitle"]= self.subtitle
                        self.full_dict["description"] = self.description
                        self.full_dict["date"]= self.date
                        self.full_dict["episode_link"] = self.episode_link
                        self.full_dict["tags"]= self.tags
                        self.full_dict["date_harvested"]  =self.date_harvested
                        self.full_dict["harvest_link"] = self.harvest_link

                        self.f600_first = ep.f600_first
                        self.f600_second = ep.f600_second
                        self.f600_third = ep.f600_third
                        self.f610_first = ep.f610_first
                        self.f610_second = ep.f610_second
                        self.f610_third = ep.f610_third
                        self.f650_first = ep.f650_first
                        self.f650_second = ep.f650_second
                        self.f650_third = ep.f650_third
                        self.f650_forth = ep.f650_forth
                        self.f655 = ep.f655
                        self.f700_first = ep.f700_first
                        self.f700_second = ep.f700_second
                        self.f700_third = ep.f700_third
                        self.f710_first  = ep.f710_first
                        self.f710_second = ep.f710_second
                        self.f710_third = ep.f710_third
                        self.full_dict["f600_first"] = self.f600_first
                        self.full_dict["f600_second"] = self.f600_second
                        self.full_dict["f600_third"] = self.f600_third
                        self.full_dict["f610_first"] = self.f610_first
                        self.full_dict["f610_second"] = self.f610_second
                        self.full_dict["f610_third"] = self.f610_third
                        self.full_dict["f650_first"] = self.f650_first
                        self.full_dict["f650_second"] = self.f650_second
                        self.full_dict["f650_third"] = self.f650_third
                        self.full_dict["f650_forth"] = self.f650_forth
                        self.full_dict["f655"] = self.f655
                        self.full_dict["f700_first"] = self.f700_first
                        self.full_dict["f700_second"] = self.f700_second
                        self.full_dict["f700_third"] = self.f700_third
                        self.full_dict["f710_first"] = self.f710_first
                        self.full_dict["f710_second"] = self.f710_second
                        self.full_dict["f710_third"] = self.f710_third
                        self.tick = ep.tick
                        self.cataloguer = ep.cataloguer
                        self.mis_mms = ep.mis_mms
                        self.mis_pol = ep.mis_pol
                        self.holdings = ep.holdings
                        self.item = ep.item
                        self.receive = ep.receive
                        self.ie_num = ep.ie_num
                        self.epis_numb = ep.epis_numb
                        self.epis_seas = ep.epis_seas
                        self.updated = ep.updated
                        self.sip = ep.sip
                        self.full_dict["tick"] = self.tick
                        self.full_dict["cataloguer"] = self.cataloguer
                        self.full_dict["mis_mms"] = self.mis_mms
                        self.full_dict['mis_pol'] = self.mis_pol
                        self.full_dict["holdings"] = self.holdings
                        self.full_dict["item"] = self.item
                        self.full_dict["receive"] = self.receive
                        self.full_dict["ie_num"] = self.ie_num
                        self.full_dict["epis_numb"] = self.epis_numb
                        self.full_dict["epis_seas"] = self.epis_seas
                        self.full_dict["updated"] = self.updated
                        self.full_dict["sip"] = self.sip
                        files = File.select().where(File.episode == ep.id)
                        self.returning_dict = {}
                        for fl in files:
                            self.file_id = fl.id
                            self.filepath = fl.filepath
                            self.md5sum = fl.md5sum
                            self.md5from_site = fl.md5from_site
                            self.filesize = fl.filesize
                            self.file_type = fl.file_type
                            self.full_dict["file_id"] = self.file_id
                            self.full_dict["filepath"] = self.filepath
                            self.full_dict["md5sum"] = self.md5sum
                            self.full_dict["md5from_site"] = self.md5from_site
                            self.full_dict["file_type"] = self.file_type
                            self.full_dict["filesize"] = self.filesize
                            self.returning_dict = {}
                            for el in self.req_list:
                                self.returning_dict[el] = self.full_dict[el] 
                            if not self.returning_dict in self.returning_list:
                                self.returning_list += [self.returning_dict]
                        if self.returning_dict == {}:
                            for el in self.req_list:
                                self.returning_dict[el] = self.full_dict[el]  
                            if not self.returning_dict in self.returning_list:
                                self.returning_list += [self.returning_dict]
                    if self.returning_dict== {}:
                        for el in self.req_list:
                            try:
                                self.returning_dict[el] = self.full_dict[el]  
                            except:
                                pass
                        if not self.returning_dict in self.returning_list:
                            self.returning_list += [self.returning_dict]
                    self.full_dict = {}
        
        if not self.returning:

            for el in self.returning_list:
                try:
                  print(["{}: {}".format(key, el[key])  for key in el.keys()])

                except:
                  print(["{}: {}".format(key, str(el[key]).encode('utf-8'))  for key in el.keys()])

            #[print(el) for el in self.returning_list]
            #print(["{}: {}".format(key, self.returning_dict[key])  for key in self.returning_dict.keys()])  
        else:
            #print(self.returning_list)
            return self.returning_list
    def delete_podcast_by_name(self, podcast_name):
        """
        Deletes all information related to a specific podcast by its name from the
        Podcasts, Episodes, and Files tables.

        Parameters:
        podcast_name (str): The name of the podcast to be deleted.
        """
        try:
            # Find the podcast by name
            podcast = Podcast.get(Podcast.podcast_name == podcast_name)
            
            # Find all episodes associated with this podcast
            episodes = Episode.select().where(Episode.podcast == podcast.id)
            
            # For each episode, find and delete all associated files
            for episode in episodes:
                files = File.select().where(File.episode == episode.id)
                for file in files:
                    file.delete_instance()
                
                # Delete the episode
                episode.delete_instance()
            
            # Finally, delete the podcast
            podcast.delete_instance()
            logger.info(f"Successfully deleted all information for podcast '{podcast_name}'.")
        except peewee.DoesNotExist:
            logger.error(f"Podcast named '{podcast_name}' does not exist.")
        except Exception as e:
            logger.error(f"Error deleting podcast '{podcast_name}': {e}")




def main():

    my_db = DbHandler()
    # my_db.table_creator( "File", {'episode': 18602, 'filepath': r"Y:\ndha\pre-deposit_prod\LD_working\podcasts\files\76 small rooms\20230901_Ep046_Award_Reward_FINAL.mp3", 'md5sum': 'fbaa50cd870f8b77dcf30c1d91b0a0ff', 'md5_from_file': None, 'filesize': 110395245, 'size_original': 110395245, 'file_type': "mp3"})
    #my_db.db_delete_episodes_and_files_by_episode_id(14382)


    # mms_list = ["9919401435402836","9919235187602836","9919401435202836","9919401435102836","9919154286602836","9919235278402836","9919398834002836","9919401434802836","9919398832902836"]

    # for el in mms_list:
    #     title_name = my_db.db_get_podcast_name_title_by_mms(mms_list[0])[0]
    #     my_db.db_update_sip_to_false(title_name[0], title_name[1])

    ######UPDATING TEMPATE NAMES FROM DICTIONARY##################################


    #my_db.db_update_templates_from_dictionary()

    ###############UPDATE  automated_flag FROM DICTIONARY #########################

    my_db.db_update_automated_flag_from_dictionary()

    ###############UPDATE  rss_feed FROM DICTIONARY #########################

    #my_db.db_update_rss_from_dictionary()

    ################################SET LAST ISUE IN PODCASTS TABLE########################################
    
    #my_db.insert_the_last_issue("Access granted","January 01 2020")


if __name__ == '__main__':
    main()

 

