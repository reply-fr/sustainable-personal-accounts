Feature: metering of SPA transactions

  As a system administrator,
  I observe end-to-end transactions
  so as to show/charge back costs of account management

  As a system administrator,
  I detect not-terminated transactions
  so as to identify possible issues on some accounts


  Scenario: where an on-boarding transaction begins
    Given an account '123456789012' that is managed by SPA
    When the event 'CreatedEvent' is emitted for account '123456789012'
    Then lambda function 'OnTransactionMetering' is executed with the event
    And a transaction of type 'on-boarding' for account '123456789012' with stamp of 'CreatedEvent' is recorded in table 'TransactionsTable'

  Scenario: where an on-boarding transaction ends
    Given an account '123456789012' that is managed by SPA
    And a transaction of type 'on-boarding' for account '123456789012' with stamp of 'CreatedEvent' is recorded in table 'TransactionsTable'
    When the event 'ReleasedEvent' is emitted for account '123456789012'
    Then lambda function 'OnTransactionMetering' is executed with the event
    And transaction '123456789012' is retrieved
    And an event 'SuccessfulOnboardingEvent' is emitted with duration between 'CreatedEvent' and 'ReleasedEvent'

  Scenario: where an on-boarding transaction fails on timeout
    Given an account '123456789012' that is managed by SPA
    And a transaction of type 'on-boarding' for account '123456789012' with stamp of 'CreatedEvent' is recorded in table 'TransactionsTable'
    When no event 'ReleasedEvent' is emitted for account '123456789012' during 'on_boarding_timeout_in_seconds'
    Then lambda function 'OnTransactionTimeOut' is executed with the expired record from table 'TransactionsTable'
    And an event 'FailedOnboardingException' is emitted for account '123456789012' with data from the expired record

  Scenario: where a maintenance transaction begins
    Given an account '123456789012' that is managed by SPA
    When the event 'ExpiredEvent' is emitted for account '123456789012'
    Then lambda function 'OnTransactionMetering' is executed with the event
    And a transaction of type 'maintenance' for account '123456789012' with stamp of 'ExpiredEvent' is recorded in table 'TransactionsTable'

  Scenario: where a maintenance transaction ends
    Given an account '123456789012' that is managed by SPA
    And a transaction of type 'maintenance' for account '123456789012' with stamp of 'ExpiredEvent' is recorded in table 'TransactionsTable'
    When the event 'ReleasedEvent' is emitted for account '123456789012'
    Then lambda function 'OnTransactionMetering' is executed with the event
    And transaction '123456789012' is retrieved
    And an event 'SuccessfulMaintenanceEvent' is emitted with duration between 'ExpiredEvent' and 'ReleasedEvent'

  Scenario: where a maintenance transaction fails on timeout
    Given an account '123456789012' that is managed by SPA
    And a transaction of type 'maintenance' for account '123456789012' with stamp of 'ExpiredEvent' is recorded in table 'TransactionsTable'
    When no event 'ReleasedEvent' is emitted for account '123456789012' during 'maintenance_timeout_in_seconds'
    Then lambda function 'OnTransactionTimeOut' is executed with the expired record from table 'TransactionsTable'
    And an event 'FailedMaintenanceException' is emitted for account '123456789012' with data from the expired record

  Scenario: where a notification transaction begins
    Given an account '123456789012' that is managed by SPA
    When the event 'NotificationEvent' is emitted for account '123456789012'
    Then lambda function 'OnTransactionMetering' is executed with the event
    And a transaction with identifier '123456789012 notification' with stamp of 'NotificationEvent' is recorded in table 'TransactionsTable'

  Scenario: where a notification transaction ends
    Given an account '123456789012' that is managed by SPA
    And a transaction with identifier '123456789012 notification' with stamp of 'NotificationEvent' is recorded in table 'TransactionsTable'
    When the event 'AcknowledgementEvent' is emitted for account '123456789012'
    Then lambda function 'OnTransactionMetering' is executed with the event
    And transaction '123456789012 notification' is retrieved
    And an event 'AcknowledgedNotificationEvent' is emitted with duration between 'NotificationEvent' and 'AcknowledgementEvent'

  Scenario: where a notification transaction fails on timeout
    Given an account '123456789012' that is managed by SPA
    And a transaction with identifier '123456789012 notification' with stamp of 'NotificationEvent' is recorded in table 'TransactionsTable'
    When no event 'AcknowledgementEvent' is emitted for account '123456789012' during 'notification_timeout_in_seconds'
    Then lambda function 'OnTransactionTimeOut' is executed with the expired record from table 'TransactionsTable'
    And an event 'UnacknowlegdedNotificationException' is emitted for account '123456789012' with data from the expired record

