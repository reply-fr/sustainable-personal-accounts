# Full setup of Sustainable Personal Accounts (SPA)

## Overview
This workbook is for the entire setup of Sustainable Personal Accounts (SPA) on one AWS account of a target AWS Organization.

## Pre-conditions
- You have credentials to access the AWS Console for the Master Account of the target AWS Organization.
- You have needed permissions to manage Control Tower and Account Factory
- Under Windows WSL, you may have to install python3-venv, gcc, rustc, libffi-dev
- Packages installed on your workstation include: make, python

## Step 1 - Deploy AWS Control Tower

The sweet spot for Sustainable Personal Account is an AWS Organizations deployed as part of Control Tower.

Reference:
- [AWS Control Tower Workshops](https://controltower.aws-management.tools/)
- [AWS Control Tower Documentation](https://docs.aws.amazon.com/controltower/)

## Step 2 - Select an AWS account and a region to deploy Sustainable Personal Account

We recommend to rename the "Sandbox" account created by Control Tower to "Automation". This is living in the Sandbox Organizational Unit. Alternatively, you can create a new account for automated background activities in your organisation, for example with the Account Factory created by Control Tower.

Take a note of the Automation account identifier, a string of 12 digits. This will be used in the next step to create a trusted relationship with the Master Account.

## Step 3 - Create a role for SPA automation

SPA is using a limited set of AWS features related to AWS Organization, such as: list OU, list accounts in OU, tag an AWS account, and so on. From the Master Account of your organisation, visit the IAM Console and create a role that can be assumed from the Automation Account. Take a note of the ARN of the role that you create, since you will enter it into the settings file used by SPA.

The full sequence of actions to complete this step:
- From the AWS Console of the Master Account of the target AWS Organization, select IAM service
- On the left pane, click on Roles
- Click on button `Create role`
- For a trusted entity type, check `AWS Account`
- Select "Another AWS account" and paste the 12 digits of the Automation account identifier
- Let options cleared
- Selec the managed permission policy `AWSOrganizationsFullAccess`
- Click on button `Next`
- On the following page, enter a role name such as `SpaAssumedRole` and a description, for example: "This role is assumed by SPA from the Automation account"
- Click on button `Create role`
- Search for roles starting with "Spa" and visit the page for the role that you have created
- Take note of the ARN role, a string similar to that: "arn:aws:iam::123456789012:role/SpaAssumedRole"

## Step 4 - Create Organizational Units for personal accounts

We recommend to create several OUs under the Sandbox Organizational Unit. Each OU can feature specific SCP and specific settings in SPA. In other terms, SPA is aligning with the structure of OU to provide differentiated behaviour on AWS accounts that they contain. Take a note of OU identifiers that you create, since you will enter them into the settings file used by SPA.

## Step 5 - Clone the SPA repository on your workstation

```
$ git clone git@github.com:reply-fr/sustainable-personal-accounts.git
$ cd sustainable-personal-accounts
$ make setup
```

## Step 6 - Configure SPA

You can duplicate the file `fixtures/settings/settings.yaml` to `settings.yaml` and reflect parameters for your own deployment. You should mention under key `role_arn_to_manage_accounts` the ARN of the role created in Master Account for SPA. You should also have one entry under `organisational_units` for every OU that SPA is looking after.

## Step 7 - Deploy SPA

One you have authenticated to AWS, maybe with AWS SSO, and have appropriate AWS credentials set on your workstation, you can deploy SPA with one command:

```
$ make shell
$ make deploy
```

## Step 8 - Inspect the solution

Use the AWS Console on the "Automation" account. There is a CloudWatch dashboard that reflects metrics for SPA. Code execution is reflected into the Lambda console.

## Post-conditions
