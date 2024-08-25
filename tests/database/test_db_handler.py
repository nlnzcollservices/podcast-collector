import pytest
import os
import peewee
import sys

test_folder = os.path.abspath(__file__)
project_folder = os.path.abspath(os.path.join(__file__ ,"..\..\.."))
script_folder = os.path.join(project_folder,"scripts")

sys.path.insert(0,script_folder)
from podcast_models import Episode
from unittest.mock import patch
from peewee import SqliteDatabase
from database_handler import DbHandler
dbh = DbHandler()


test_db = SqliteDatabase(':memory:')
test_db.bind([Episode], bind_refs=False, bind_backrefs=False)
test_db.connect()
test_db.create_tables([Episode])

def test_db_update_mms():

    episode = Episode.create(
        episode_title="Test Episode",
        podcast=1,
        mis_mms=None,
    )

    with patch('database_handle.Episode.update') as mock_update:
        mock_update.return_value.execute.return_value = 1
        db_update_mms(mms_id='99999999999999992836', episode_title='Test Episode', podcast_id=1)

    updated_episode = Episode.get_by_id(episode.id)
    assert updated_episode.mis_mms == '99999999999999992836'











