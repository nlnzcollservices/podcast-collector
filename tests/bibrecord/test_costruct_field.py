import pytest
import os
import sys
test_folder = os.path.abspath(__file__)
project_folder = os.path.abspath(os.path.join(__file__ ,"..\..\.."))
script_folder = os.path.join(project_folder,"scripts")
sys.path.insert(0,script_folder)
from podcasts1_create_record import RecordCreator
from pymarc import Record, Subfield

rc = RecordCreator("prod")
rc.record = Record()


def test_construct_field():
    my_field = ["700", "1_ $a Duffy, Laura,"]
    rc.construct_field(my_field)
    field = rc.record.fields[0]
    assert field.tag == "700"
    assert field.indicators == ["1", ""]
    assert field.subfields == [Subfield(code = "a", value = "Duffy, Laura,")]

