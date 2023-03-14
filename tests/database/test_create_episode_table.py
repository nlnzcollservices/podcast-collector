import pytest
import os
import peewee
import sys

test_folder = os.path.abspath(__file__)
project_folder = os.path.abspath(os.path.join(__file__ ,"..\..\.."))
script_folder = os.path.join(project_folder,"scripts")

sys.path.insert(0,script_folder)

from podcast_models import Episode



@pytest.fixture(scope="module")
def db():
    # Set up db and create table
    test_db = peewee.SqliteDatabase(":memory:")
    test_db.bind([Episode])
    test_db.create_tables([Episode])
    yield test_db
    test_db.drop_tables([Episode])

def test_create_table(db):

    Episode.bind(db)
    Episode.create_table()
    assert Episode.table_exists()

 	#checking columns
    expected_columns = ['id','podcast', 'episode_title', 'subtitle', 'description', 'date', 'episode_link', 'tags', 'date_harvested', 'harvest_link', 'f100', 'f600_first', 'f600_second', 'f600_third', 'f610_first', 'f610_second', 'f610_third', 'f650_first', 'f650_second', 'f650_third', 'f650_forth', 'f655', 'f700_first', 'f700_second', 'f700_third', 'f710_first', 'f710_second', 'f710_third', 'tick', 'mis_mms', 'sip', 'mis_pol', 'holdings', 'item', 'receive', 'ie_num', 'epis_numb', 'epis_seas', 'updated']



    actual_columns = [field.name for field in Episode._meta.sorted_fields]
    assert expected_columns == actual_columns


