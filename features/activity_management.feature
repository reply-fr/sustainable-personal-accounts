Feature: record and report on metered transactions and activities originating from SPA

As a system administrator,
I record metered transactions
so as to show/charge back costs of account management

Scenario: where a successful on-boarding transaction is recorded
    Given an existing SPA system
     When the event 'SuccessfulOnBoardingEvent' is emitted
     Then the Lambda function 'OnActivityEvent' is invoked

Scenario: where a successful maintenance transaction is recorded
    Given an existing SPA system
     When the event 'SuccessfulMaintenanceEvent' is emitted
     Then the Lambda function 'OnActivityEvent' is invoked

Scenario: where an activity is recorded
    Given the default event bus of AWS account 'Automation' in an AWS Organisation
     When an activity event is put on the automation bus
     Then the Lambda function 'OnActivityEvent' is invoked
      And the event is recorded in table 'Activities'

Scenario: where activites are reported everyday for current month
    Given an existing SPA system
     When the Lambda function 'OnDailyActivitiesReport' is invoked
     Then code scans the table 'Activities' for current month
      And code reports a list of activities as one CSV file per month on S3 reporting bucket

Scenario: where activities are reported for previous month
    Given an existing SPA system
     When the Lambda function 'OnMonthlyActivitiesReport' is invoked
     Then code scans the table 'Activities' for current month
      And code reports a list of activities as one CSV file per month on S3 reporting bucket

