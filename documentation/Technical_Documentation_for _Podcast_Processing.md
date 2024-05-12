# Technical Documentation for Podcast Processing

## System Architecture Overview

### High-Level Diagram
![Podcasts](/documentation/podcasts_high_level_chart.png)

### Data Flow
![Podcasts](/documentation/Podcasts.png)

## Technology Stack

### Languages and Frameworks
Specify the programming languages, frameworks, and major libraries used:
- Python
- Peewee ORM
- pymarc
- gspread
- BeautifulSoup

### External Services
Detail any external services the system interacts with, such as:
- Google Sheets API
- Alma API

## Current State Functionality

### Main Script
- **Purpose:** Manages the overall workflow of the podcast processing system.
- **Functions:** Run podcast pipeline, which includes harvesting, making bib records, making SIPs, updating records, and  also it handles file clean-ups.
- **Key Features:**
  - Integration with Google Sheets for data management.
  - Use of external libraries for data parsing.
  - Extensive logging for debugging and tracking the process flow.

### Record Creation Script
- **Purpose:** Handles the creation and updating of bibliographic records in Alma.
- **Functions:** Parses spreadsheet data to create MARC records.
- **Key Features:**
  - Uses `pymarc` to handle MARC records.
  - Dynamically adds fields based on spreadsheet inputs.
  - Can handle various podcast titles by adjusting MARC fields with individual rules.
  - Uses ['alma_tools'](https://github.com/nlnzcollservices/alma-tools)
 
 
###  SIP Making Script
- **Purpose:** Makes Submission Inormation Packages to submit to Rosetta folder.
- **Functions:** Run SIPs making script and supply it with episode information.
- **Key Features:**
  - Usees ['rosetta_sip_factory'](https://github.com/NLNZDigitalPreservation/rosetta_sip_factory)
  - Produces SIPs for Rosetta

 ### Records Updating Script
- **Purpose:** Updates bibliographic record with new field in the Alma system.
- **Functions:** Identifies and removes duplicate fields, adds specific fields, and updates records.
- **Key Features:**
  - Focus on  removing duplicates.
  - Capability to update records with 942 field.
    
### Harvesting Script
- **Purpose:** Harvest new episodes  according to podcasts dictionary and based on last episode date.
- **Functions:** Checking for, downloading, checking files, cleaning metadata, adding to Google sheet, poplulates database.
- **Key Features:**
  - Use of [downloader script](https://github.com/nlnzcollservices/file-downloader/).
  - Capability to indetify required episode

### Database Models Script
- **Purpose:** Defines the structure of the database using `peewee` ORM.
- **Functions:** Establishes tables for podcasts, episodes, and associated files.
- **Key Features:**
  - Models for managing relational data.
  - Use of foreign keys to link episodes to podcasts and files to episodes.
  - Fields include episode details, metadata for MARC fields, and file handling specifics.

### Database Handler Script
- **Purpose:** Manages all database interactions.
- **Functions:** Reads from, writes to, and updates the database based on various triggers and inputs.
- **Key Features:**
  - Comprehensive methods for database CRUD operations.
  - Functionality to handle complex queries and updates, such as batch updates and deletions.


 ## Setup and Configuration

### Installation Requirements
A list of technologies used within the project:
* [Python](https://www.python.org/downloads/release/python-370/): Version  3.7.2 
* [Google Spreadsheets APIs](https://developers.google.com/sheets/api/quickstart/python): Version current
* [AlmaTools](https://github.com/nlnzcollservices/alma-tools): Vesion 3
* [Exiftool](https://exiftool.org/): Version 12.10
* [PyExifTool](https://smarnach.github.io/pyexiftool/) : Version 0.1.1
* [Downloader](https://github.com/nlnzcollservices/file-downloader): Version downloader_light_modified
* [Rosetta sip factory](https://github.com/NLNZDigitalPreservation/rosetta_sip_factory): Version 0.1.9
* [beautifulsoup4](https://https://www.crummy.com/software/BeautifulSoup/bs4/doc/): Version 4.9.1
* [configparser](https://docs.python.org/3/library/configparser.html): Version 5.0.0
* [dateparser](https://pypi.org/project/dateparser/): Version 0.7.6
* [feedparser](https://pypi.org/project/feedparser/): Version 5.2.1
* [gspread](https://gspread.readthedocs.io/en/latest/): Version 3.6.0
* [httplib2](https://pypi.org/project/httplib2/): Version 0.18.1
* [lxml](https://pypi.org/project/lxml/): Version 4.5.2
* [nltk](https://pypi.org/project/nltk/): Version 3.5
* [openpyxl](https://pypi.org/project/openpyxl/): Version 3.0.4
* [peewee](http://docs.peewee-orm.com/en/latest/): Version 3.13.3
* [pymarc](https://pypi.org/project/pymarc/): Version 4.0.0
* [requests](https://pypi.org/project/requests/): Version 2.24.0
* [urllib3](https://pypi.org/project/urllib3/): Version 1.25.9

  ## Additional technologies to set up:
  
  * Gain Cascade access to project_folder and server_side_deposite folder.
  * Set Exlibris sandbox and production keys on [developers website](https://developers.exlibrisgroup.com/) 
  * Obtain permissions for Exlibris Rosetta SIP related APIs (given individually by PRC based on system credentials and manager's approval)

### Configuration Files

1)`settings.py` and `settings_prod.py` are used for setting all the paths and also make initial structure of project folders
2) 'sectrets' - contains Alma API keys for production and sandbox
3) 'client_sectets.json' - contains Google spreadsheet credentials


## Usage Examples

### Typical Use Cases
The script should be run between Thursday and Monday.

### User Interaction
The system takes a podcast dictionary (`podcast_dic.py`) as input.

## Maintenance and Support

### Updating Scripts
All updates should be tested with pytest or a similar tool.

### Common Issues and Troubleshooting
See existing errors and solutions [here](error_solution.txt).

## Security Aspects
The script checks downloaded files.
Currently, verification is disabled to avoid SSL errors.

### Data Handling
The podcast data is open access, and the library can process it and deliver it to everyone using the library website. However, usage for public services should be assessed due to copyright issues.

### Access Control
The script is located in the Cascade LD_working folder and could be accessible to any team member with Cascade access.

## Future Development
Updates will be made based on requests or technical needs.
The script could be wrapped into a GUI.

### Planned Improvements
There are no current plans. Changes will be made as needed.

### Contribution Guidelines

#### Reporting Bugs
To report a bug, please [open an issue](https://github.com/nlnzcollservices/podcast-collector/issues) and include a detailed description of the bug, steps to reproduce it, and any relevant information about your environment.

#### Requesting Features
If you have a feature request or suggestion, please [open an issue](https://github.com/nlnzcollservices/podcast-collector/issues) and provide a clear description of the feature you would like to see added.

#### Documentation
Contributions to the project's documentation are also welcome. If you would like to contribute to the documentation, please follow the same process as for code contributions.

#### Contact
If you have any questions or need assistance, you can reach out to the project maintainers at [collect.podcasts@gmail.com](collect.podcasts@gmail.com).
