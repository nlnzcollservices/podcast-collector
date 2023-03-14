import pytest
import os
import peewee
import sys

test_folder = os.path.abspath(__file__)
project_folder = os.path.abspath(os.path.join(__file__ ,"..\..\.."))
script_folder = os.path.join(project_folder,"scripts")

sys.path.insert(0,script_folder)

from podcast_models import File



@pytest.fixture(scope="module")
def db():
    # Set up db and create table
    test_db = peewee.SqliteDatabase(":memory:")
    test_db.bind([File])
    test_db.create_tables([File])
    yield test_db
    test_db.drop_tables([File])

def test_create_file_table(db):

    File.bind(db)
    File.create_table()
    assert File.table_exists()

 	#checking columns
    expected_columns = ['id','episode', 'filepath', 'md5sum', 'md5from_site', 'file_type', 'filesize', 'size_original']

    actual_columns = [field.name for field in File._meta.sorted_fields]
    assert expected_columns == actual_columns


