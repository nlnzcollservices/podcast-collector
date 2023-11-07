import pytest
import os
import sys

test_folder = os.path.abspath(__file__)
project_folder = os.path.abspath(os.path.join(__file__ ,r"..\..\.."))
script_folder = os.path.join(project_folder,"scripts")
sys.path.insert(0,script_folder)
from podcasts0_harvester import Harvester



# Define test fixtures (e.g., instances of Harvester class) as needed for your tests
@pytest.fixture
def harvester_instance():
    podcast_id = 1  
    podcast_name = "Your Podcast Name" 
    podcast_data = {} 
    last_issue = "Last Issue"  
    podcast_url = "Podcast URL"  
    serial_mms = "Serial MMS" 
    my_harv = Harvester(podcast_id, podcast_name, podcast_data, last_issue, podcast_url, serial_mms)
    return my_harv

# Test for checking if the function can handle a feed with no entries
def test_parsing_with_feedparser_no_entries(harvester_instance):
    harvester_instance.podcast_data = {"rss_filename": "https://example.com/rss"}
    harvester_instance.parsing_with_feedparser()
    # Assert that the function handles an empty feed gracefully (no exceptions, etc.)
    assert True  # Modify this assertion as needed

# Test for checking if the function filters episodes based on date
def test_parsing_with_feedparser_date_filtering(harvester_instance):
    harvester_instance.podcast_data = {"rss_filename": "https://example.com/rss"}
    # Set the last_issue to a timestamp to filter episodes
    harvester_instance.last_issue = 1609459200  # E.g., January 1, 2021
    harvester_instance.parsing_with_feedparser()
    # Assert that only new episodes are processed
    assert True  # Modify this assertion as needed

# Test for checking if the function correctly downloads an episode
def test_parsing_with_feedparser_download_episode(harvester_instance):
    harvester_instance.podcast_data = {"rss_filename": "https://example.com/rss"}
    # Ensure that an episode with a download link is included in the feed
    harvester_instance.parsing_with_feedparser()
    # Assert that the episode is downloaded successfully
    assert True  # Modify this assertion as needed



# ---TO DO-------------------------------------

# def test_parsing_with_feedparser_error_handling(harvester_instance):
#     harvester_instance.podcast_data = {"rss_filename": "https://invalid-feed.com/rss"}
#     # Set an invalid RSS feed URL to trigger an error
#     with pytest.raises(Exception):
#         harvester_instance.parsing_with_feedparser()

# class Harvester:
#     # ... other class methods ...

#     def parsing_with_feedparser(self):
#         try:
#             # Attempt to parse the RSS feed
#             # If parsing fails, raise an exception
#             # Example:
#             if not is_valid_rss(self.podcast_data["rss_filename"]):
#                 raise Exception("Invalid RSS feed URL")
#             # Rest of the parsing logic
#         except Exception as e:
#             # Handle the exception or log an error message
#             print(f"Error: {e}")
#             raise 