Feature: release of individual cloud account

As an employee,
I use the individual cloud account that has been assigned to me
so as to learn, build, test and to innovate with AWS services
# requirement: enablement of individual software engineers, system engineers, data engineers
# use case: personal exploration of cloud services, and code saved in git repositories
# limit: personal accounts are not suited for collective deployments, that are covered by Dev/OAT/Prod environments
# limit: personal accounts are not suited for production data

Scenario: where authenticated employee is entitled to create and delete resources
Given an individual cloud account is tagged with key 'account-state' and value 'released'
When employee assigned to the account signs in using SSO
Then cloud resources can be created, modified and deleted
# SCP allow for resource creation and deletion, except for some operations

Scenario: where accounts are expired on maintenance window
Given a scheduled maintenance window
When maintenance window is reached
Then lambda function 'OnMaintenanceWindow' is executed
And code scans the accounts of all configured organizational units
And code tags each released account with key 'account-state' and value 'expired'
# use case: hundreds of accounts are purged on Friday evening after 20:00 CET
# limit: there is a need to limit maximum events/second on bus
