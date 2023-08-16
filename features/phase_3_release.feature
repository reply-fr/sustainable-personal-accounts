Feature: release of individual cloud account

    As an employee,
    I use the individual cloud account that has been assigned to me
    so as to learn, build, test and to innovate with AWS services

    Scenario: where authenticated employee is entitled to create and delete resources
        Given an individual cloud account is tagged with key 'account-state' and value 'released'
        When employee assigned to the account signs in using SSO
        Then cloud resources can be created, modified and deleted

    Scenario: where accounts are expired on maintenance window
        Given a scheduled maintenance window
        When maintenance window is reached
        Then lambda function 'OnMaintenanceWindow' is executed
        And code scans the accounts of all configured organizational units
        And code tags each released account with key 'account-state' and value 'expired'
