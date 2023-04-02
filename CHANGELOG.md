# Change Log
Notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres now to [Calendar Versioning](http://calver.org/).

## [23.04.02]
This release is contributing to cloud governance at enterprise scale. New features include following capabilities:
- management by exception with AWS Incident Manager - every budget alert is now a documented incident record with contextualised tags
- distribution of incident attachments with lambda function URLs - including throttling
- automated creation of monthly cost reports in Excel format - by cost center and by organizational units
- monitoring dashboard now provides business indicators aside the technical indicators
- automated metric of daily costs by cost center - displayed in the dashboard
- automated metering of preparation and purge transactions - displayed in the dashboard
- automated creation of weekly inventories (CSV)
- strict control of settings semantics while loading related files
- single place in settings file for default configuration of accounts
- tags used by SPA for state management can be configured in settings
- extension of the configuration from external CSV files - for collective management with FinOps team, SecOp team, etc.
- easier on-boarding of contributors after code restructuring and renaming
- additional pytest marks for wip-tests, unit-tests, integration-tests
- additional on-demand lambda functions for specific situations: release all accounts, reset all accounts
- expand feature files and architectural diagrams to explain the behavior and the structure of the software
- SPA can manage the AWS account where it has been deployed


## [22.12.17]
Since its inception, SPA handle accounts located in selected organizational units. This setup enables efficient automation of large number of accounts. With this version, SPA can also manage selected accounts, irrespectively of their location in organizational units.

What can you do with SPA?
- set a pace for maintenance windows - daily, weekly, monthly, or other cron-based expression
- tag or re-tag accounts on every maintenance window
- purge cloud resources depending on their tags or on their age - or make it optional
- set or change billing alerts for each account
- consolidate billing alerts to a single Microsoft Teams channel, or to central email addresses
- adapt to your specific needs the purge script and the preparation script

We start to document changes after the solution has been used in production at Reply for 6 months. In addition, we got feedback from external enterprises for past 3 months, and integrated most suggestions into the solution.

## [0.0.1] - 2022-05-19

Initial release of Sustainable Personal Accounts package on GitHub.
