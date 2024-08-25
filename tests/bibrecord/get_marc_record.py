from pymarc import parse_xml_to_array

def get_marc_record(template_path):
    """
    This function reads an XML file, parses it, and returns the first MARC record.
    """
    record = parse_xml_to_array(template_path)[0]
    return record
