Feature: metering of SPA transactions

As a system administrator,
I observe end-to-end transactions
so as to show/charge back costs of account management

As a system administrator,
I observe end-to-end transactions
so as to identify possible issues on some accounts


Scenario: where an account is on-boarded as a transaction
    Given an account '123456789012' that is managed by SPA
     When the event 'CreatedEvent' is emitted for account '123456789012' and transaction 'abc'
      And the event 'AssignedEvent' is emitted for account '123456789012' and transaction 'abc'
      And the event 'PreparedEvent' is emitted for account '123456789012' and transaction 'abc'
      And the event 'ReleasedEvent' is emitted for account '123456789012' and transaction 'abc'
     Then an event 'SuccessfulOnboardingEvent' is emitted as transaction 'abc' and with duration between 'CreatedEvent' and 'ReleasedEvent'

Scenario: where an account is only tagged on on-boarding
    Given an account '123456789012' that is managed by SPA
     When the event 'CreatedEvent' is emitted for account '123456789012' and transaction 'abc'
      And the event 'AssignedEvent' is emitted for account '123456789012' and transaction 'abc'
      And the event 'ReleasedEvent' is emitted for account '123456789012' and transaction 'abc'
     Then an event 'SuccessfulOnboardingEvent' is emitted as transaction 'abc' and with duration between 'CreatedEvent' and 'ReleasedEvent'

Scenario: where an account is purged and prepared on maintenance window
    Given an account '123456789012' that is managed by SPA
     When the event 'ExpiredEvent' is emitted for account '123456789012' and transaction 'xyz'
      And the event 'PurgedEvent' is emitted for account '123456789012' and transaction 'xyz'
      And the event 'AssignedEvent' is emitted for account '123456789012' and transaction 'xyz'
      And the event 'PreparedEvent' is emitted for account '123456789012' and transaction 'xyz'
      And the event 'ReleasedEvent' is emitted for account '123456789012' and transaction 'xyz'
     Then an event 'SuccessfulMaintenanceEvent' is emitted as transaction 'xyz' and with duration between 'ExpiredEvent' and 'ReleasedEvent'

Scenario: where an account is only prepared on maintenance window
    Given an account '123456789012' that is managed by SPA
     When the event 'ExpiredEvent' is emitted for account '123456789012' and transaction 'xyz'
      And the event 'AssignedEvent' is emitted for account '123456789012' and transaction 'xyz'
      And the event 'PreparedEvent' is emitted for account '123456789012' and transaction 'xyz'
      And the event 'ReleasedEvent' is emitted for account '123456789012' and transaction 'xyz'
     Then an event 'SuccessfulMaintenanceEvent' is emitted as transaction 'xyz' and with duration between 'ExpiredEvent' and 'ReleasedEvent'

Scenario: where an account is only purged on maintenance window
    Given an account '123456789012' that is managed by SPA
     When the event 'ExpiredEvent' is emitted for account '123456789012' and transaction 'xyz'
      And the event 'PurgedEvent' is emitted for account '123456789012' and transaction 'xyz'
      And the event 'AssignedEvent' is emitted for account '123456789012' and transaction 'xyz'
      And the event 'ReleasedEvent' is emitted for account '123456789012' and transaction 'xyz'
     Then an event 'SuccessfulMaintenanceEvent' is emitted as transaction 'xyz' and with duration between 'ExpiredEvent' and 'ReleasedEvent'

Scenario: where an account transparently passes through maintenance window
    Given an account '123456789012' that is managed by SPA
     When the event 'ExpiredEvent' is emitted for account '123456789012' and transaction 'xyz'
      And the event 'AssignedEvent' is emitted for account '123456789012' and transaction 'xyz'
      And the event 'ReleasedEvent' is emitted for account '123456789012' and transaction 'xyz'
     Then an event 'SuccessfulMaintenanceEvent' is emitted as transaction 'xyz' and with duration between 'ExpiredEvent' and 'ReleasedEvent'



