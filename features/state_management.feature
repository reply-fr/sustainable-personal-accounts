Feature: management of AWS accounts with tags

As a system administrator,
I can check account tags
in order to control account states at system scale

As a system administrator,
I can edit account tags
in order to set account states manually

As a system administrator,
I can align all account tags
so as to recover from transient states and software bugs


Scenario: where account states are checked globally
    Given an existing SPA system
     When the Lambda function 'CheckAccounts' is invoked
     Then code inspects all accounts managed in the system
      And the execution log provides a list of anomalies if any

Scenario: where account states are modified manually
    Given an existing SPA system
     When the system administrator goes to the AWS Organization console
      And the system administrator edits tags of an account managed in the system
     Then the state of the account is changed accordingly
      And a Lambda Function can process the account as part of the automated state machine

Scenario: where accounts are released globally
    Given an existing SPA system
     When the Lambda function 'ReleaseAccounts' is invoked
     Then code inspects all accounts managed in the system
      And all accounts that are not in release state are tagged to this state

