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
- **Monitoring**: Ensure Google Sheets API and Alma API are responsive
- **Metrics**: Track the number of episodes collected and records created

### e. Release / Roll-out and Deployment Plan

The pipeline can be deployed in the following stages:
- Initial deployment and testing with a small set of podcasts
- Gradual increase in the number of titles covered
- Full roll-out with continuous monitoring

### f. Rollback Plan

In case of failure, the script can resume from the last completed step. Each stage is marked with flags, ensuring that no previous steps are repeated unnecessarily.

### g. Alternate Solutions / Designs

- **Alternative 1**: Manual collection
  - **Cons**: Labor-intensive, error-prone
- **Alternative 2**: Pre-built API for podcast collection
  - **Cons**: Limited customization and dependency on third-party services

## 4. Further Considerations

### a. Impact on Other Teams

- **Cataloguers**: Will need to review and enrich metadata
- **IT team**: Responsible for maintaining access to APIs and managing the infrastructure

### b. Third-party Services Considerations

- **Google Sheets API**: Ensure security and privacy when handling metadata
- **Alma and Rosetta APIs**: Handle potential limitations in API availability and response times

### c. Cost Analysis

- **Operational Costs**: Minimal, limited to API usage and server runtime
- **Infrastructure Costs**: No significant hardware or software expenses

### d. Security Considerations

- Secure API access using credentials stored in a protected folder
- Ensure proper handling of bibliographic data with no leaks

### e. Privacy Considerations

- Metadata should comply with New Zealand's legal deposit regulations
- Ensure that no personally identifiable information (PII) is collected or stored

### f. Accessibility Considerations

- No specific accessibility concerns as the system is automated with minimal manual interaction

## 5. Success Evaluation

### a. Impact

- **Performance Impact**: Significant reduction in manual effort
- **Security Impact**: Secure handling of data through encrypted API connections
- **Cost Impact**: Low operational costs

### b. Metrics

- Number of episodes collected
- Number of records created
- Errors or failed attempts in creating records or SIPs

## 6. Work

### a. Work Estimates and Timelines

- **Task 1**: Complete initial setup and testing (2 weeks)
- **Task 2**: Integrate additional podcast titles (3 weeks)

### b. Prioritization

- High priority: Automating podcast collection for existing feeds
- Medium priority: Expanding collection to podcasts without RSS feeds

### c. Milestones

- **Milestone 1**: Complete end-to-end pipeline for initial podcast title (Month 1)
- **Milestone 2**: Expand to full catalog of titles (Month 2)

## 7. Deliberation

### a. Discussion

- None at this stage, as the system has been tested with live data.

### b. Open Questions

- How to handle podcasts without RSS feeds?
- Future improvements for metadata enrichment?

## 8. End Matter

### a. Related Work

- Similar projects may be happening in other national libraries with similar legal deposit requirements.

### b. References

- [ExLibris Alma API](https://developers.exlibrisgroup.com/alma/apis/)
- [Google Sheets API](https://developers.google.com/sheets/api)

### c. Acknowledgments

- Thanks to the Legal Deposit team and the IT team for their support and contributions.
