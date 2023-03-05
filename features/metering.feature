Feature: metering of SPA transactions

As a system administrator,
I observe end-to-end transactions
so as to show/charge back costs of account management

As a system administrator,
I observe end-to-end transactions
so as to identify possible issues on some accounts


Scenario: where an on-boarding transaction begins
    Given an account '123456789012' that is managed by SPA
     When the event 'CreatedEvent' is emitted for account '123456789012'
     Then lambda function 'OnAccountEventThenMeter' is executed
      And a transaction 'OnBoarding 123456789012' is set with time of 'CreatedEvent'

Scenario: where an on-boarding transaction ends
    Given an account '123456789012' that is managed by SPA
      And a transaction 'OnBoarding 123456789012' is set with time of 'CreatedEvent'
     When the event 'ReleasedEvent' is emitted for account '123456789012'
     Then lambda function 'OnAccountEventThenMeter' is executed
      And a transaction 'OnBoarding 123456789012' is retrieved
      And an event 'SuccessfulOnboardingEvent' is emitted with duration between 'CreatedEvent' and 'ReleasedEvent'

Scenario: where an on-boarding transaction fails on timeout
    Given an account '123456789012' that is managed by SPA
      And a transaction 'OnBoarding 123456789012' is set with time of 'CreatedEvent'
     When no event 'ReleasedEvent' is emitted for account '123456789012' during 'transactions_timeout_in_seconds'
     Then lambda function 'OnTransactionEvent' is executed
      And an event 'FailedOnboardingEvent' is emitted with last event received for account '123456789012'

Scenario: where a maintenance transaction begins
    Given an account '123456789012' that is managed by SPA
     When the event 'ExpiredEvent' is emitted for account '123456789012'
     Then lambda function 'OnAccountEventThenMeter' is executed
      And a transaction 'Maintenance 123456789012' is set for time of 'ExpiredEvent'

Scenario: where a maintenance transaction ends
    Given an account '123456789012' that is managed by SPA
      And a transaction 'Maintenance 123456789012' is set for time of 'ExpiredEvent'
     When the event 'ReleasedEvent' is emitted for account '123456789012'
     Then lambda function 'OnAccountEventThenMeter' is executed
      And a transaction 'Maintenance 123456789012' is retrieved
      And an event 'SuccessfulMaintenanceEvent' is emitted with duration between 'ExpiredEvent' and 'ReleasedEvent'

Scenario: where a maintenance transaction fails on timeout
    Given an account '123456789012' that is managed by SPA
      And a transaction 'Maintenance 123456789012' is set for time of 'ExpiredEvent'
     When no event 'ReleasedEvent' is emitted for account '123456789012' during 'transactions_timeout_in_seconds'
     Then lambda function 'OnTransactionEvent' is executed
      And an event 'FailedMaintenanceEvent' is emitted with last event received for account '123456789012'

