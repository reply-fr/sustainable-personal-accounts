Feature: purge of individual cloud accounts
As cloud practice owner,
I purge as many resources as possible from each individual cloud account
so as to enforce software engineering best practices
# use case: cut costs of unused resources
# use case: enforce everything-as-code over configuration a the console

Scenario: where authenticated employee is prevented to create resources in expired account
Given an individual cloud account is tagged with key 'account:state' and value 'expired'
When employee assigned to the account signs in using SSO
Then he can not create new resources
# implementation: SCP

Scenario: where expired account is reported and handled
When account tag of key 'account:state' is changed to value 'expired'
Then lambda function 'SignalExpiredAccount' is executed
And lambda function emits an event 'ExpiredAccount' on event bus
And lambda function creates codebuild project 'PurgeAccount' within assigned account
And lambda function starts codebuild project 'PurgeAccount' asynchronously
# implementation: lambda execution role permits creation of codebuild projects
# implementation: boto3.client('codebuild').start_build() with inline buildspec

Scenario: where expired account is purged
When codebuild project 'PurgeAccount' is executed within assigned account
Then codebuild project emits an event 'PurgedAccount' on event bus when job has been completed
# implementation: execute aws-nuke within the provided buildspec
# credit: https://www.1strategy.com/blog/2019/07/16/automated-clean-up-with-aws-nuke-in-multiple-accounts/
# implementation: 'aws events put-events ...' at the end of the provided buildspec

Scenario: where purged account is moved to next state
When an event 'PurgedAccount' has been emitted on event bus
Then lambda function 'MoveExpiredAccount' is executed
And account tag of key 'account:state' is changed to value 'assigned'
# a possible extension would be to check if the person is still eligigle for a personal account
