# Inspect a production system

## Overview
SPA features a distributed architecture, and it does not have a single interface that can be used to control everything. In this workbook we review the main components of the system and ways to inspect their behavior. We have written this for system engineers, our peers. And we hope they will find here useful guidance during their troubleshooting of production deployments.

1. [Understand the components of the architecture](#step-1)
2. [Inspect account tags](#step-2)
3. [Inspect the event bus and event handlers](#step-3)
4. [Inspect the monitoring dashboard](#step-4)
5. [Inspect incident records](#step-5)
6. [Inspect account inventories](#step-6)
7. [Inspect cost reports](#step-7)
8. [Inspect activity reports](#step-8)

## Prerequisites
- You have credentials to access the AWS Console
- You have received permissions to manage the AWS Organization where SPA has been deployed
- You have received permissions to access the AWS account where SPA has been deployed

## Step 1. Understand the components of the architecture <a id="step-1"></a>

In this workbook we focus on following components of the SPA architecture:
* Account Tags
* Event bus and event handlers
* Monitoring Dashboard
* Incident Manager
* Account Inventories
* Cost Reports

In following steps we assume following names for accounts and OU that we use:
- `Management` is the top-level account of the AWS Organization
- `Automation` is the account where SPA has been deployed
- `Alice` and `Bob` are two personal accounts managed by SPA
- `Sandboxes` is the Organizational Unit (OU) that contains `Alice` and `Bob` accounts

## Step 2. Inspect account tags <a id="step-2"></a>

SPA works by tagging AWS accounts, so by looking at account tags you can ensure proper transitions across account states. You can also set or change a tag by yourself to trigger actions from SPA.

To inspect account tags:
- From the AWS Console of `Management`, the top-level account of the AWS Organization, select the service 'AWS Organizations'
- Search for the account `Alice` or unfold the OU `Sandboxes`
- Select the account `Alice` to view account details

During normal operations, an account managed by SPA should feature several tags, including those specified in settings files. The following example reflects a released account:
| Key            | Value             |
| ---            | ---               |
| account-holder | alice@example.com |
| account-state  | released          |
| cost-center    | Example Corp.     |
| cost-owner     | bob@example.com   |

The tag `account-holder` reflects the email address assigned to the AWS account. The value of the tag `account-state` can have one of following values: `vanilla`, `assigned`, `released` or `expired`. Other tags have static values configured in SPA settings for an OU level or for an account.

SPA detects the creation, the move and the tagging of AWS accounts. When an AWS account has been properly on-boarded in SPA, you can track its state changes by inspecting the value of tag `account-state` over time. You can also change this tag manually to trigger a specific transaction, or to fix an issue by yourself.

To change account tags:
- From the AWS Console of `Management`, the top-level account of the AWS Organization, select the service 'AWS Organizations'
- Search for the account `Alice` or unfold the OU `Sandboxes`
- Select the account `Alice` to view account details
- Click on button `Manage tags`
- Set the target states for tags and click on button `Save changes`

To on-board an account, set the account tag `account-state` to value `vanilla`. Over some minutes, the account tag will move to values `assigned` and then `released`.

To start maintenance of an account, set the account tag `account-state` to value `expired`. Later on, the tag should move to values `assigned` then `released`.

If you observe some anomalies, or if you have to change the states of several accounts, then refer to the workbook devoted to [the management of account states](./manage-account-states.md).

## Step 3. Inspect the event bus and event handlers <a id="step-3"></a>

SPA listens events from the default bus of `Automation`, the account where it has been deployed. Events that match patterns defined in EventBridge rules are passed to Lambda functions. You can inspect the CloudWatch logs of each Lambda function to monitor activities of the system. The Lambda function `SpaOnAccountEvent` is seeing every transition of accounts, therefore it is a good place to start.

Perform following activities to on-board an account and to monitor the process:
- From the AWS Console of `Management`, the top-level account of the AWS Organization, select the service 'AWS Organizations'
- Search for the account `Alice` or unfold the OU `Sandboxes`
- Select the account `Alice` to view account details
- Click on button `Manage tags`
- Set the tags `account-state` to `vanilla` then click on button `Save changes`
- Switch to the AWS Console of `Automation`, the AWS account where SPA has been deployed, and select the service 'Lambda'
- Search for the Lambda function `SpaOnAccountEvent`
- Click on the tab 'Monitor' then on button 'View CloudWatch logs'
- Click on the most recent log stream
- You should get the full sequence of state changes over a couple of minutes: `CreatedAccount`, `AssignedAccount`, `PreparedAccount` then `ReleasedAccount`.

If the Lambda function `SpaOnAccountEvent` has no CloudWatch logs despite the creation or tagging of AWS accounts, then it is likely that events emitted by AWS do not reach the event bus of SPA.

To inspect the forwarding of AWS Organizations events to SPA:
- From the AWS Console of `Management`, the top-level account of the AWS Organization, select the service 'Amazon EventBridge'
- ⚠️ Select the region `US East (N. Virginia) us-east-1`
- In the left panel, click on 'Rules'
- Look for a rule that forward events from AWS Organizations to the default event bus of SPA

A pattern that matches events from AWS Organizations:
```json
{"detail":{"eventSource":["organizations.amazonaws.com"]}}
```

The ARN of the default event bus should mention the region where SPA has been deployed, similar to the following:
```
arn:aws:events:eu-west-1:123456789012:event-bus/default
```

To inspect the forwarding of Console Login events to SPA:
- From the AWS Console of `Management`, the top-level account of the AWS Organization, select the service 'Amazon EventBridge'
- ⚠️ Select the region where your IAM Identity Center has been deployed, e.g., `Europe (Ireland) eu-west-1`
- In the left panel, click on 'Rules'
- Look for a rule that forward sign-in events to the default event bus of SPA

A pattern that matches sign-in events from AWS:
```json
{"detail":{"eventSource":["signin.amazonaws.com"],"eventName":["ConsoleLogin"]}}
```

The ARN of the default event bus should mention the region where SPA has been deployed, similar to the following:
```
arn:aws:events:eu-west-1:123456789012:event-bus/default
```

For additional guidance on events, you may want to double-check the [Full setup of SPA](./full-setup-of-spa.md) workbook.

## Step 4. Inspect the monitoring dashboard <a id="step-4"></a>

SPA comes with a monitoring dashboard that features a combination of technical and functional indicators.
To ensure complete observability of SPA operations, visit the CloudWatch dashboard in the `Automation` account. Metrics for Lambda and DynamoDB should reflect your activities on personal accounts.

To inspect the monitoring dashboard:
- From the AWS Console of `Automation`, the AWS account where SPA has been deployed, select the service 'CloudWatch'
- In the left panel, click on 'Dashboards'
- Select the custom dashboard that has been deployed with SPA, e.g., `SpaCockpit-eu-west-1`

Adjust the time scale to one week or more. You can click on '1w' or you can pick up a custom scale, for example, '4w' or '3M'. The default time scale used by CloudWatch may be tto short for SPA operations.

The monitoring dashboard features a comprehensive set of widgets:

- Banner - This is fixed Markdown text that is coming from SPA settings. You can customize the banner like you want, for example, put important contact information or reminders, etc.

- Daily costs by cost center - SPA computes every night a custom metric on usage costs. Here you can detect abnormal evolutions of your costs before the AWS invoices reach you.

- Transactions by label - SPA meters internal activities as transaction: account on-boarding, account maintenance, and console login. Data points here reflect the quantity of accounts managed by SPA, and actual usage of accounts by their holders.

- Transactions by cost center - SPA provides a breakdown of transactions by cost center. These data points reflect the quantity of accounts managed for each cost center, and also the number of console logins for each cost center.

- Events by label - This widget reflects the state transitions of accounts managed by SPA. During normal operations, it should display a series of vertical dots on each maintenance window.

- Exceptions by label - This widget reflects the incident records that are created on exceptions. You can monitor here the budget alerts and the abnormal logins to the console.

- Lambda invocations - With this technical indicator you can verify that SPA behaves correctly, and you can also detect some unusual invocations.

- Lambda durations - With this technical indicator you can check that no Lambda is getting close to the hard limit of 15 minutes of execution.

- Lambda errors - If this is not sticking to zero, then there is a run-time error or a bug.

- DynamoDB read capacity units - With this technical indicator you can monitor the costs of DynamoDB.

- DynamoDB write capacity units - With this technical indicator you can monitor the costs of DynamoDB.

- DynamoDB errors - If this is not at zero, then there is a run-time error.

## Step 5. Inspect incident records <a id="step-5"></a>

SPA automates the work on AWS accounts as much as possible, so that human beings are involved only on exceptional situations. When this happens, SPA creates incident records in AWS Incident Manager.

To inspect the monitoring dashboard:
- From the AWS Console of `Automation`, the AWS account where SPA has been deployed, select the service 'AWS Systems Manager'
- In the left panel, click on 'Incident Manager'

It is perfectly normal to get no open incidents, until a first exception is detected.

SPA handles following exceptions:

- Budget alert - This happens when costs go beyond budget threshold set for an account. The incident record should be closed after discussion with the person using this account.

- Console Login with IAM User - This happens when someone bypasses Single Sign-On (SSO) and authenticates directly to an AWS account. The incident record signals a potential backdoor that needs additional analysis.

- Console Login with root credentials - This happens when someone authenticates with the email address attached to an AWS account. The incident record flags a potential misuse of AWS account, that should not happen under regular account operations.

- Failed CodeBuild execution - This happens when SPA cannot complete either a preparation activity or a purge activity in an AWS account that it manages. The incident record should be investigated to troubleshoot CodeBuild on the target account.

- Failed maintenance transaction - This happens when an expiration event has been observed, but no related released event. The operator should check potential failures in the purge ran by CodeBuild on the target account.

- Failed on-boarding transaction - This happens when a vanilla event has been observed, but no released event. The operator should check potential failure in the preparation ran by CodeBuild on the target account.

- Generic exception - This is used by experimental code for some situations.


## Step 6. Inspect account inventories <a id="step-6"></a>

SPA produces inventories of AWS accounts that it manages. Inventories are useful for quick inspection of a large number of accounts.

To inspect most recent inventory:
- From the AWS Console of `Automation`, the AWS account where SPA has been deployed, select the service 'S3'
- Select the reporting S3 bucket that is created with SPA
- Click on prefix `SpaReports`
- Click on `Inventories`
- Click on the selected year, e.g., `2023`
- Click on the selected month, e.g., `05` for May
- Click on the most recent CSV file, e.g., `2023-05-20-inventory.csv`
- Click on the 'Download' button to get a copy of the file on your computer
- Open the file with a tool adapted to CSV files

For each AWS account, the inventory provides information that is useful on transverse analysis:
- Account id - The 12 digits that are unique across AWS
- Account name - Is account name aligned with corporate policies?
- Account email - Is account email internal or external to the company?
- Account state - Should be `released`, else there is an issue
- Date and time of last console login - Is the account really used?
- Cost center - Are costs for this account reported accurately for FinOps reports?
- Cost owner - Is cost ownership tagged accurately?
- Organizational Unit that contains the account - Is the account at the right place in the AWS Organization?
- Last login - Is account really used?

The CSV format has been selected for easy integration with downwards processes. For example, these CSV files can be pushed to a data warehouse for historical analysis and processing. While such automation is going beyond SPA itself, it can be easily configured with S3 events on the reporting bucket fed by SPA.

## Step 7. Inspect cost reports <a id="step-7"></a>

SPA contributes to FinOps with the production of monthly reports. There are monthly reports for each cost center on their service usage, e.g., S3 and EC2 for the account of `Alice` and AppStream for the account of `Bob`. These reports are posted on the SPA S3 bucket both as CSV files and as Excel files. There are also summary reports that reflect monthly costs either by service or by charge type.

To get and to inspect some service usage report for a given cost center:
- From the AWS Console of `Automation`, the AWS account where SPA has been deployed, select the service 'S3'
- Select the reporting S3 bucket that is created with SPA
- Click on prefix `SpaReports`
- Click on `Costs`
- Click on the selected cost center, e.g., `StormFR`
- Click on the most recent Excel file, e.g., `2023-04-StormFR-services.xlsx`
- Click on the 'Download' button to get a copy of the file on your computer
- Open the file with and inspect it
- There is also a CSV version of the file, for automated integration into downward processes

To get and to inspect a summary of service costs across the entire AWS Organization:
- From the AWS Console of `Automation`, the AWS account where SPA has been deployed, select the service 'S3'
- Select the reporting S3 bucket that is created with SPA
- Click on prefix `SpaReports`
- Click on `Costs`
- Click on `Summary`
- Click on the most recent Excel file, e.g., `2023-04-Summary-services.xlsx`
- Click on the 'Download' button to get a copy of the file on your computer
- Open the file with and inspect it
- There is also a CSV version of the file, for automated integration into downward processes

To get and to inspect charge types across the entire AWS Organization:
- From the AWS Console of `Automation`, the AWS account where SPA has been deployed, select the service 'S3'
- Select the reporting S3 bucket that is created with SPA
- Click on prefix `SpaReports`
- Click on `Costs`
- Click on `Summary`
- Click on the most recent Excel file, e.g., `2023-04-Summary-charges.xlsx`
- Click on the 'Download' button to get a copy of the file on your computer
- Open the file with and inspect it
- There is also a CSV version of the file, for automated integration into downward processes

Note that they may have other versions of the same file if you have asked SPA to convert currencies, e.g. `2023-04-Summary-charges-EUR.xlsx` in Euros instead of USD. This is driven by optional features in SPA settings.

## Step 8. Inspect activity reports <a id="step-8"></a>

SPA creates a variety of activity records for accounts that it manages. The main objective of activity records is to report to each cost center the actual service provided by SPA. Activity records relates to account on-boarding, to account maintenance, but also to console logins, etc.

To get and to inspect some activity report for a given cost center:
- From the AWS Console of `Automation`, the AWS account where SPA has been deployed, select the service 'S3'
- Select the reporting S3 bucket that is created with SPA
- Click on prefix `SpaReports`
- Click on `Activities`
- Click on the selected cost center, e.g., `StormFR`
- Click on the most recent Excel file, e.g., `2023-06-StormFR-activities.csv`
- Click on the 'Download' button to get a copy of the file on your computer
- Open the file with and inspect it

The CSV format has been selected for easy integration with downwards processes. For example, these CSV files can be pushed to a data warehouse for historical analysis and processing. While such automation is going beyond SPA itself, it can be easily configured with S3 events on the reporting bucket fed by SPA.

## Follow-up

* Inspect SCP set for the OU managed by SPA, with [the workbook on preventive controls](./manage-preventive-controls.md)

