import os
from pymarc import Record
from get_marc_record  import get_marc_record

def test_get_marc_record():
    # Provide a path to a sample XML file for testing purposes
    template_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'templates', 'mis_Podcast_SR_AgriHQandA.xml')
    
    # Call the function and get the record
    record = get_marc_record(template_path)
    
    # Check if the record is an instance of the MARC Record
    assert isinstance(record, Record), "Record should be a MARC Record instance"
    
    # Check if the record is not None (i.e., it parsed correctly)
    assert record is not None, "Parsed record should not be None"
    
    # Optionally, check specific fields in the record
    assert '245' in record, "Record should contain a title field (tag 245)"
