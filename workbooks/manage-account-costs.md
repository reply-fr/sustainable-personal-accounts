# Manage account costs

## Overview

In this workbook we dive deep on cost management for AWS accounts. The objective is to explain automation brought by SPA, so that you can monitor costs at scale, detect abnormal spending, and also contribute to the FinOps processes of your enterprise.

1. [Assign cost budget to every AWS account](#step-1)
2. [Manage budget alerts centrally](#step-2)
3. [Assign a cost center to every AWS account](#step-3)
4. [Automate cost monitoring and reporting](#step-4)
5. [Monitor daily costs with custom CloudWatch metric](#step-5)
6. [Produce reports of account costs](#step-6)
7. [Transmit cost reports over email to FinOps team](#step-7)

## Prerequisites

- You have credentials to access the AWS Console
- You have the permission to access the CloudWatch Console of the `Automation` account (where SPA has been deployed)

## Step 1. Assign cost budget to every AWS account <a id="step-1"></a>

SPA provides an opportunity to set budget thresholds to every account that it manages. You can either define budgets for all accounts in one organizational unit (OU), or for an individual account. You can also set a default budget when this is not specified elsewhere.

The excerpt below illustrates how a budget is set for accounts in one OU in the settings file:

```yaml
# these are organizational units where accounts are managed by the solution
organizational_units:

  # settings specific to accounts placed in this organizational unit
  - identifier: 'ou-5678'
    note: 'some container of accounts'

    preparation: # of managed accounts

      # processing is skipped if not enabled explicitly - 'enabled' or 'disabled'
      feature: enabled

      # passed to Codebuild project for the preparation of an account
      variables:
        ALERT_THRESHOLD: 90 # percentage of budget
        BUDGET_AMOUNT: 300 # USD
        BUDGET_NAME: DevelopmentTeamBudget
```

In this example, each AWS account put in the OU `ou-5678` will have a budget alert named `DevelopmentTeamBudget` with a maximum budget of 300 USD and an alert threshold of 90%. In other terms, if actual costs on these account go beyond 270 USD, a budget alert will be raised.

Note that we describe here standard behavior of SPA, powered by the default buildspec provided for account preparation. You can develop your own buildspec file, and define a specific set of environment variables to be passed to CodeBuild projects.

## Step 2. Manage budget alerts centrally <a id="step-2"></a>

When a budget alert is raised by AWS, a message is sent automatically to the email address of the account. Therefore, when you use personal mail addresses for sandbox accounts managed by SPA, the account owners receive mail alerts right into their own mailboxes. By enforcing ownership of account holders, SPA facilitates their rapid reaction such as the deletion of unused resources, etc.

In addition, SPA manages budget alerts centrally, with following options:

- creation of incident records in AWS Incident Manager
- publish alerts to subscribers of a SNS topic
- push notifications to Microsoft Teams webhook

SPA consolidates budget alerts on the `Automation` account. One incident record is created in AWS Incident Manager for each budget alert. A cost report is attached automatically to each incident record for easier analysis of on-going costs. In other terms, SPA handles budget alerts with principles that were developed for professional management of corporate incidents.

The settings excerpt below illustrates how SPA can forward alerts to selected email recipients:

```yaml
features:  # that can be activated optionally

  # these e-mail addresses receive messages on alerts, e.g., billing alerts, CodeBuild failures, etc.
  # - allowed values: a list of valid e-mail addresses
  # - default value: empty list
  #
  with_email_subscriptions_on_alerts:
  - alice@example.com
  - bob@example.com
  ```

In this example, Alice and Bob will receive messages from Amazon to confirm their subscription after the deployment or update of SPA. After that, each of them will receive a copy of each budget alert.

SPA creates a SNS topic to forward budget alerts. The addition of alert subscribers is managed by the modification of settings:

- Open the settings file of SPA, e.g., `settings.yaml`, with you preferred text editor
- In the section `features`, set the parameter `with_email_subscriptions_on_alerts` to the list of email recipients
- Save and close the settings file
- Use the command `make deploy` to update the SPA stack on AWS

The [setup of a Microsoft Teams webhook](./add-microsoft-teams-webhook.md) is described in a separate workbook.

## Step 3. Assign a cost center to every AWS account <a id="step-3"></a>

SPA can tag AWS accounts that it manages. The settings excerpt below shows how to set cost center and cost owner to each account of organizational units:

```yaml
# these are organizational units where accounts are managed by the solution
organizational_units:

  # settings specific to accounts placed in this organizational unit
  - identifier: 'ou-1234'
    note: 'Alpha Sandboxes'

    # added to every account
    account_tags:
      cost-center: 'Alpha'
      cost-owner: foo.bar@example.com

  # settings specific to accounts placed in this organizational unit
  - identifier: 'ou-5678'
    note: 'Gamma Sandboxes'

    # added to every account
    account_tags:
      cost-center: 'Gamma'
      cost-owner: jones@example.com
  ```

Here we define one organizational unit for the business unit Alpha, and another one for the business unit Gamma. AWS accounts for collaborators of these business units are placed in respective business units. SPA tags all accounts of the Alpha business unit with the tag `cost-center` and the value `Alpha`. Similarly, accounts of the Gamma business units are tagged with `cost-center` and the value `Gamma`. This setup can accommodate hundreds of sandbox accounts spread over organizational units.

The addition of tags related to cost management is managed by the modification of settings:

- Open the settings file of SPA, e.g., `settings.yaml`, with you preferred text editor
- In the section `organizational_units`, set tags for each OU managed collectively by SPA
- In the section `accounts`, set tags for each OU managed individually by SPA
- In the section `default`, set tags to be positioned if not specified elsewhere
- Save and close the settings file
- Use the command `make deploy` to update the SPA stack on AWS

## Step 4. Automate cost monitoring and reporting <a id="step-4"></a>

By default, SPA does not monitor account costs in the CloudWatch dashboard, and it does not report on costs every month. These have to be enabled explicitly if you want to benefit of automated cost management at account level.

The monitoring and the reporting on costs is activated by specifying the cost center tag as follows:

- Open the settings file of SPA, e.g., `settings.yaml`, with you preferred text editor
- In the section `features`, set the parameter `with_cost_management_tag` to the tag used for cost center, e.g., `cost-center`
- Save and close the settings file
- Use the command `make deploy` to update the SPA stack on AWS

An example of automation of the settings file:

```yaml
# additional features that can be activated optionnally
features:

  # this is the tag key that is used across settings for cost management
  # automated processing of costs is deployed only if this is set to a valid string
  # - allowed value: key of the tag that is used for cost management, e.g., 'cost-center'
  # - default value: no value
  #
  with_cost_management_tag: cost-center

```

## Step 5. Monitor daily costs with custom CloudWatch metric <a id="step-5"></a>

When the settings file features a cost management tag, a new widget appears in the CloudWatch dashboard of SPA, that displays costs of previous day for each cost center. The computation of daily costs is done automatically during the night, and persisted as a CloudWatch custom metric.

Since SPA produces CloudWatch metrics, you can add your own custom alarms if you wish, for one cost center or for a combination of them.

## Step 6. Produce reports of account costs <a id="step-6"></a>

When the settings file mentions a cost management tag, SPA can query Cost Explorer and produce reports on a monthly basis. SPA checks tags attached to each AWS account to sum costs per cost center.

Following reports are produced every month to support comprehensive FinOps requirements:

- A Excel report for each cost center, that lists accounts and their consumption, and that can be checked by the owner of a cost center
- CSV reports for each cost center, for easy integration in data processing chains
- A summary Excel report, that lists accounts and cost types, and that can be checked by central FinOps team
- A summary CSV report with similar information, for easy integration in data processing chains

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

SPA can also produce summary report with additional currencies than USD. The excerpt below shows such settings:

```yaml
features:  # that can be activated optionally

  # monthly reports are produced for each of these currencies
  # - allowed value: a list of valid currencies, e.g., 'EUR', 'GBP', etc.
  # - default value: no value
  #
  with_cost_extra_currencies: ['EUR']

```

In this example, SPA produces each month one summary report in USD and another one in EUR.

## Step 7. Transmit cost reports over email to FinOps team <a id="step-7"></a>

SPA can use AWS SES to push summary files out of S3 bucket. Look at [Transmit reports over email](./transmit-reports-over-email.md) for more information.
