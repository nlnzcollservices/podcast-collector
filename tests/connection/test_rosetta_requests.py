import os
import re
import requests
from zeep import Client
import sys
import pytest
import responses

test_folder = os.path.abspath(__file__)
project_folder = os.path.abspath(os.path.join(__file__, "..\..\.."))
script_folder = os.path.join(project_folder, "scripts")
sys.path.insert(0, script_folder)
from podcasts import Podcast_pipeline

pp = Podcast_pipeline("sb")

@pytest.fixture
def responses_fixture():
    with responses.RequestsMock() as mock:
        yield mock

def test_check_sip_status(responses_fixture):
    # Mock the HTTP request
    responses_fixture.add(responses.GET, 'https://ndhadeliver.natlib.govt.nz/delivery/sru',
                          body='<response>mocked_response</response>', status=200)

    # Mock the Zeep client and its methods
    with responses_fixture:
        responses_fixture.add(responses.POST, 'http://mocked_service_url', body='<response>mocked_response</response>', status=200)

        # Replace any necessary environment variables
        os.environ["USERNAME"] = "your_username"

        # Call the function
        result = pp.check_sip_status("199777")

        # Perform assertions
        assert result is True
        assert len(responses_fixture.calls) == 2
        assert responses_fixture.calls[0].request.url == 'https://ndhadeliver.natlib.govt.nz/delivery/sru'
        assert responses_fixture.calls[1].request.url == 'http://mocked_service_url'
