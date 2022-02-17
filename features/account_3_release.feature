Feature: release of individual cloud account
As an employee,
I use the individual cloud account that has been assigned to me
so as to learn, build, test and innovate on AWS services
# requirement: enablement of individual software engineers, system engineers, data engineers
# use case: personal exploration of cloud services, and code saved in git repositories
# limit: not suited to collective work, that is covered by Dev/OAT/Prod environment
# limit: no production data

Scenario: where authenticated employee is entitled to create and delete resources
Given an individual cloud account is tagged with key 'account:state' and value 'released'
When employee assigned to the account signs in using SSO
Then he can create new resources
And he can delete existing resources
# SCP allow for resource creation and deletion, except for some operations

Scenario: where released accounts are expired
When expiration time is reached
Then lambda function 'ExpireReleasedAccounts' is executed
And account tag of key 'account:state' is changed to value 'expired'
# use case: hundreds of accounts are purged on Friday evening after 20:00 CET
# limit: there is a need to limit maximum events/second on bus
