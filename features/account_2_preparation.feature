Feature: preparation of an individual cloud account
As a compliance manager,
I adjust resources in each individual cloud account
so as to enforce corporate policies
-- requirement: enforce security policies in individual cloud accounts
-- requirement: enforce configuration rules in individual cloud accounts
-- requirement: enforce observability policies in individual cloud accounts
-- requirement: enforce cost management policies in individual cloud accounts

Scenario: where assigned account is processed to next state
Given an OU 'Released Accounts'
When an account lands in OU 'Assigned Accounts'
Then runbook 'HandleAssignedAccount' is executed
And an event 'AssignedAccount' is emitted on event bus for one account
And the account is configured as per corporate policies
And selected tools are deployed automatically
And account is moved to OU 'Released Accounts'
And an event 'ReleasedAccount' is emitted on event bus for one account
-- implementation: event rule and ssm automation
-- ssm automation allow for customization of the runbook itself
-- event is emitted for observability and for system extension
-- limit: those of ssm automation
