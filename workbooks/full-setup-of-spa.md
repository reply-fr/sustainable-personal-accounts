# Full setup of Sustainable Personal Accounts (SPA)

## Overview

This workbook is for the entire setup of Sustainable Personal Accounts (SPA) on one AWS account of a target AWS Organization.

1. [Create or use an AWS Organization](#step-1)
2. [Ensure that all organizational events are collected in CloudTrail](#step-2)
3. [Select an AWS account and a region to deploy Sustainable Personal Account](#step-3)
4. [Create a role for SPA automation](#step-4)
5. [Receive events on Automation account](#step-5)
6. [Forward organization events to the Automation account](#step-6)
7. [Forward console logins to the Automation account](#step-7)
8. [Activate AWS Incident Manager](#step-8)
9. [Create Organizational Units for personal accounts](#step-9)
10. [Clone the SPA repository on your workstation and configure the software](#step-10)
11. [Deploy SPA](#step-11)
12. [Inspect the solution](#step-12)

## Prerequisites

- You have credentials to access the AWS Console
- You have received permissions to create a new AWS account
- You have a computer to run shell commands, `make` commands, Node.js and python code (>= 3.8)
- If you need a convenient place to work, then consider a [Cloud9](https://aws.amazon.com/pm/cloud9/) environment in the AWS account where SPA is deployed
- If you are on Windows, take the time for a full setup of [WSL](https://learn.microsoft.com/en-us/windows/wsl/install) from Microsoft, or use a [Cloud9](https://aws.amazon.com/pm/cloud9/) environment on AWS

## Step 1: Create or use an AWS Organization <a id="step-1"></a>

SPA is leveraging AWS Organization for events management and for account management across AWS accounts.

If you do not have an AWS Organizations yet, then you have to create one. There are multiple options to consider and you have to select the one that will work best for you:

- The deployment of AWS Organizations can be managed by AWS Control Tower, and this is our recommended approach if you start from a single account.
- You can use an alternative account management solution from some AWS Partner
- You deploy a new AWS Organizations by yourself

Reference:

- [AWS Control Tower Workshops](https://controltower.aws-management.tools/)
- [AWS Control Tower Documentation](https://docs.aws.amazon.com/controltower/)

## Step 2: Ensure that all organizational events are collected in CloudTrail <a id="step-2"></a>

SPA is using events related to multiple AWS accounts. The collection and aggregation of these events can be done by CloudTrail, but this needs explicit activation.

When you have deployed Control Tower, this step can be completed with following activities:

- From the AWS Console of the top-level account of the AWS Organization, select Control Tower service
- In the left pane, click on `Landing zone settings`
- Click on button `Modify settings`
- This will lead you to a 3-step assistant
- Pass the first step by clicking on the button `Next` at the very bottom right
- On second step, that is referring to `AWS CloudTrail Configuration`, check the `Enabled` radio button
- Click on the button `Next` at the very bottom right
- On third step, review the overall configuration. Ensure that Organisational-level logging has been enabled then click on button `Update landing zone`

If you do not have Control Tower, then configure your landing zone to generate EventBridge events related to AWS Organizations.

## Step 3: Select an AWS account and a region to deploy Sustainable Personal Account <a id="step-3"></a>

We do not want to execute code in the top-level account of the AWS Organization. In case of error the blast radius could just kill our entire business. Also the two accounts in the Security organizational units should be limited to read-only and reporting operations. We want to not intermix regular business operations and security operations, but isolate these two as different streams.

We recommend to create an AWS account named `Automation` to host SPA code. This should be considered production level, and put in the appropriate Organizational Unit.

Take a note of the `Automation` account identifier, a string of 12 digits. This will be used in the next step to create a trusted relationship with the top-level account of the AWS Organization.

## Step 4: Create a role for SPA automation <a id="step-4"></a>

SPA is using a limited set of AWS features related to AWS Organization, such as: list OU, list accounts in OU, tag an AWS account, and so on. SPA can also make good use of AWS Cost Explorer to compute costs based on account tags. And to act on managed accounts, SPA needs to assume a role on these accounts.

From the top-level account of your AWS Organization, visit the IAM Console and create a role that can be assumed from the `Automation` account. Take a note of the ARN of the role that you create, since you will enter it into the settings file used by SPA.

Here is the full sequence of activities for this step:

- From the AWS Console of the top-level account of the AWS Organization, select IAM service
- In the left pane, click on `Policies`
- Click on button `Create policy`
- in the JSON tab, paste the content below. You can also find it in the file `fixtures/policies/allow_account_automation.json` of the SPA repository:

```json
{
   "Version":"2012-10-17",
   "Statement":[
      {
         "Sid": "AllowToNavigateTheOrganizationAndToTagAccounts",
         "Effect":"Allow",
         "Action":[
            "organizations:AttachPolicy",
            "organizations:CreatePolicy",
            "organizations:Describe*",
            "organizations:DetachPolicy",
            "organizations:List*",
            "organizations:TagResource",
            "organizations:UntagResource",
            "organizations:UpdatePolicy"
         ],
         "Resource":"*"
      },
      {
         "Sid": "AllowToDescribeAccounts",
         "Effect": "Allow",
         "Action": [
            "account:PutAlternateContact",
            "account:DeleteAlternateContact",
            "account:GetAlternateContact",
            "account:GetContactInformation",
            "account:PutContactInformation",
            "account:ListRegions",
            "account:EnableRegion",
            "account:DisableRegion"
         ],
         "Resource": "*"
      },
      {
         "Sid": "AllowToAssumeRole",
         "Effect":"Allow",
         "Action":[
            "sts:AssumeRole"
         ],
         "Resource":"*"
      },
      {
         "Sid": "AllowToAccessCostInformation",
         "Effect": "Allow",
         "Action": [
            "account:GetAccountInformation",
            "billing:GetBillingData",
            "billing:GetBillingDetails",
            "billing:GetBillingNotifications",
            "billing:GetBillingPreferences",
            "billing:GetContractInformation",
            "billing:GetCredits",
            "billing:GetIAMAccessPreference",
            "billing:GetSellerOfRecord",
            "billing:ListBillingViews",
            "ce:*",
            "consolidatedbilling:GetAccountBillingRole",
            "consolidatedbilling:ListLinkedAccounts",
            "cur:GetClassicReport",
            "cur:GetClassicReportPreferences",
            "cur:ValidateReportDestination",
            "freetier:GetFreeTierAlertPreference",
            "freetier:GetFreeTierUsage",
            "invoicing:GetInvoiceEmailDeliveryPreferences",
            "invoicing:GetInvoicePDF",
            "invoicing:ListInvoiceSummaries",
            "payments:GetPaymentInstrument",
            "payments:GetPaymentStatus",
            "payments:ListPaymentPreferences",
            "tax:GetTaxInheritance",
            "tax:GetTaxRegistrationDocument",
            "tax:ListTaxRegistrations"
         ],
         "Resource": "*"
      }
   ]
}
```

- Adjust these statements to your specific needs and requirements. More specifically, consider the statement `AllowToAssumeRole` and narrow resources that can be assumed, or add a condition using `aws:ResourceOrgPath`
- Click on button `Next: Tags`
- Click on button `Next: Review`
- Give a name to the policy, e.g., `SpaPermissions` and a description, e.g., "Permissions given to SPA Lambdas on top-level account"
- In the left pane, click on `Roles`
- Click on button `Create role`
- For a trusted entity type, check `AWS Account`
- Select `Another AWS account` and paste the 12 digits of the `Automation` account identifier
- Let options cleared
- Click on button `Next`
- On the following page, search for the policy that you have created above and select it
- Click on button `Next`
- On the following page, enter a role name such as `SpaAssumedRole` and a description, for example: "This role is assumed by SPA from the Automation account"
- Click on button `Create role`
- Search for roles starting with "Spa" and visit the page for the role that you have created
- Take note of the ARN role, a string similar to that: `arn:aws:iam::123456789012:role/SpaAssumedRole`

SPA is also assuming a role to act on the accounts that it manages. If you rely on AWS Control Tower then you may want to leverage the role `AWSControlTowerExecutionRole` and there is additional no IAM setup. If you fear the super-power given to SPA across all of your AWS Organization, then you can add a condition that limits the permission to selected Organizational Unit. You can also deploy a specific role via a AWS StackSet to a limited number of accounts and/or Organizational Units. When the setup is not correct, then access denied is reported into the logs of the Lambda functions `OnAssignedAccount` and `OnExpiredAccount`.

## Step 5: Receive events on Automation account <a id="step-5"></a>

Since organizational events are collected by the top-level account of the AWS Organization, we will forward these events to the default bus of the `Automation` account. Actually, we want to make this bus a global resource, accessible from any account. We modify the resource policy of the default bus so that events can be put from any account of the AWS Organization. This is based on Attribute-Based Access Control (ABAC), with a specific IAM condition.

Following activities are related to this step:

- From the AWS Console of the top-level account, select AWS Organizations service
- In the left pane, copy the Organization ID, a string like `o-l7ht176sac`
- Close the tab
- From the AWS Console of the `Automation` account, select Amazon EventBridge service
- On the left pane, click on `Event buses`
- Click on the `default` event bus, the one that will be used by SPA
- Take note of the event bus ARN, something like `arn:aws:events:eu-west-1:123456789012:event-bus/default`
- Click on the button `Manage permissions`
- If there is already a policy, do not copy paste the following, but insert a statement in the policy, using the event bus ARN and the Organization ID, similar to the following one:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
      "Sid": "allow_all_accounts_from_organization_to_put_events",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "events:PutEvents",
      "Resource": "arn:aws:events:eu-west-1:123456789012:event-bus/default",
      "Condition": {
        "StringEquals": {
          "aws:PrincipalOrgID": "o-l7ht176sac"
        }
      }
    }
  ]
}
```

- Ensure that the mention "JSON is valid" appears before you hit the button `Update` at the bottom of the form. In case of error, ensure that statements are separated by commas.

After the update you can control that the resource-based policy for the default event bus is looking like the following:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "allow_all_accounts_from_organization_to_put_events",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "events:PutEvents",
    "Resource": "arn:aws:events:eu-west-1:123456789012:event-bus/default",
    "Condition": {
      "StringEquals": {
        "aws:PrincipalOrgID": "o-l7ht176sac"
      }
    }
  }, {
    "Sid": "allow_account_to_manage_rules_they_created",
    "Effect": "Allow",
    "Principal": {
      "AWS": "arn:aws:iam::123456789012:root"
    },

...
```

## Step 6: Forward organization events to the Automation account <a id="step-6"></a>

Events related to AWS accounts are posted on the default bus of the top-level account of the AWS Organization. In addition, these events are generated in the region `us-east-1`, and not in the region of your choice. Therefore, we create an Eventbridge rule in the top-level account and in the `us-east-1` region to forward events to the default bus in the `Automation` account and in the region where you will deploy SPA.

Following activities are related to this step:

- From the AWS Console of the `Automation` account, select Amazon EventBridge service
- In the left pane, click on `Event buses`
- Take note of the `default` event bus ARN, something like `arn:aws:events:eu-west-1:123456789012:event-bus/default`
- From the AWS Console of the top-level account, select Amazon EventBridge service
- At the top of the AWS Console, select the region `us-east-1`
- In the left pane, click on `Rules`
- Click on the `Create rule` button
- Provide an explicit name such as `ForwardOrganizationalEventsToSustainablePersonalAccounts`
- Provide an explicit description, e.g., `Detect the creation and modification of AWS accounts`
- Ensure that the `default` bus has been selected
- Select the radio button `Rule with an event pattern`
- Click on the button `Next`
- Select the event source as radio button `AWS events or EventBridge partner events`
- Skip the Sample event section
- For the event pattern, select event source `AWS services`, `Organizations`, `All events`
- The event pattern displayed on the right is looking like this:

    ```json
    {
      "source": ["aws.organizations"]
    }
    ```

- Click on the button `Next`
- For a target, select radio button `EventBridge event bus`
- For a target type, select radio button `Event bus in a different account or Region`
- Paste the ARN of the default event bus in the `Automation` that you noted previously, something like `arn:aws:events:eu-west-1:123456789012:event-bus/default`
- Select the radio button `Create a new role for this specific resource`
- Click on the button `Next`
- Add a new tag, e.g., key `domain` and value `SustainablePersonalAccount`
- Click on the button `Next`
- Review the setup then click on button `Create rule`

## Step 7: Forward console logins to the Automation account <a id="step-7"></a>

In some setup of CloudTrail the console logins are emitted on the default bus of the top-level account of the AWS Organization. In addition, these events are generated in the region where IAM Identity Center (previously, SSO) has been deployed. This region can be found from the settings of this service. Therefore the need to create an EventBridge rule in the top-level account and in the SSO region to forward events to the default bus in the `Automation` account and in the region where you will deploy SPA.

Following activities are related to this step:

- From the AWS Console of the top-level account, select IAM Identity Center service
- In the left pane, click on `Settings`
- Look for the deployment region, for example: `eu-west-1`
- Then move to the AWS Console of the `Automation` account, select Amazon EventBridge service
- In the left pane, click on `Event buses`
- Take note of the `default` event bus ARN, something like `arn:aws:events:eu-west-1:123456789012:event-bus/default`
- From the AWS Console of the top-level account, select Amazon EventBridge service
- At the top of the AWS Console, select the region that you identified previously, e.g., `eu-west-1`
- In the left pane, click on `Rules`
- Click on the `Create rule` button
- Provide an explicit name such as `ForwardConsoleLoginsToSustainablePersonalAccounts`
- Provide an explicit description, e.g., `Detect logins to the AWS Console`
- Ensure that the `default` bus has been selected
- Select the radio button `Rule with an event pattern`
- Click on the button `Next`
- Select the event source as radio button `AWS events or EventBridge partner events`
- Skip the Sample event section
- For the event pattern, use following JSON::

    ```json
    {
      "detail": {
        "eventSource": ["signin.amazonaws.com"],
        "eventName": ["ConsoleLogin"]
      }
    }
    ```

- Click on the button `Next`
- For a target, select radio button `EventBridge event bus`
- For a target type, select radio button `Event bus in a different account or Region`
- Paste the ARN of the default event bus in the `Automation` that you noted previously, something like `arn:aws:events:eu-west-1:123456789012:event-bus/default`
- Select the radio button `Create a new role for this specific resource`
- Click on the button `Next`
- Add a neww tag, e.g., key `domain` and value `SustainablePersonalAccount`
- Click on the button `Next`
- Review the setup then click on button `Create rule`

## Step 8: Activate AWS Incident Manager <a id="step-8"></a>

AWS Incident Manager is used by SPA to record budget alerts and other operational exceptions, and to support easy handling of these. This is a great building block for serverless application, that can be integrated into ServiceNow and to Jira if needed.

Before SPA can use it programmatically, you have to enable the usage of the service in the `Automation` account in the AWS region where SPA has been deployed. Go to the page [Getting started with Incident Manager](https://docs.aws.amazon.com/incident-manager/latest/userguide/getting-started.html) and follow instructions.

Note: this step is mandatory, and the deployment of SPA will fail if you do not activate AWS Incident Manager manually.

## Step 9: Create Organizational Units for personal accounts <a id="step-9"></a>

We recommend to create one general `Sandboxes` Organizational Unit, possibly with multiple child Organizational Units. Each OU can feature specific SCP and specific settings in SPA. In other terms, SPA is aligning with the structure of OU to provide differentiated behavior on AWS accounts that they contain. Take a note of OU identifiers that you create, since you will enter them into the settings file used by SPA.

The easiest way to create Organizational Units in the context of Control Tower is to do it directly from within the Control Tower Console. With this way of working, new OU are registered automatically in Control Tower. If you create OU from the AWS Organizations Console, or programmatically, then you have to register new OU in Control Tower anyway.

## Step 10: Clone the SPA repository on your workstation and configure the software <a id="step-10"></a>

Next steps of the setup rely on Linux shell, on `git`, on `make`, on Node.js and on python. If one of these items is missing on your workstation, then please consider to create an [AWS Cloud9](https://aws.amazon.com/pm/cloud9/) environment directly in the account where SPA will be deployed. This is the easiest way to go, and the recommended solution for manual actions on a SPA deployment. If you are on Windows, then setup a full [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install).

With following shell commands you copy SPA on your workstation, and you install software dependencies such as CDK.

```shell
$ git clone https://github.com/reply-fr/sustainable-personal-accounts.git
$ cd sustainable-personal-accounts
$ make setup
```

You can edit the file `settings.yaml` and reflect parameters for your own deployment. You should mention under key `role_arn_to_manage_accounts` the ARN of the role created in top-level account for SPA. You should mention under key `role_name_to_manage_codebuild` the name of the role that SPA will assume to act within each account that it manages. In the context of Control Tower, this can be `AWSControlTowerExecution`. You should also have one entry under `organisational_units` for every OU that SPA is looking after.

Note: if you get an error message related to python `bdist wheel` then ensure that your workstation has a full python environment. For example for Ubuntu and WSL, you may have to add the package `python-dev` to pass the `make setup` command.

## Step 11: Deploy SPA <a id="step-11"></a>

To deploy SPA from your workstation you need permissions to act on the `Automation` account.

If you have created a Cloud9 environment in the `Automation` account then this is done automatically. In other cases, you have to configure [a local profile in `~/.aws/config`](https://docs.aws.amazon.com/cli/latest/userguide/sso-configure-profile-token.html) that provides `AWSAdministratorAccess` permissions to `Automation`. In the example below, the local profile named `automation-sso` is linked with Identity Center. Feel free to use your own name and settings.

```shell
$ export AWS_PROFILE=automation-sso
$ aws sso login
$ aws sts get-caller-identity
```

One you have been authenticated, implicitly (Cloud9) or explicitly (local computer), you can bootstrap CDK (if not done yet). Pass in variable `AWS_REGION` the same region that what you put in `settings.yaml`. Then you can deploy SPA:

```shell
$ make shell
$ export AWS_REGION=<deployment-region>
$ make bootstrap-cdk
$ make deploy
```

Note: the `make shell` command ensures that you are using the local virtual python environment that was created during the setup.

Note: the [bootstrap of CDK](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html) is required if you have not used CDK yet on the target AWS account and region. This is an idempotent command; it can be run multiple times without inconvenience.

## Step 12: Inspect the solution <a id="step-12"></a>

Use the AWS Console on the `Automation` account. There is a CloudWatch dashboard that reflects metrics for SPA. Code execution is reflected into the Lambda console. You can also inspect DynamoDB tables.

Activities to on-board one account manually:

- If you expect an AWS account to be handled by SPA, then you set tag `account-state` to the value `vanilla` from the AWS Organizations console of the top-level account.
- Then move to the AWS Console of the `Automation` account and check the log of the Lambda function `SpaOnAccountEvent`. You should get the full sequence of state changes over a couple of minutes: `CreatedAccount`, `AssignedAccount`, `PreparedAccount` then `ReleasedAccount`.
- After this sequence, you can go to the AWS Console of the personal account and inspect the budget that has been set by SPA. In addition, you can also review the Codebuild project that has been executed by SPA during the preparation phase.

Activities to on-board existing accounts in managed Organizational Units:

- Move to the AWS Console of the `Automation` account
- Select the Lambda service
- Look for the Lambda function `SpaResetAccounts`
- Select the tab `Test`
- Click on the button `Test` to trigger the function and tag all managed accounts with tag `account-state` and value `vanilla`.

To ensure complete observability of SPA operations, visit the CloudWatch dashboard in the `Automation` account. Metrics for Lambda and DynamoDB should reflect your activities on personal accounts.

If you have to go deeper in the inspection of your SPA system, use the [Inspect a production system](./inspect-a-production-system.md) workbook.

## Follow-up

- Copy the `settings.yaml` file to a safe place, on a shared file system, on a S3 bucket or in git.
- [Manage preparation tasks](./manage-preparation-tasks.md) with specific `buildspec` and related code
- You can now [create new AWS accounts](./create-a-personal-account.md) and let SPA manage them automatically
- You can also [on-board existing accounts](./reset-managed-accounts.md) by setting their states to VANILLA
- [Manage and troubleshoot account states](./manage-account-states.md) to fix potential issues with the state machine
- You can [forward consolidated alerts to Microsoft Teams](./add-microsoft-teams-webhook.md) and look for collective efficiency of your entire team
- Add SCP to Organizational Units to [manage preventive controls of personal accounts](./manage-preventive-controls.md)
