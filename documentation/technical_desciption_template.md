# Technical description

## 1. Front matter

Title **Podcasts**

Author(s)?

Team **Legal Deposit**

Reviewer(s)? 

Created on **2020**

Last updated **2020**

Epic, ticket, issue, or task tracker reference link ?

## 2. Introduction
The following script is bulky collecting podcast episodes, interracting with google spreadsheet to write rss metadata and collecting back enriched metadata, creating bibliograhic records in Exlibris Alma and managing audio files to be preserved with Exlibris Rosetta.

### a. Overview, Problem Description, Summary, or Abstract

    Summary of the problem (from the perspective of the user), the context, suggested solution, and the stakeholders. 

The aim of the script is a systematic automative collecting of podcast episodes and managing audio file preservation in the library system. It contineously tracks new episodes published in rss feed, collects audio files and episodes' metadata and places them to human readable and machine readable source, to allow cataloguing team to make changes and add new bibliographic inforamtion, creatse full bibliographic records, checks files, creates SIPs and places them in a special folder for futher preservation, finishes aquisition part by creating items and updates the existing record with additional field to allow them be published worldwide. It is stable againsed and can be run from any step after interruption. 

The script contains several code blocks and database. Each block is responsible for one of the steps in the pipelinse
 
 - harvesting episodes
 - creating record
 - creating and submitting SIP
 - finishin record
 - cleaning files, db and spreadsheet
 
 and special operations 
 
 - database
 - Alma APIs
 - general settings

There are the flags which mark the end of each step, and script will not run the next one, until previous is finished, which allow to run and rerun script as many times as required.

The script is using Downloader module, Google spreadsheet and APIs, JHOVe and Exiftool. Could be combined with Macro Express  and batch script to run automatucally on schedule.

## b. Glossary  or Terminology

    New terms you come across as you research your design or terms you may suspect your readers/stakeholders not to know.  

### c. Context or Background

    Reasons why the problem is worth solving
    Origin of the problem
    How the problem affects users and company goals
    Past efforts made to solve the solution and why they were not effective
    How the product relates to team goals, OKRs
    How the solution fits into the overall product roadmap and strategy
    How the solution fits into the technical strategy
The purpuse of script to reduce manual work as much as possible in context of increasing amount of digital materials.  The podcast episodes previously were preserved manually one by one. So the script helps to safe time. 

### d. Goals or Product and Technical Requirements

    Product requirements in the form of user stories 
    Technical requirements

### e. Non-Goals or Out of Scope

    Product and technical requirements that will be disregarded

### f. Future Goals

    Product and technical requirements slated for a future time

Increase amount of collecting podcast titles. And attach scrapers for podcast without feed.


### g. Assumptions

    Conditions and resources that need to be present and accessible for the solution to work as described. 
    
For stable and continuess work podcast should have rss feeds, the same title, the same format of title, otherwise additional adjustment required.

## 3. Solutions

### a. Current or Existing Solution / Design

    Current solution description
    Pros and cons of the current solution
Pros:
Stable, rerunable, interruptable, includes all the stages of creating library record with digital source.

Cons:

Depending on cataloguing impact, Google account and APIs, Alma APIs

### b. Suggested or Proposed Solution / Design 

    External components that the solution will interact with and that it will alter
    Dependencies of the current solution
    Pros and cons of the proposed  solution 
    Data Model / Schema Changes
        Schema definitions
        New data models
        Modified data models
        Data validation methods
    Business Logic
        API changes
        Pseudocode
        Flowcharts
        Error states
        Failure scenarios
        Conditions that lead to errors and failures
        Limitations
    Presentation Layer
        User requirements
        UX changes
        UI changes
        Wireframes with descriptions
        Links to UI/UX designer’s work
        Mobile concerns
        Web concerns
        UI states
        Error handling
    Other questions to answer
        How will the solution scale?
        What are the limitations of the solution?
        How will it recover in the event of a failure?
        How will it cope with future requirements?

c. Test Plan

    Explanations of how the tests will make sure user requirements are met
    Unit tests
Will make a test for checking bib record.
    Integrations tests
Will make Test for writing to spreadsheet, Test for get API
    QA

d. Monitoring and Alerting Plan 

    Logging plan and tools
    Monitoring plan and tools
    Metrics to be used to measure health
    How to ensure observability
    Alerting plan and tools

e. Release / Roll-out and Deployment Plan

    Deployment architecture 
    Deployment environments
    Phased roll-out plan e.g. using feature flags
    Plan outlining how to communicate changes to the users, for example, with release notes

f. Rollback Plan

    Detailed and specific liabilities 
    Plan to reduce liabilities
    Plan describing how to prevent other components, services, and systems from being affected

g. Alternate Solutions / Designs

    Short summary statement for each alternative solution
    Pros and cons for each alternative
    Reasons why each solution couldn’t work 
    Ways in which alternatives were inferior to the proposed solution
    Migration plan to next best alternative in case the proposed solution falls through

4. Further Considerations

a. Impact on other teams

    How will this increase the work of other people?

b. Third-party services and platforms considerations

    Is it really worth it compared to building the service in-house?
    What are some of the security and privacy concerns associated with the services/platforms?
    How much will it cost?
    How will it scale?
    What possible future issues are anticipated? 

c. Cost analysis

    What is the cost to run the solution per day?
    What does it cost to roll it out? 

d. Security considerations

    What are the potential threats?
    How will they be mitigated?
    How will the solution affect the security of other components, services, and systems?

e. Privacy considerations

    Does the solution follow local laws and legal policies on data privacy?
    How does the solution protect users’ data privacy?
    What are some of the tradeoffs between personalization and privacy in the solution? 

f. Regional considerations

    What is the impact of internationalization and localization on the solution?
    What are the latency issues?
    What are the legal concerns?
    What is the state of service availability?
    How will data transfer across regions be achieved and what are the concerns here? 

g. Accessibility considerations

    How accessible is the solution?
    What tools will you use to evaluate its accessibility? 

h. Operational considerations

    Does this solution cause adverse aftereffects?
    How will data be recovered in case of failure?
    How will the solution recover in case of a failure?
    How will operational costs be kept low while delivering increased value to the users? 

i. Risks

    What risks are being undertaken with this solution?
    Are there risks that once taken can’t be walked back?
    What is the cost-benefit analysis of taking these risks? 

j. Support considerations

    How will the support team get across information to users about common issues they may face while interacting with the changes?
    How will we ensure that the users are satisfied with the solution and can interact with it with minimal support?
    Who is responsible for the maintenance of the solution?
    How will knowledge transfer be accomplished if the project owner is unavailable? 

5. Success Evaluation

a. Impact

    Security impact
    Performance impact
    Cost impact
    Impact on other components and services

b. Metrics

    List of metrics to capture
    Tools to capture and measure metrics

6. Work

a. Work estimates and timelines

    List of specific, measurable, and time-bound tasks
    Resources needed to finish each task
    Time estimates for how long each task needs to be completed

b. Prioritization

    Categorization of tasks by urgency and impact

c. Milestones

    Dated checkpoints when significant chunks of work will have been completed
    Metrics to indicate the passing of the milestone

d. Future work

    List of tasks that will be completed in the future

7. Deliberation

a. Discussion

    Elements of the solution that members of the team do not agree on and need to be debated further to reach a consensus.

b. Open Questions

    Questions about things you do not know the answers to or are unsure that you pose to the team and stakeholders for their input. These may include aspects of the problem you don’t know how to resolve yet. 

8. End Matter

a. Related Work

    Any work external to the proposed solution that is similar to it in some way and is worked on by different teams. It’s important to know this to enable knowledge sharing between such teams when faced with related problems. 

b. References

    Links to documents and resources that you used when coming up with your design and wish to credit. 

c. Acknowledgments

    Credit people who have contributed to the design that you wish to recognize.
