# Proposal for Updates to Podcast Processing System

## Overview

The podcast processing pipeline currently in place manages the workflow of podcast data from harvesting to record creation and SIP production. This proposal outlines the updates required to enhance the system's functionality based on recent requirements from the cataloguing team.

## Proposed Updates

### 1. Spreadsheet Changes
- **Addition of "Date harvested" Column**: Introduce a new column in the spreadsheet to record the date when podcast titles are added. This will facilitate tracking of when episodes were discovered.
- **Inclusion of "Episode Numbering" Column**: Add a column to handle episode numbering in titles. This will be used to separate the episode number from the rest of the title, enabling easier processing. Should allow cataloguing to change db info.
- **Inclusion of "245 title" Column**: Add a column to keep title text separated from number (if they exist) for 245 field. Should allow cataloguing to change db info.
- **Inclusion of "rss season" and "rss_number" Columns**: Add 2 columns with episode  season and number from rss feed (if they exist).

### 2. MARC Record Changes
- **Usage of Publication Date for 490 $v and 800/830 $v**: Switch to using the publication date for these fields in all titles. This will ensure consistency and accuracy in bibliographic records.
- **Discontinuation of the 100 Field**: The 100 field will no longer be used in the processing. Repurpose the column on the spreadsheet originally designated for the 100 field.

### 3. System Integration
- **Integration of iTunes Elements**: Extract and include `<itunes:season>` and `<itunes:episode>` elements from RSS feeds into the spreadsheet. This information can enhance the metadata of the podcast episodes.

### 4. Script Updates
- **Script Modification for New Spreadsheet Columns**: Modify the existing scripts to accommodate the new columns for "Date harvested" and "Episode Numbering" in the spreadsheet.
- **Enhanced Logging**: Improve logging functionality to include details of the date harvested and episode numbering changes.

## Implementation Plan

1. **Requirement Analysis**: Understand the exact requirements and dependencies of the updates.
2. **Code Modification**: Update the existing scripts to accommodate the new spreadsheet columns and MARC record changes.
3. **Testing**: Thoroughly test the updated scripts to ensure they work as expected.
4. **Deployment**: Deploy the updated scripts to the production environment.
5. **Documentation Update**: Update the technical documentation to reflect the changes made.

## Timeline

- **Requirement Analysis**: 1 week
- **Code Modification**: 2 weeks
- **Testing**: 1 week
- **Deployment**: 1 week
- **Documentation Update**: Ongoing, to be completed during and after implementation

## Resources Required

- **Development Team**: 1 developer for code modifications and testing
- **Testing Environment**: Access to a test environment to validate changes before deployment
- **Documentation Team**: 1 technical writer to update the documentation

## Risks and Mitigation

- **Data Loss**: Implement backup mechanisms to prevent data loss during the update process.
- **Integration Challenges**: Ensure close collaboration with the team responsible for integrating iTunes elements to address any challenges.
- **User Acceptance**: Engage with users early in the process to gather feedback and ensure the updates meet their requirements.

## Conclusion

This proposal outlines the updates required to enhance the podcast processing system in response to the cataloguing team's requirements. By implementing these updates, we aim to improve the accuracy and efficiency of the system while meeting the evolving needs of our users.

Please let me know if you need any further details or adjustments to this proposal.
