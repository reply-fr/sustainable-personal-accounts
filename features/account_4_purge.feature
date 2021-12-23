Feature: purge of individual cloud accounts
As cloud practice owner,
I purge as many resources as possible from each individual cloud account
so as to enforce software engineering best practices
-- use case: cut costs of unused resources
-- use case: enforce everything-as-code over configuration a the console

Scenario: where authenticated employee is prevented to create resources in expired account
Given an individual cloud account in OU 'Expired Accounts'
When employee assigned to the account signs in using SSO
Then he can not create new resources
-- implementation: SCP of OU Expired Accounts

Scenario: where expired account is mentioned on event bus
When an account lands in OU 'Expired Accounts'
Then lambda function 'SignalExpiredAccount' is executed
And an event 'ExpiredAccount' is emitted on event bus for one account

Scenario: where expired account is purged by SSM runbook
When an event 'ExpiredAccount' has been emitted on event bus for one account
Then runbook 'PurgeAccount' is executed
And an event 'PurgedAccount' is emitted on event bus for one account
-- implementation: event rule and ssm automation running aws-nuke
-- ssm automation allow for customization of the runbook itself
-- limit: those of ssm automation
-- implementation: workers running aws-nuke behind a SQS queue
-- credit: https://www.1strategy.com/blog/2019/07/16/automated-clean-up-with-aws-nuke-in-multiple-accounts/
-- how to protect resources created by Control Tower?
-- Enhance CloudFormation Stacksets with default tagging in AWS config
-- For tag conformity, use tag policy at organization level
-- credit: https://controltower.aws-management.tools/ops/tag/

Scenario: where purged account is moved to next state
When an event 'PurgedAccount' is emitted on event bus for one account
Then lambda function 'MoveExpiredAccount' is executed
And account is moved from OU 'Expired Accounts' to OU 'Assigned Accounts'
-- a possible extension would be to check if the person is still eligigle for a personal account
