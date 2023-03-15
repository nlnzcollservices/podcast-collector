import pytest
import os
import sys
test_folder = os.path.abspath(__file__)
project_folder = os.path.abspath(os.path.join(__file__ ,"..\..\.."))
script_folder = os.path.join(project_folder,"scripts")
sys.path.insert(0,script_folder)
from podcasts1_create_record import RecordCreator

rc = RecordCreator("prod")



def test_parsing_added_fields_one_s():
    # one subfield
    value = "__$a First subfield"
    expected_output = ("", "", ["a First subfield"])
    output = rc.parsing_added_fields(value)
    assert output == expected_output

def test_parsing_added_fields_two_s():
    # two subfields and indicators
    value = "12$a First subfield$b Second subfield"
    expected_output = ("1", "2", ["a First subfield", "b Second subfield"])
    output = rc.parsing_added_fields(value)
    assert output == expected_output

