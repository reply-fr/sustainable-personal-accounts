Feature: creation of an individual cloud account
As an employee,
I request an individual cloud account
so as to learn, build, test and innovate on AWS services
# requirement: enablement of individual software engineers, system engineers, data engineers
# use case: personal exploration of cloud services, and code saved in git repositories
# limit: not suited to collective deployments, that is covered by Dev/OAT/Prod environments
# limit: no production data

Scenario: where an employee is asking for an individual cloud account
Given an employee
When there is a need for being enabled on cloud platform
Then the employee can request an individual cloud account

Scenario: where a new individual cloud account is created and assigned
Given a cloud environment managed with Control Tower
And an individual cloud account has been requested by an employee
When a new individual cloud account is created from the Account Factory
And the account is assigned the corporate e-mail address of the requesting employee
And the account is tagged with key 'account:holder' and value is the e-mail address of requesting employee
Then the account is tagged with key 'account:state' and value 'vanilla'

Scenario: where only one single account can be created for one e-mail address
Given an individual cloud account has been requested by an employee
And an individual cloud account already exists for the e-mail address of this employee
When a new individual cloud account is created
Then an error is generated because an account with the same e-mail address already exists

Scenario: where authenticated employee is prevented to handle resources in available account
Given an individual cloud account is tagged with key 'account:state' and value 'vanilla'
When employee assigned to the account signs in using SSO
Then he can not create new resources
And he cannot delete existing resources
# implementation: SCP of OU where accounts have been placed

Scenario: where vanilla account is moved to next state
When lambda function 'MoveVanillaAccount' is executed
Then lambda function emits an event 'CreatedAccount' on event bus
And account tag of key 'account:state' is changed to value 'assigned'
# implementation: event rule and lambda execution
# event is emitted for observability and for system extension
# limit: up to hundreds of accounts per second
