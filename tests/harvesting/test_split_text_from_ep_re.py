import re
import pytest
import os
import sys

test_folder = os.path.abspath(__file__)
project_folder = os.path.abspath(os.path.join(__file__, "..", "..", ".."))
script_folder = os.path.join(project_folder, "scripts")
sys.path.insert(0, script_folder)

from podcasts0_harvester import Harvester

# Sample data for initializing Harvester instance
podcast_id = 1
podcast_name = "NZ everyday investor"
podcast_data = {}
last_issue = "2023-01-01"
podcast_url = "http://example.com"
serial_mms = "12345"

def test_extract_episode_info():
    # Create an instance of Harvester
    harvester = Harvester(podcast_id, podcast_name, podcast_data, last_issue, podcast_url, serial_mms)
    
    # Define test cases as tuples (text, pattern, expected_remaining_text, expected_ep_info)
    test_cases = [
        ("Ep 123: Episode title", re.compile(r"(Ep\s*\d+)"), ": Episode title", "Ep 123"),
        ("No episode info", re.compile(r"(Ep\s*\d+)"), "No episode info", None),
        ("Episode 45: Another title", re.compile(r"(Episode\s*\d+)"), ": Another title", "Episode 45"),
    ]
    
    for text, pattern, expected_remaining_text, expected_ep_info in test_cases:
        remaining_text, ep_info = harvester.extract_episode_info(text, pattern)
        assert remaining_text == expected_remaining_text, f"Failed for text: {text}"
        assert ep_info == expected_ep_info, f"Failed for text: {text}"

def test_apply_rules():
    # Create an instance of Harvester

    podcast_names = {"Stag roar":[
                                    ('Ep318: Ben; The Roe Deer Guy', 'Ben; The Roe Deer Guy.','Ep318'),
                                    ('Ep37-Dave Keto Feldman','Dave Keto Feldman.','Ep37'),
                                    ('The Otago Herd/ Allan Wells; Waipapa Junction Flats, Arawhata Valley: 1960','The Otago Herd/ Allan Wells; Waipapa Junction Flats, Arawhata Valley: 1960.', None),
                                    ("Episode 45 - Another Title", "Another Title.", "Episode 45")
                                ],
                    "All Blacks":[
                                    ('Episode 1 S3 HSBC 7s in focus with Brady Rush, Leroy Carter, and Moses Leo', 'HSBC 7s in focus with Brady Rush, Leroy Carter, and Moses Leo.','Episode 1 S3'),
                                    ("Episode 12 S2 Reviewing 2023 with Jeff Wilson ahead of the ASB Rugby Awards",'Reviewing 2023 with Jeff Wilson ahead of the ASB Rugby Awards.','Episode 12 S2'),
                                    ('Episode 11: Other title','Episode 11: Other title.', None),
                                    ("Ep 15: Other title2","Ep 15: Other title2.",None)
                                ],


                    "Dancing in your head":[

                                        ("Dancing In Your Head - Ep01 - Chris Palmer", "Chris Palmer.","Ep01"),
                                        ("CUD - Frances Libeau","CUD - Frances Libeau.",None),
                                        ("PūoroTū - A Celebration of the Oro - Ep2","PūoroTū - A Celebration of the Oro - Ep2.",None)
                    ],
                    "Taringa":[
                                ("Taringa - Ep 236 - Kupu, Kupu, Kupu with MC Grammar - Postposed Particles - pt 3","Kupu, Kupu, Kupu with MC Grammar - Postposed Particles - pt 3.","Ep 236"),

                    ]
                    }


    for podcast in podcast_names.keys():
        harvester = Harvester(podcast_id, podcast, podcast_data, last_issue, podcast_url, serial_mms) 
        for episode_title, expected_bib_title, expected_bib_numbering in podcast_names[podcast]:

            harvester.episode_title = episode_title  # Set the episode title
            print(harvester.episode_title)
            print(harvester.podcast_name)

            harvester.split_rss_title()  # Call the method without 
            print(harvester.bib_title)
            print(harvester.bib_numbering)

            assert harvester.bib_title == expected_bib_title, f"Failed for episode_title: {episode_title}"
            assert harvester.bib_numbering == expected_bib_numbering, f"Failed for episode_title: {episode_title}"




if __name__ == "__main__":
    pytest.main()



