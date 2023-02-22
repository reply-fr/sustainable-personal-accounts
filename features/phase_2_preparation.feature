Feature: preparation of an individual cloud account

As a compliance manager,
I adjust resources in each individual cloud account
so as to enforce corporate policies
# requirement: enforce security policies in individual cloud accounts
# requirement: enforce configuration rules in individual cloud accounts
# requirement: enforce observability policies in individual cloud accounts
# requirement: enforce cost management policies in individual cloud accounts

Scenario: where account assignment is detected and processed
Given a central event bus
And a central queue for budget alerts
And a buildspec configuration for the preparation of accounts
When the account is tagged with key 'account-state' and value 'assigned'
Then lambda function 'OnAssignedAccount' is executed
And code emits an event 'AssignedAccount'
And code creates SNS topic in target account
And code subscribes central queue to SNS topic
And code forwards codebuild events to central event bus
And code creates codebuild project 'PrepareAccount' in target account
And code starts codebuild project 'PrepareAccount' asynchronously

Scenario: where account has been prepared
Given a central event bus
And codebuild events are forwarded to central event bus
And SCP policies have been configured for released accounts in hosting organizational unit
When codebuild project 'PrepareAccount' is completed or has failed
Then lambda function 'OnPreparedAccount' is executed
And code tags account with key 'account-state' and value 'released'
And code attachs SCP policies configured for released accounts of the hosting organizational unit
And code emits an event 'ReleasedAccount'
# event is emitted for observability and for system extension
