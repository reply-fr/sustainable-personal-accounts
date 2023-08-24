# Change Log
Notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres now to [Calendar Versioning](http://calver.org/).


## Unreleased

### Added
- introduce a buildspec to update a SPA environment - #117
- add history of work done on this project - #118
- add command "make history" to record project issues and progress - #118
- add nat gateways to resources that should be purged after some time
- introduce a SCP policy to prevent usage of root account on non-sandboxes accounts - #116

### Fixed
- fix: consolidate fixtures in conftest
- fix E721 errors reported by make lint
- list generated reports in debug mode
- use pip from virtual environment to package the lambda zip file
- use standard command for the setup of cdk
- use the right function to compute cost reports

### Changed
- align with reference .gitignore used at Reply
- iterate on the system inspection workbook - #119
- use lines instead of stacked areas for widget on cost center activities - #119
- auto-format features files as per Gherkin specification
- reduce duration of pre-commit validation
- use floats instead of strings during computation of cost reports
- restructure commands in Makefile

### Removed


## [23.08.03]
This release provides essentially bug fixes and small improvements.

### Added
- record identities on console logins
- prevent accounts to leave the organization

### Fixed
- fix Lambda errors
- fix typos in README

### Changed
- bump to CDK 2.89
- set the span of the monitoring dashboard to 4 weeks
- improve the workbook related to system inspection
- integrate changes from AWS on granular permissions related to Cost Explorer

## [23.07.02]
This release is adding console logins to the transactions managed by SPA. It also expands business support and brings several ptimisations:
- revise visual diagrams on business functions
- improve README
- new FAQ document
- reduce delay in the computation of daily cost metric
- align cost reports with the AWS invoicing cycle
- improve clarity of titles and content of incident records
- add a workbook on cost management
- add a workbook to assist on system inspection
- improve sample SCP to make it compatible with Control Tower
- improve the full setup workbook
- improve accuracy of cost and usage reports
- produce cost and usage reports in different currencies, e.g., EUR
- improve documentation on account on-boarding
- add a workbook on account state management
- reduce the number of cloud resources to prevent quota limitation in CloudFormation
- add IAM password enforcement to the standard preparation buildspec
- add technical indicators on DynamoDB to the monitoring dashboard
- add workbook related to console login management
- add exception on console login with IAM user or with root credentials
- mention date of last login in the inventories of accounts
- record console login events
- normalize documentation on `@example.com` domain
- add new commands `make rebase` and `make push` for developers
- add a workbook related to preventive controls with SCP
- make tests runnable without access to the Internet
- add monthly reports on AWS charges
- structure cost and usage reports with cost center and with Organizational Units
- include environment identifiers in names of DynamoDB tables to prevent deployment collisions
- provide a sample IAM policy for permission given to SPA on management account
- add workbook to configure the transmission of reports over email
- add markdown template for messages sent with cost reports
- send messages over email to target recipients
- add tests to ensure that data is encrypted at rest -- S3 and DynamoDB
- move to recent versions of CDK
- align feature files with code capabilities
- refactor code
- fix bugs and typos

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
