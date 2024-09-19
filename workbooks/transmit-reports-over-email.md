# Transmit reports over email

## Overview

With this workbook you can forward monthly reports to selected email recipients. This way of working is well-adapted to accounting teams and to FinOps teams, since data is reaching their mailboxes at periodic intervals.

1. [Verify the origin email address in AWS SES](#step-1)
2. [Configure the origin email address in SPA settings](#step-2)
3. [Verify in AWS SES all email addresses of target recipients](#step-3)
4. [Configure in SPA the list of email recipients for reports](#step-4)
5. [Request production usage of AWS SES](#step-5)

## Prerequisites

- You have credentials to create a SES origin email address
- You have access to the settings file of your deployed SPA
- You have AWS credentials to deploy SPA

## Step 1: Verify the origin email address in AWS SES <a id="step-1"></a>

AWS Simple Email Service, or SES, is a managed service that allows the transmission of messages to email recipients. In order to prevent spam and to protect the reputation of AWS email services, you have to pass through multiple steps before you can use an origin email recipient with SPA.

Complete following activities at this step:

- Open the AWS Console of the AWS account and in the AWS region where SPA has been deployed
- Go to the SES Console
- In the left pane, select 'Verified identities'
- Click on the button 'Create identity'
- Select the option 'Email address' for the verification of a single recipient
- Enter the email address that you want to use, e.g., `spa@example.com`
- Click on the button 'Create identity' at the bottom of the form
- Move to your mailbox, find the verification message and click on the link provided by AWS
- A congratulation page is displayed in your web browser on successful verification
- Go back to the SES Console, refresh the page, and ensure that the Identity status is now `Verified`

Learn more:

- [AWS SES: Creating an email address identity](https://docs.aws.amazon.com/ses/latest/dg/creating-identities.html#verify-email-addresses-procedure)

## Step 2: Configure the origin email address in SPA settings <a id="step-2"></a>

This step can be completed with following activities:

- Open the SPA settings file in the editor of your choice
- Look for the keyword `with_origin_email_recipient:` and paste the email address that was verified previously
- Save the SPA settings file and deploy the new configuration with the command `make deploy`

To validate the deployment, you can inspect Lambda functions `SpaOnMonthlyCostsReport` of SPA in the AWS account where SPA has been deployed. The environment variable `ORIGIN_EMAIL_RECIPIENT` should reflect the origin email address used by SES.

## Step 3: Verify in AWS SES all email addresses of target recipients <a id="step-3"></a>

This is similar to activities at step 1, but for each target recipients of reports:

- Open the AWS Console of the AWS account and in the AWS region where SPA has been deployed
- Go to the SES Console
- In the left pane, select 'Verified identities'
- Click on the button 'Create identity'
- Select the option 'Email address' for the verification of a single recipient
- Enter the email recipient that will receive reports, e.g., `alice@example.com`
- Click on the button 'Create identity' at the bottom of the form
- Move to your mailbox, find the verification message and click on the link provided by AWS
- A congratulation page is displayed in your web browser on successful verification
- Go back to the SES Console, refresh the page, and ensure that the Identity status is now `Verified`

## Step 4: Configure in SPA the list of email recipients for reports <a id="step-4"></a>

This step can be completed with following activities:

- Open the SPA settings file in the editor of your choice
- Look for the keyword `with_cost_email_recipients:`
- Add one list item for each target recipient that was verified previously
- Save the SPA settings file and deploy the new configuration with the command `make deploy`

To validate the deployment, you can inspect Lambda functions `SpaOnMonthlyCostsReport` of SPA in the AWS account where SPA has been deployed. The environment variable `COST_EMAIL_RECIPIENTS` should reflect the destination email addresses for reports.

## Step 5: Request production usage of AWS SES <a id="step-5"></a>

Initially AWS SES is limiting the sending of email messages. Such sandboxing is useful for tests, however now you are ready for production:

- Open the AWS Console of the AWS account and in the AWS region where SPA has been deployed
- Go to the SES Console
- In the left pane, select 'Account dashboard'
- If you see a banner like 'Your Amazon SES account is in the sandbox in EU (Ireland)' or similar, then click on the button `Request production access`
- On the next page, enter request details as follows:
- Select the Mail type `Transactional`
- For the Website URL, enter the address of your corporate web site, e.g., https://www.example.com
- In the use case description, you can explain how SPA is leveraging SES. For example: 'With SES we will distribute cost reports to FinOps team and to accountants, once per month.'
- Add your email address in the Additional contacts
- Acknowledge the AWS Service Terms and Acceptable Use Policy (AUP)
- Click on the button 'Submit request'
- Wait for feedback and confirmation from AWS. This can take up to 24 hours.
