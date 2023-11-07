import pytest
import gspread
import sys
import os 


test_folder = os.path.abspath(__file__)
project_folder = os.path.abspath(os.path.join(__file__ ,"..\..\.."))
script_folder = os.path.join(project_folder,"scripts")
sys.path.insert(0,script_folder)
from podcasts0_harvester import reload_spreadsheet 

class MockGspread:
    def open_by_key(self, key):
        return MockWorksheet()

class MockWorksheet:
    def get_worksheet(self, index):
        return self

    def range(self, cell_range):
        return ["Item 1", "Item 2", "Item 3"]

    @property
    def row_count(self):
        return 3  # Set the row_count attribute to an appropriate value

# Patch the 'gspread.authorize' function to return our MockGspread object
@pytest.fixture
def mock_gspread(monkeypatch):
    monkeypatch.setattr(gspread, "authorize", lambda creds: MockGspread())

def test_reload_spreadsheet(mock_gspread):
    # Call the function and get the cell range
    cell_range = reload_spreadsheet()

    # Perform assertions based on the expected result from the MockWorksheet
    expected_range = ["Item 1", "Item 2", "Item 3"]
    assert cell_range == expected_range

if __name__ == "__main__":
    pytest.main()
