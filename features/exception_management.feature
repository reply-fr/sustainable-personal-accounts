Feature: exception management

As a system administrator,
I manage exceptions with a ticketing system
so as to support incident management and problem analysis

Scenario: where a budget alert triggers an exception
    Given an existing SPA system
     When the event 'BudgetAlertException' is emitted
     Then the Lambda function 'OnException' is invoked

Scenario: where a failed codebuild project triggers an exception
    Given an existing SPA system
     When the event 'FailedCodebuildException' is emitted
     Then the Lambda function 'OnException' is invoked

Scenario: where a failed on-boarding transaction triggers an exception
    Given an existing SPA system
     When the event 'FailedOnBoardingException' is emitted
     Then the Lambda function 'OnException' is invoked

Scenario: where a failed maintenance transaction triggers an exception
    Given an existing SPA system
     When the event 'FailedMaintenanceException' is emitted
     Then the Lambda function 'OnException' is invoked

Scenario: where a generic exception is handled
    Given an existing SPA system
     When the event 'GenericException' is emitted
     Then the Lambda function 'OnException' is invoked

Scenario: where an incident record is created on exception
    Given the default event bus of AWS account 'Automation' in an AWS Organisation
     When an exception event is put on the automation bus
     Then the Lambda function 'OnException' is invoked
      And an incident record is created in the response plan
      And the incident record is tagged with event information

Scenario: where an incident record is enriched with account information
    Given an exception that conveys an account id is put on the automation bus
      And an incident record is created on exception
     Then the incident record is tagged with account information
      And a cost report for current month for this account is attached to the incident record

Scenario: where an incident record is reviewed during resolution
    Given an incident record is created on exception
     When a system administrator reviews the incident record
     Then the incident record features a title and a summary as captured from the exception event
      And the incident record is tagged with exception label

Scenario: where an incident record enriched with account information is reviewed during resolution
    Given an exception that conveys an account id is put on the automation bus
      And an incident record is created on exception
     When a system administrator reviews the incident record
      And the incident record is tagged with account id, account email, account name and organizational unit
      And the incident record provides a web link to a cost and usage report for this account

Scenario: where a cost and usage report is reviewed during incident resolution
    Given an exception that conveys an account id is put on the automation bus
      And an incident record is created on exception
     When a system administrator reviews the incident record
      And a system administrator clicks on the link to the cost and usage report
     Then lambda function 'OnExceptionAttachmentDownload' is executed
      And the cost and usage report is downloaded to the workstation of system administrator
      And the cost and usage report can be inspected by system administrator

