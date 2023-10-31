# Add a Microsoft Teams webhook

## Overview

With this workbook you can forward consolidated alerts to a Microsoft Teams channel. This setup is aligned with ChatOps principles, where information originating from the platform is driven to discussion channels for human beings. With a central team of administrators, it fosters collective efficiency and prevents blind spots that can come with individual e-mail notifications. And when the chat channel is shared across users of SPA, it closes the feedback loop when a billing alert is raised.

1. [Understand Microsoft Teams Incoming Webhooks](#step-1)
2. [Create a Microsoft Teams Incoming Webhook](#step-2)
3. [Configure the webhook in SPA](#step-3)

## Prerequisites

- You have credentials to create a webhook to Microsoft Teams
- You have access to the settings file of your deployed SPA
- You have AWS credentials to deploy SPA

## Step 1. Understand Microsoft Teams Incoming Webhooks <a id="step-1"></a>

![ChatOps architecture](./medias/chatops_integration.drawio.svg)

An Incoming Webhook lets external applications to share content in Microsoft Teams channels. The webhooks are used as tools to track and notify. The webhooks provide a unique URL, to send a JSON payload with a message in card format. Cards are user interface containers that include content and actions related to a single article. You can use cards in the following capabilities:

- Bots
- Message extensions
- Connectors

SPA is consolidating alerts emitted by accounts that it manages, such as billing alerts and failures of CodeBuild projects. With Microsoft Teams Incoming Webhooks, such alerts can be automatically forwarded to one specific channel. All people connected to this channel will receive information simultaneously, and can react through the channel itself.

## Step 2. Create a Microsoft Teams Incoming Webhook <a id="step-2"></a>

Following activities take place from within Microsoft Teams itself:

- Open the channel in which you want to add the webhook and select ••• from the top navigation bar.
- Select Connectors from the dropdown menu.
- Search for Incoming Webhook and select Add.
- Select Configure, provide a name, and upload an image for your webhook if necessary.
- Copy and save the unique webhook URL present in the dialog window. The URL maps to the channel and you will use it in SPA settings file. Select Done.

At the end of this step, the webhook is available in the Teams channel, and you have a web link to configure SPA.

Credit:

- (Microsoft official documentation) [Create Incoming Webhooks](https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook)

## Step 3. Configure the webhook in SPA <a id="step-3"></a>

For this step you need to do the following:

- Open the SPA settings file in the editor of your choice
- Look for the keyword `with_microsoft_webhook_on_alerts:` and paste the webhook URL copied from previous step.
- Save the SPA settings file and deploy the new configuration with the command `make deploy`

To validate the deployment, you can inspect Lambda functions of SPA in the AWS account where SPA has been deployed. The environment variable `MICROSOFT_WEBHOOK_ON_ALERTS` should reflect the webhook URL across all Lambda functions.

## Follow-up

When a billing threshold is reached, an alert is consolidated by SPA and reflected in Microsoft Teams.