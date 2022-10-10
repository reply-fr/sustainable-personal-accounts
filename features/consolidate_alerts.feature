Feature: consolidation of alerts across accounts

As a system administrator,
I consolidite alerts from managed accounts
so as to build an event-driven architecture for the personal accounts that I manage

Scenario: where a billing alert is consolidated
Given a central queue created in AWS account 'Automation' in an AWS Organisation
When a billing alert is triggered on an AWS account into this AWS Organisation
Then the billing alert is forwarded to the central queue
And lambda function 'OnAlert' is executed
And the billing alert is forwarded to the central SNS topic

Scenario: where a CodeBuild failure is consolidated
Given the default event bus of AWS account 'Automation' in an AWS Organisation
When CodeBuild project is executed within assigned account
And CodeBuild project fails or does not succeed
Then the native event generated by 'aws:codebuild' is pushed to the event bus
And lambda function 'OnAlertFromCodebuild' is executed
And the failure message is forwarded to the central SNS topic



