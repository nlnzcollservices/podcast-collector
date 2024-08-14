import peewee
import os
try:
    from settings import script_folder, working_folder, database_fullname

except:
        script_folder = os.getcwd()
        working_folder = "\\".join(script_folder.split("\\")[:-1])
        database_folder = os.path.join(working_folder, "database")
        database_fullname = os.path.join(database_folder, "podcasts.db")

database = peewee.SqliteDatabase(database_fullname)

#'title' VARCHAR(30) PRIMARY KEY, 'paged_feed_next' VARCHAR(30)  , 'link' VARCHAR(30) , 'description' VARCHAR(30) , 'cover_url' INTEGER(14));")  
#q = "CREATE TABLE IF NOT EXISTS [{}] ('podcast_title' VARCHAR(30), 'title' VARCHAR(30) PRIMARY KEY, 'subtitle'  VARCHAR(30)  ,  'description'  VARCHAR(500), 'published'  VARCHAR(30),  'link'  VARCHAR(30), 'total_time'  VARCHAR(30), 'payment_url'  VARCHAR(30), 'enclosures'  VARCHAR(30) , 'guid'  VARCHAR(30)); ".format(title) 


class Podcast(peewee.Model):

    podcast_name = peewee.CharField(max_length=255)
    serial_mms = peewee.CharField(max_length=20)
    serial_pol = peewee.CharField(max_length = 15, null= True, default = None )
    serial_holding = peewee.CharField(default=None, max_length = 30, null = True)
    rss_link = peewee.CharField(max_length = 125)
    location = peewee.CharField(max_length = 125, null= True, default = None )
    access_policy = peewee.CharField(max_length = 3)
    publish_link_to_record = peewee.BooleanField(default = True)
    automated_flag = peewee.BooleanField(default=False)
    last_issue = peewee.DateTimeField(null= True, default = None)
    template_name = peewee.CharField(default=None, max_length = 100, null = True)

    class Meta:
        database = database

class Episode(peewee.Model):

    podcast = peewee.ForeignKeyField(Podcast) 
    episode_title = peewee.CharField(max_length = 255)
    subtitle = peewee.CharField(max_length=255,null= True, default = None )
    bib_title = peewee.CharField(max_length=255)
    bib_numbering= peewee.CharField(max_length=255)
    description = peewee.CharField(max_length=4000)
    date = peewee.DateTimeField()
    episode_link = peewee.CharField(125)
    tags = peewee.CharField(max_length=700, null= True, default = None )
    date_harvested = peewee.DateTimeField()
    harvest_link = peewee.CharField(max_length=125, null= True, default =None)
    f600_first = peewee.CharField(max_length=700, null= True, default = None )
    f600_second = peewee.CharField(max_length=700 , null= True, default = None)
    f600_third = peewee.CharField(max_length=700, null= True, default = None)
    f610_first = peewee.CharField(max_length=700, null= True, default = None) 
    f610_second = peewee.CharField(max_length=700, null= True, default = None)
    f610_third=peewee.CharField(max_length=700, null= True, default = None)  
    f650_first =peewee.CharField(max_length=700, null= True, default = None) 
    f650_second = peewee.CharField(max_length=700, null= True, default = None)  
    f650_third = peewee.CharField(max_length=700, null= True, default = None) 
    f650_forth = peewee.CharField(max_length=700, null= True, default = None)
    f655 = peewee.CharField(max_length=700, null= True, default = None)
    f700_first = peewee.CharField(max_length=700, null= True, default = None) 
    f700_second = peewee.CharField(max_length=700, null= True, default = None) 
    f700_third = peewee.CharField(max_length=700, null= True, default = None) 
    f710_first  = peewee.CharField(max_length=700, null= True, default = None)  
    f710_second = peewee.CharField(max_length=700, null= True, default = None) 
    f710_third = peewee.CharField(max_length=700, null= True, default = None)
    tick = peewee.BooleanField(default=False)
    cataloguer= peewee.CharField(max_length=125, null= True, default =None)
    mis_mms = peewee.CharField(max_length=125, null= True, default = None )
    sip = peewee.BooleanField(default=False)
    mis_pol = peewee.CharField(max_length=125, null= True, default = None )
    holdings = peewee.CharField(max_length=125, null= True, default = None )
    item = peewee.CharField(max_length=125, null= True, default = None )
    receive = peewee.BooleanField(default=False)
    ie_num = peewee.CharField(max_length=125, null= True, default = None )
    epis_numb = peewee.CharField(default=None, max_length = 10, null = True)
    epis_seas = peewee.CharField(default=None, max_length = 10, null = True)
    updated = peewee.CharField(default=False, max_length = 20, null = True)
   
    class Meta:
        database = database


class File(peewee.Model):

    episode = peewee.ForeignKeyField(Episode) 
    filepath = peewee.CharField(max_length=1024)
    md5sum = peewee.CharField(max_length=32)
    md5from_site = peewee.CharField(max_length = 32, null= True, default = None )
    file_type = peewee.CharField(max_length = 4)
    filesize = peewee.CharField(default=None, max_length = 20, null = True)
    size_original = peewee.CharField(default=None, max_length = 20, null = True)

    class Meta:
        database = database



if __name__ == '__main__':
    try:
        Podcast.create_table()
    except peewee.OperationalError:
        print("Podcast table already exists!")

    try:
        Episode.create_table()
    except peewee.OperationalError:
        print("Podcast table already exists!")

    try:
        File.create_table()
    except peewee.OperationalError:
        print("Podcast table already exists!")
