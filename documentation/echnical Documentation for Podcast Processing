# Podcast Processing System Documentation

## System Architecture Overview

### High-Level Diagram
Include a system architecture diagram showing how each script interacts with others and external systems (like Alma, Google Sheets, and email servers).

### Data Flow
Describe the flow of data through the system, from input to output, which can help in understanding how components are interlinked.

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
- Email servers

## Current State Functionality

### Main Script
- **Purpose:** Manages the overall workflow of the podcast processing system.
- **Functions:** Downloads emails, processes attachments, updates databases, manages records, and handles file clean-ups.
- **Key Features:**
  - Integration with Google Sheets for data management.
  - Use of external libraries for email handling and data parsing.
  - Extensive logging for debugging and tracking the process flow.

### Record Creation Script
- **Purpose:** Handles the creation and updating of bibliographic records in Alma.
- **Functions:** Parses spreadsheet data to create MARC records.
- **Key Features:**
  - Uses `pymarc` to handle MARC records.
  - Dynamically adds fields based on spreadsheet inputs.
  - Can potentially handle various podcast formats by adjusting MARC fields.

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

### Field Management Script
- **Purpose:** Updates bibliographic fields in the Alma system.
- **Functions:** Identifies and removes duplicate fields, adds specific fields, and updates records.
- **Key Features:**
  - Focus on maintaining record integrity by removing duplicates.
  - Capability to update records based on predefined rules and external inputs.

## Setup and Configuration

### Installation Requirements
List the requirements for setting up the system, including necessary libraries, external account setups (like Google API keys), and environment setup.

### Configuration Files
Explain any configuration files used (e.g., `settings.py` and `settings_prod.py`) and how they can be adjusted for different environments.

## Usage Examples

### Typical Use Cases
Provide scenarios or use cases that demonstrate how the system is used in daily operations.

### User Interaction
Explain how users interact with the system, what inputs they need to provide, and what outputs they can expect.

## Maintenance and Support

### Updating Scripts
Guidelines on how to update scripts when changes are needed.

### Common Issues and Troubleshooting
List common issues that might arise and provide basic troubleshooting steps.

## Security Aspects

### Data Handling
Describe how sensitive data is handled and any security measures in place to protect it.

### Access Control
Explain how access to the system is controlled and who has permission to make changes.

## Future Development

### Planned Improvements
Outline any planned upgrades or features that may be added to the system.

### Contribution Guidelines
If open to contributions, provide guidelines on how others can contribute to the system.
