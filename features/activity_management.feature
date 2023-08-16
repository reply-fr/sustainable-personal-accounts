Feature: management of account activities and transactions

    As a system administrator,
    I want to record on-boarding transactions
    so as to monitor and to manage service usage per cost center

    As a system administrator,
    I want to record maintenance transactions
    so as to monitor and to manage service usage per cost center

    As a system administrator,
    I want to record console logins
    so as to monitor and to manage service usage per cost center

    As a system administrator,
    I want to record acknowledged notifications of account holders
    so as to monitor and to manage service usage per cost center

    As a system administrator,
    I observe activities as daily metrics
    so as to monitor and to manage service usage per cost center

    As a system administrator,
    I check the on-going report on activities
    so as to monitor and to manage service usage per cost center

    As a system administrator,
    I check the monthly reports on activities
    so as to monitor and to manage service usage per cost center

    Scenario: where a successful on-boarding transaction is recorded
        Given an existing SPA system
        When a 'SuccessfulOnBoardingEvent' event for account '123456789012' is put from 'SustainablePersonalAccounts'
        Then lambda function 'OnActivityEvent' is executed with the event
        And details of the activity are put in a new record in the table 'ActivitiesTable'
        And a data point is put to metric 'TransactionsByCostCenter'
        And a data point is put to metric 'TransactionsByLabel'

    Scenario: where a successful maintenance transaction is recorded
        Given an existing SPA system
        When a 'SuccessfulMaintenanceEvent' event for account '123456789012' is put from 'SustainablePersonalAccounts'
        Then lambda function 'OnActivityEvent' is executed with the event
        And details of the activity are put in a new record in the table 'ActivitiesTable'
        And a data point is put to metric 'TransactionsByCostCenter'
        And a data point is put to metric 'TransactionsByLabel'

    Scenario: where a regular console login event is metered
        Given an existing SPA system
        When a 'ConsoleLoginEvent' event for account '123456789012' is put from 'SustainablePersonalAccounts'
        Then lambda function 'OnActivityEvent' is executed with the event
        And details of the activity are put in a new record in the table 'ActivitiesTable'
        And a data point is put to metric 'TransactionsByCostCenter'
        And a data point is put to metric 'TransactionsByLabel'

    Scenario: where an acknowledged notification is metered
        Given an existing SPA system
        When a 'AcknowledgedNotificationEvent' event for account '123456789012' is put from 'SustainablePersonalAccounts'
        Then lambda function 'OnActivityEvent' is executed with the event
        And details of the activity are put in a new record in the table 'ActivitiesTable'
        And a data point is put to metric 'TransactionsByCostCenter'
        And a data point is put to metric 'TransactionsByLabel'

    Scenario: where activities appear in the monitoring dashboard
        Given an existing SPA system
        Then the monitoring dashboard displays metric 'TransactionsByCostCenter'
        And the monitoring dashboard displays metric 'TransactionsByLabel'

    Scenario: where activites are reported for current month
        Given an existing SPA system
        When time is coming for a scheduled execution of 'OnOngoingActivitiesReport'
        Then the Lambda function 'OnOngoingActivitiesReport' is invoked
        And code scans the table 'ActivitiesTable' for current month
        And code reports a list of activities as one CSV file per month on S3 reporting bucket

    Scenario: where activities are reported for previous month
        Given an existing SPA system
        When time is coming for a scheduled execution of 'OnPastActivitiesReport'
        Then the Lambda function 'OnPastActivitiesReport' is invoked
        And code scans the table 'ActivitiesTable' for previous month
        And code reports a list of activities as one CSV file per month on S3 reporting bucket

