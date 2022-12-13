# Full setup of Sustainable Personal Accounts (SPA)

## Overview
This workbook is for the entire setup of Sustainable Personal Accounts (SPA) on one AWS account of a target AWS Organization.

## Pre-conditions
- You have credentials to access the AWS Console for the top-level account of the target AWS Organization.
- You have needed permissions to manage Control Tower and Account Factory
- Under Windows WSL, you may have to install python3-venv, gcc, rustc, libffi-dev
- Packages installed on your workstation include: make, python

## Step 1 - Deploy AWS Control Tower

The sweet spot for Sustainable Personal Account is an AWS Organization deployed as part of AWS Control Tower.

Reference:
- [AWS Control Tower Workshops](https://controltower.aws-management.tools/)
- [AWS Control Tower Documentation](https://docs.aws.amazon.com/controltower/)

## Step 2 - Ensure that all organizational events are collected in CloudTrail

SPA is using events related to multiple AWS accounts. The collection and aggregation of these events can be done by CloudTrail, but this needs explicit activation.

This step can be completed with following activities:
- From the AWS Console of the top-level account of the AWS Organization, select Control Tower service
- In the left pane, click on `Landing zone settings`
- Click on button `Modify settings`
- This will lead you to a 3-step assistant
- Pass the first step by clicking on the button `Next` at the very bottom right
- On second step, that is referring to `AWS CloudTrail Configuration`, check the `Enabled` radio button
- Click on the button `Next` at the very bottom right
- On third step, review the overall configuration. Ensure that Organisational-level logging has been enabled then click on button `Update landing zone`

## Step 3 - Select an AWS account and a region to deploy Sustainable Personal Account

We do not want to execute code in the top-level account of the AWS Organization. In case of error the blast radius could just kill our entire business. Also the two accounts in the Security organisational units should be limited to read-only and reporting operations. We want to not intermix regular business operations and security operations, but isolate these two as different streams. As a result, out of all shared accounts created by Control Tower, the `Sandbox` account seems a good candidate to automate business operations with tools such as SPA.

We recommend to rename the `Sandbox` account created by Control Tower to `Automation`. This is living in the Sandbox Organizational Unit. Alternatively, you can create a new account for automated background activities in your organisation, for example with the Account Factory created by Control Tower.

Take a note of the `Automation` account identifier, a string of 12 digits. This will be used in the next step to create a trusted relationship with the top-level account of the AWS Organization.

## Step 4 - Create a role for SPA automation

SPA is using a limited set of AWS features related to AWS Organization, such as: list OU, list accounts in OU, tag an AWS account, and so on. From the top-level account of your AWS Organisation, visit the IAM Console and create a role that can be assumed from the `Automation` account. Take a note of the ARN of the role that you create, since you will enter it into the settings file used by SPA.

Here is the full sequence of activities for this step:
- From the AWS Console of the top-level account of the AWS Organization, select IAM service
- In the left pane, click on `Roles`
- Click on button `Create role`
- For a trusted entity type, check `AWS Account`
- Select `Another AWS account` and paste the 12 digits of the `Automation` account identifier
- Let options cleared
- Select the managed permission policy `AWSOrganizationsFullAccess`
- Click on button `Next`
- On the following page, enter a role name such as `SpaAssumedRole` and a description, for example: "This role is assumed by SPA from the Automation account"
- Click on button `Create role`
- Search for roles starting with "Spa" and visit the page for the role that you have created
- Take note of the ARN role, a string similar to that: `arn:aws:iam::123456789012:role/SpaAssumedRole`

## Step 5 - Receive all events on Automation account

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
- Insert a statement, using the event bus ARN and the Organization ID, similar to the following one:

```
{
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
  ```

- Ensure that the mention JSON is valid appears before you hit the button `Update` at the bottom of the form. In case of error, ensure that statements are separated by commas.

After the update you can control that the resource-based policy for the default event bus is looking like the following:

```
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

## Step 6 - Forward organizational events to the Automation account

Events related to AWS accounts are posted on the default bus of the top-level account of the AWS Organization. In addition, these events are generated in the region `us-east-1`, and not in the region of your choice. Therefore, we create an Eventbridge rule in the top-level account and in the `us-east-1` region to forward events to the default bus in the `Automation` account and in the region where you will deploy SPA.

Following activities are related to this step:
- From the AWS Console of the `Automation` account, select Amazon EventBridge service
- In the left pane, click on `Event buses`
- Take note of the `default` event bus ARN, something like `arn:aws:events:eu-west-1:123456789012:event-bus/default`
- From the AWS Console of the top-level account, select Amazon EventBridge service
- At the top of the AWS Console, select the region `us-east-1`
- In the left pane, click on `Rules`
- Click on the `Create rule` button
- Provide an explicit name such as `forward-organizational-events`
- Provide an explicit description, e.g., `Detect the creation a,nd modification of AWS accounts`
- Ensure that the `default` bus has been selected
- Select the radio button `Rule with an event pattern`
- Click on the button `Next`
- Select the event source as radio button `AWS events or EventBridge partner events`
- Skip the Sample event section
- For the event pattern, select event source `AWS services`, `Organizations`, `All events`
- The event pattern displayed on the right is looking like this:

```
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
- Add a neww tag, e.g., key `domain` and value `SustainablePersonalAccount`
- Click on the button `Next`
- Review the setup then click on button `Create rule`


## Step 7 - Create Organizational Units for personal accounts

We recommend to create several OUs under the Sandbox Organizational Unit. Each OU can feature specific SCP and specific settings in SPA. In other terms, SPA is aligning with the structure of OU to provide differentiated behaviour on AWS accounts that they contain. Take a note of OU identifiers that you create, since you will enter them into the settings file used by SPA.

## Step 8 - Clone the SPA repository on your workstation

```
$ git clone git@github.com:reply-fr/sustainable-personal-accounts.git
$ cd sustainable-personal-accounts
$ make setup
```

## Step 9 - Configure SPA

You can duplicate the file `fixtures/settings/settings.yaml` to `settings.yaml` and reflect parameters for your own deployment. You should mention under key `role_arn_to_manage_accounts` the ARN of the role created in top-level account for SPA. You should also have one entry under `organisational_units` for every OU that SPA is looking after.

## Step 10 - Deploy SPA

One you have authenticated to AWS, maybe with AWS SSO, and have appropriate AWS credentials set on your workstation, you can deploy SPA:

```
$ make shell
$ make deploy
```

## Step 11 - Inspect the solution

Use the AWS Console on the `Automation` account. There is a CloudWatch dashboard that reflects metrics for SPA. Code execution is reflected into the Lambda console.

## Post-conditions

- You can now [create new AWS accounts](./create-a-personal-account.md) and let SPA manage them automatically
- You can [forward consolidated alerts to Microsoft Teams](./add-microsoft-teams-webhook.md) and look for collective efficiency of your entire team
