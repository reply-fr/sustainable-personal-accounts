Feature: management of login to the AWS console

As a system administrator,
I can monitor console logins
in order to control activities of account users

As a system administrator,
I can detect console logins with root credentials
in order to manage deviations from corporate policies

As a system administrator,
I can detect console logins with IAM user credentials
in order to manage deviations from corporate policies


Scenario: where console login events across accounts are consolidated to one event bus
    Given an existing SPA system
      And SPA is listening from bus on account '111111111111'
     When lambda function 'OnAssignedAccount' is executed for account '123456789012'
     Then a forwarding rule is deployed on account '123456789012' to push console login events to bus of '111111111111'

Scenario: where a regular console login is processed as part of shadow updates
    Given an existing SPA system
     When a 'console login' event for account '123456789012' is put from 'aws.signin'
      And the 'console login' event is of type 'AssumedRole'
     Then lambda function 'OnConsoleLogin' is executed with the event
      And the date of the event is stored as stamp 'ConsoleLogin' in the shadow record of the account '123456789012'
      And a 'ConsoleLoginEvent' event for account '123456789012' is put from 'SustainablePersonalAccounts'

Scenario: where date of last console login is reported in account inventories
    Given an existing SPA system
     When the Lambda function 'OnInventoryReport' is executed
     Then code reflects stamp 'ConsoleLogin' from shadow records in the inventory CSV reports

Scenario: where a console login with root credentials is managed as an exception
    Given an existing SPA system
     When a 'console login' event for account '123456789012' is put by 'aws.signin'
      And the 'console login' event is of type 'Root'
     Then lambda function 'OnConsoleLogin' is executed with the event
      And a 'ConsoleLoginWithRootException' event for account '123456789012' is put from 'SustainablePersonalAccounts'

Scenario: where a console login with IAM user credentials is managed as an exception
    Given an existing SPA system
     When a 'console login' event for account '123456789012' is put by 'aws.signin'
      And the 'console login' event is of type 'IAMUser'
     Then lambda function 'OnConsoleLogin' is executed with the event
      And a 'ConsoleLoginWithIamUserException' event for account '123456789012' is put from 'SustainablePersonalAccounts'
