import os
import hashlib
from datetime import datetime as dt
from database_handler import DbHandler
from time import mktime
import peewee
from podcast_models import Podcast, Episode, File

path = r""

def add_file(filepath, episode_id):
	hash_md5 = hashlib.md5()
	print(filepath)
	with open(filepath, "rb") as f:
		for chunk in iter(lambda: f.read(4096), b""):
			hash_md5.update(chunk)
			md5 = hash_md5.hexdigest()
	filesize = os.path.getsize(filepath)
	file_type = filepath.split(".")[-1]
	my_db = DbHandler()
	file_data = {"episode" : episode_id, "filepath" : filepath, "md5sum" : md5, "md5_from_file" : md5, "filesize" : filesize, "size_original" : filesize, "file_type" : file_type}
	my_db.table_creator("File", file_data)
			

		 		


if __name__ == "__main__":
	add_file(path, 5985)
