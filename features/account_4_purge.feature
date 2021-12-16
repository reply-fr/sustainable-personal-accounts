Feature: purge of individual cloud accounts
As cloud practice owner,
I purge as many resources as possible from each individual cloud account
so as to enforce software engineering best practices
-- use case: cut costs of unused resources
-- use case: enforce everything-as-code over configuration a the console

Scenario: where expired accounts are purged
Given a queue ExpiredAccounts
And an OU Expired Accounts
When account identifiers can be fetched from the queue ExpiredAccounts
Then an event 'ExpiredAccount' is emitted on event bus for one account
And the account is moved to OU Expired Accounts
And SSM runbook 'PurgeAccount' is launched
And the account is purged from cloud resources
And an event 'PurgedAccount' is emitted on event bus for one account
-- implementation: workers running aws-nuke behind a SQS queue
-- credit: https://www.1strategy.com/blog/2019/07/16/automated-clean-up-with-aws-nuke-in-multiple-accounts/
-- how to protect resources created by Control Tower?

Scenario: where purged account is moved to next state
Given an OU Assigned Accounts
When an event 'PurgedAccount' is emitted on event bus for one account
Then lambda function 'HandlePurgedAccount' is executed
And account is moved to OU Assigned Accounts
-- a possible extension would be to check if the person is still eligigle for a personal account

Scenario: where authenticated employee is prevented to create resources in expired account
Given an individual cloud account in OU Expired Accounts
When employee assigned to the account signs in using SSO
Then he can not create new resources
-- implementation: SCP of OU Expired Accounts
