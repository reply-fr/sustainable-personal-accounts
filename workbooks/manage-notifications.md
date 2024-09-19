# Manage notifications

THIS PAGE IS UNDER CONSTRUCTION

## Overview

In this workbook we dive deep on notification management for AWS accounts. The objective is to explain automation brought by SPA on notifications, so that you can collect confirmations from end users on key documents transmitted to them over email.

1. [Understand the notifications system](#step-1)
2. [Configure the origin email address in SPA settings](#step-2)
3. [Prepare notifications](#step-3)
4. [Assign notifications to accounts](#step-4)
5. [Contextualize notifications](#step-5)
6. [Inspect notifications](#step-6)
7. [Inspect notifications reports](#step-7)

## Prerequisites

- You have credentials to access the AWS Console
- You have the permission to access the CloudWatch Console of the `Automation` account (where SPA has been deployed)

## Step 1: Understand the notifications system <a id="step-1"></a>

In the context of SPA, notifications are email messages that can be confirmed by end-users. Notifications can be used for spreading terms and conditions to newcomers, and to collect validations automatically. Another use case is the transmission of important news and informative messages, through the same system.

Multiple notifications can be setup in the system. In that case, SPA transmits one notification on each maintenance cycle, until all notifications have been processed. If you add a notification at some point, it will be transmitted on the next maintenance cycle.

## Step 2: Configure the origin email address in SPA settings <a id="step-2"></a>

This step can be completed with following activities:

- Open the SPA settings file in the editor of your choice
- Look for the keyword `with_origin_email_recipient:` and paste the email address that was verified previously
- Save the SPA settings file and deploy the new configuration with the command `make deploy`

To validate the deployment, you can inspect Lambda functions `SpaOnMonthlyCostsReport` of SPA in the AWS account where SPA has been deployed. The environment variable `ORIGIN_EMAIL_RECIPIENT` should reflect the origin email address used by SES.

## Step 3: Prepare notifications <a id="step-3"></a>

Notifications are email messages that are built from documents. Documents are regular Markdown files, with a YAML header. This format is also known as "frontmatter". In addition, Markdown content can feature placeholders for text that can come either from the frontmatter section, or from other sources.

```markdown
---
title: User Agreement for Personal Sandbox AWS Account
---
# {{ title }}

This User Agreement ("Agreement") governs your use of the personal AWS sandbox account ("Account") provided to you by {{ corporation }}. By accessing or using this Sandbox Account, you agree to be bound by this Agreement.

...
```

## Step 4: Assign notifications to accounts <a id="step-4"></a>

Notifications are configured as named documents. Names are processed in alphabetical order. This may be important for you if you configure multiple notifications and want to manage the order of email messages ent to end-users. Here is an example of a notification for general terms of use of SPA:

```yaml
defaults:  # applies to every account

  notifications:
    feature: enabled
    documents:
      00_TermsOfUse: fixtures/documents/terms_of_use.md
```

The addition of notifications is performed by the modification of settings:

- Open the settings file of SPA, e.g., `settings.yaml`, with you preferred text editor
- In the section `organizational_units`, set notifications for each OU managed collectively by SPA
- In the section `accounts`, set notifications for each accounts managed individually by SPA
- In the section `default`, set notifications to be sent to every account managed by SPA
- Save and close the settings file
- Use the command `make deploy` to update the SPA stack on AWS

## Step 5: Contextualize notifications <a id="step-5"></a>

Contextualization allows the re-use of documents, but with different content provided to end-users. For example, you manage one single document for Terms of Use, but the name of the entity in charge of your account can vary. Notifications can be contextualized globally, at Organizational Unit level, or at the account level.

Here is an example where you bind a generic template to your specific enterprise:

```yaml
defaults:

  notifications:  # global setup
    feature: enabled
    documents:
      00_TermsOfUse: fixtures/documents/terms_of_use.md
    placeholders:
      corporation: 'Example.com Inc.'

```

Here is another example when multiple enterprises share SPA services:

```yaml
defaults:

  notifications:  # global setup
    feature: enabled
    documents:
      00_TermsOfUse: fixtures/documents/terms_of_use.md

organizational_units:

  - identifier: 'ou-1234'
    note: 'Alpha Sandboxes'

    notifications:   # only for accounts in this OU
      placeholders:
        corporation: 'Alpha SARL'


  - identifier: 'ou-5678'
    note: 'Gamma Sandboxes'

    notifications:   # only for accounts in this OU
      placeholders:
        corporation: 'Gamma s.p.a.'


```

## Step 6: Inspect notifications <a id="step-6"></a>

Notifications are persisted in a dedicated DynamoDB table. You can use the DynamoDB console to inspect most recent records of the table.

## Step 7: Inspect notifications reports <a id="step-7"></a>

SPA creates one record for each notification that it sends. In addition, SPA updates these records on user confirmations. Notifications are reported at the end of each month for each cost center.

To get and to inspect some notification report for a given cost center:

- From the AWS Console of `Automation`, the AWS account where SPA has been deployed, select the service 'S3'
- Select the reporting S3 bucket that is created with SPA
- Click on prefix `SpaReports`
- Click on `Notifications`
- Click on the selected cost center, e.g., `StormFR`
- Click on the most recent Excel file, e.g., `2023-06-StormFR-notification.csv`
- Click on the 'Download' button to get a copy of the file on your computer
- Open the file with and inspect it

Note that some notifications can be reported multiple times, if their confirmation is happening on the month that follows their sending.
