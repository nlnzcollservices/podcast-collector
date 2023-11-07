import pytest
import os
import sys

test_folder = os.path.abspath(__file__)
project_folder = os.path.abspath(os.path.join(__file__ ,"..\..\.."))
script_folder = os.path.join(project_folder,"scripts")
sys.path.insert(0,script_folder)
from podcasts0_harvester import Harvester



@pytest.fixture
def episodes():
    # Define sample episodes in ascending order of publication date
    episode1 = {"published": "2023-01-01T00:00:00+00:00"}
    episode2 = {"published": "2023-01-02T00:00:00+00:00"}
    return [episode1, episode2]

def test_reverse_episodes_ascending(episodes):
   
    podcast_id = 1  
    podcast_name = "Your Podcast Name" 
    podcast_data = {} 
    last_issue = "Last Issue"  
    podcast_url = "Podcast URL"  
    serial_mms = "Serial MMS" 
    my_harv = Harvester(podcast_id, podcast_name, podcast_data, last_issue, podcast_url, serial_mms)
    reversed_episodes =my_harv.reverse_episodes(episodes)
    assert reversed_episodes[0]["published"] > reversed_episodes[1]["published"]

def test_reverse_episodes_descending(episodes):
    # Change the order of episodes to descending
    podcast_id = 1  
    podcast_name = "Podcast Name"  
    podcast_data = {} 
    last_issue = "Last Issue"  
    podcast_url = "Podcast URL" 
    serial_mms = "Serial MMS"
    my_harv = Harvester(podcast_id, podcast_name, podcast_data, last_issue, podcast_url, serial_mms)
    reversed_episodes = my_harv.reverse_episodes(episodes)

    assert reversed_episodes[1]["published"] < reversed_episodes[0]["published"]

if __name__ == "__main":
    pytest.main()
