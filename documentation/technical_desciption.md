# Technical description

## 1. Front matter

- **Title**: Podcasts
- **Team**: Legal Deposit
- **Created on**: 2020
- **Last updated**: 2020

## 2. Introduction

The podcast pipeline is designed to automate the collection and management of podcast episodes, their metadata, and their preservation in the National Library of New Zealand's systems. The pipeline interacts with Google Sheets, processes RSS metadata, and creates bibliographic records in Exlibris Alma. Additionally, it prepares audio files for long-term preservation in Exlibris Rosetta.

### a. Overview, Problem Description, or Summary

This pipeline automates the systematic collection of podcast episodes, tracks new releases from RSS feeds, gathers audio files and metadata, and updates bibliographic records. The script performs the following tasks:

- **Harvests podcast episodes** (via `podcasts0_harvester.py`)
- **Creates records** in Alma (via `podcasts1_create_record.py`)
- **Creates and submits SIPs** for Rosetta (via `podcasts2_make_sips.py`)
- **Manages holdings and items** (via `podcasts3_holdings_items.py`)
- **Updates records** with additional fields for global publishing (via `podcasts4_update_fields.py`)
- **Cleans files, databases, and spreadsheets**

The system allows cataloguers to enrich metadata through a Google Sheet interface. It ensures the podcasts are preserved in the library system and stable enough to resume from any step after interruptions.

### b. Glossary or Terminology

- **SIP**: Submission Information Package
- **Alma**: ExLibris Alma for managing bibliographic records
- **Rosetta**: Digital preservation system used for long-term storage

### c. Context or Background

Due to an increasing amount of digital materials, this pipeline was created to reduce the manual labor involved in preserving podcasts. Previously, episodes were preserved manually one by one. Automating this process saves time and improves consistency.

### d. Goals or Technical Requirements

- Automate the collection and preservation of podcast episodes
- Enrich and manage metadata in Google Sheets
- Create SIPs for ExLibris Rosetta
- Manage and update bibliographic records in ExLibris Alma

### e. Non-Goals or Out of Scope

- No support for podcasts without an RSS feed (future work)

### f. Future Goals

- Automate the collection of podcasts without RSS feeds via web scraping.
- Increase the number of podcast titles collected.

### g. Assumptions

- Podcasts must have RSS feeds for the pipeline to work without manual intervention.

## 3. Solutions

### a. Current Solution

The pipeline runs in multiple stages, with dependencies on the Google Sheets API, Alma API, and Rosetta.

- **Pros**:
  - Stable, rerunable, and interruptible
  - Fully automates the creation of bibliographic records with digital sources
- **Cons**:
  - Dependence on Google Sheets and external APIs (Alma, Rosetta)

### b. Suggested Solution / Design

The current pipeline is composed of several modules, each performing specific tasks:
- **Downloader module**: Downloads new podcast episodes based on RSS feeds.
- **Google Sheets API**: Enriches metadata via cataloguer interaction.
- **Alma and Rosetta APIs**: Manages bibliographic records and digital preservation.

**External Components**:
- Google Sheets API
- ExLibris Alma
- ExLibris Rosetta

**Business Logic**:
The pipeline logic is organized in separate scripts:
- **Harvester**: `podcasts0_harvester.py`
- **Record Creation**: `podcasts1_create_record.py`
- **SIP Creation**: `podcasts2_make_sips.py`
- **Holdings and Items Management**: `podcasts3_holdings_items.py`
- **Field Updates**: `podcasts4_update_fields.py`
- **Database Management**: `podcasts_database_handler.py`, `podcast_models.py`

### c. Test Plan

- **Unit Tests**:
  - Test for bibliographic record creation
- **Integration Tests**:
  - Test writing to Google Sheets
  - Test API calls to Alma and Rosetta

### d. Monitoring and Alerting Plan

- **Logging**: Implement logging for all key actions (file collection, record creation)
- **Monitoring**: Export to csv, Google spreadsheet, regular cleaning workflow.
- **Metrics**: Track the number of episodes collected and records created

### e. Release / Roll-out and Deployment Plan

- Full roll-out with continuous monitoring
- Adding new podcasts and removing old.

### f. Rollback Plan

In case of failure, the script can resume from the last completed step. Each stage is marked with flags, ensuring that no previous steps are repeated unnecessarily.

### g. Alternate Solutions / Designs

- **Manual collection**: 
  - **Cons**: Labor-intensive, error-prone


## 4. Further Considerations

### a. Impact on Other Teams

- **Cataloguers**: Will need to review and enrich metadata.
- **PRC**: Server side deposit load.

### b. Third-party Services Considerations

- **Google Sheets API**: Handle limitations in API availability and response times

### c. Cost Analysis

- **Operational Costs**: Minimal, ase uses free tools and existing software.
- **Infrastructure Costs**: No significant hardware or software expenses

### d. Security Considerations

- Secure API access using credentials stored in a protected folder
- Keeping in "secrets" Google spreadsheet key.

### e. Privacy Considerations

- Metadata should comply with New Zealand's legal deposit regulations particularly around the person names.


### f. Accessibility Considerations

- Cascade access.
- Developers permissions.
- API and spreadsheet keys.

## 5. Success Evaluation

### a. Impact

- **Performance Impact**: Significant reduction in manual effort
- **Security Impact**: Secure handling API keys
- **Cost Impact**: Low operational costs

### b. Metrics

- Number of episodes collected
- Number of records created
- Errors or failed attempts in creating records or SIPs

## 6. Work

### a. Work Estimates and Timelines

- Run the process weekly.

### b. Prioritization

-Prioritize new podcast tiles based on selective digital collecting desisions.

## 7. Deliberation

### a. Discussion

- None at this stage, as the system has been tested with live data.

### b. Open Questions

- How to handle podcasts without RSS feeds?
- How to handle monographic podcasts?
- Future changes related with RDA workflow.


## 8. References

- [ExLibris Alma API](https://developers.exlibrisgroup.com/alma/apis/)
- [Google Sheets API](https://developers.google.com/sheets/api)

### c. Acknowledgments

- Thanks to the Legal Deposit, Cataloguing and PRC team for their support and contributions.
