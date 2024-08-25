import pytest
import os
import sys

test_folder = os.path.abspath(__file__)
project_folder = os.path.abspath(os.path.join(__file__ ,"..\..\.."))
script_folder = os.path.join(project_folder,"scripts")
sys.path.insert(0,script_folder)

from podcasts3_holdings_items import ItemMaker, Holdings_items

@pytest.fixture
def item_maker():
    return ItemMaker()

@pytest.fixture
def holdings_items():
    return Holdings_items("prod")

def test_check_item_in_the_system(item_maker):
    pub_name = "example_pub"
    description = "example_description"
    assert item_maker.check_item_in_the_system(pub_name, description) == False


