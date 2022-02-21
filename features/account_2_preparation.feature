Feature: preparation of an individual cloud account
As a compliance manager,
I adjust resources in each individual cloud account
so as to enforce corporate policies
# requirement: enforce security policies in individual cloud accounts
# requirement: enforce configuration rules in individual cloud accounts
# requirement: enforce observability policies in individual cloud accounts
# requirement: enforce cost management policies in individual cloud accounts

Scenario: where assigned account is reported and handled
When account tag of key 'account:state' is changed to value 'assigned'
Then lambda function 'SignalAssignedAccount' is executed
And lambda function emits event 'AssignedAccount' on event bus
And lambda function creates codebuild project 'PrepareAccount' within assigned account
And lambda function starts codebuild project 'PrepareAccount' asynchronously
# implementation: lambda execution role permits creation of codebuild projects
# implementation: boto3.client('codebuild').start_build() with inline buildspec

Scenario: where assigned account is prepared
When codebuild project 'PrepareAccount' is executed within assigned account
Then codebuild project emits an event 'PreparedAccount' on event bus when job has been completed
# implementation: 'aws events put-events ...' at the end of the provided buildspec

Scenario: where assigned account is moved to next state
When an event 'PreparedAccount' has been emitted on event bus
Then lambda function 'MoveAssignedAccount' is executed
And lambda function emits an event 'ReleasedAccount' on event bus
And account tag of key 'account:state' is changed to value 'released'
# event is emitted for observability and for system extension
