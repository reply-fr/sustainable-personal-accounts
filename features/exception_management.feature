Feature: exception management

As a system administrator,
I manage exceptions with a ticketing system
so as to support incident management and problem analysis

Scenario: where an exception creates a ticket
    Given the default event bus of AWS account 'Automation' in an AWS Organisation
      And a response plan has been configured in SPA settings
     When an exception event is put on this bus
     Then lambda function 'OnException' is executed
      And an incident record is created in the response plan
      And a cost report is attached to the incident record when an account id is provided



