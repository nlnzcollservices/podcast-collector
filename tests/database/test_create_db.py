import pytest
import os
import peewee
import sys

test_folder = os.path.abspath(__file__)
project_folder = os.path.abspath(os.path.join(__file__ ,"..\..\.."))
script_folder = os.path.join(project_folder,"scripts")

sys.path.insert(0,script_folder)

from podcast_models import Podcast, Episode, File



@pytest.fixture(scope="module")
def db():
    # Set up db and create table
    test_db = peewee.SqliteDatabase(":memory:")
    test_db.bind([Podcast])
    test_db.create_tables([Podcast])
    yield test_db
    test_db.drop_tables([Podcast])

def test_create_table(db):

    Podcast.bind(db)
    Podcast.create_table()
    assert Podcast.table_exists()

 	#checking columns
    expected_columns = ["id", "podcast_name", "serial_mms", "serial_pol",
                        "serial_holding", "rss_link", "location",
                        "access_policy", "publish_link_to_record",
                        "automated_flag", "last_issue", "template_name"]
    actual_columns = [field.name for field in Podcast._meta.sorted_fields]
    assert expected_columns == actual_columns


