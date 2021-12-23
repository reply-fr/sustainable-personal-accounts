Feature: preparation of an individual cloud account
As a compliance manager,
I adjust resources in each individual cloud account
so as to enforce corporate policies
-- requirement: enforce security policies in individual cloud accounts
-- requirement: enforce configuration rules in individual cloud accounts
-- requirement: enforce observability policies in individual cloud accounts
-- requirement: enforce cost management policies in individual cloud accounts

Scenario: where assigned account is mentioned on event bus
When an account lands in OU 'Assigned Accounts'
Then lambda function 'SignalAssignedAccount' is executed
And an event 'AssignedAccount' is emitted on event bus for one account

Scenario: where assigned account is processed by SSM runbook
When an event 'AssignedAccount' has been emitted on event bus for one account
Then runbook 'PrepareAccount' is executed
And an event 'PreparedAccount' is emitted on event bus for one account
-- implementation: event rule and ssm automation
-- ssm automation allow for customization of the runbook itself
-- limit: those of ssm automation

Scenario: where assigned account is moved to next state
When an event 'PreparedAccount' has been emitted on event bus for one account
Then lambda function 'MoveAssignedAccount' is executed
And account is moved from OU 'Assigned Accounts' to OU 'Released Accounts'
-- event is emitted for observability and for system extension
