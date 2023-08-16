Feature: creation of an individual cloud account

    As an employee,
    I get an individual cloud account
    so as to learn, build, test and to innovate with AWS services

    Scenario: where an employee is eligible for an individual cloud account
        Given an employee
        When there is a need for accelerating digital innovation on cloud platform
        Then the employee is assigned an individual cloud account

    Scenario: where only one single account can be created for one e-mail address
        Given a decision has been made to assign an individual cloud account to an employee
        And an individual cloud account already exists for the e-mail address of this employee
        When a new individual cloud account is created
        Then an error is generated because an account with the same e-mail address already exists

    Scenario: where a cloud account is created in a managed organizational unit
        Given a cloud environment managed with AWS Organization
        And a decision has been made to assign an individual cloud account to an employee
        When an AWS account is created
        And the account has been put in an organizational unit managed by SPA
        And the account is assigned the corporate e-mail address of the requesting employee
        Then lambda function 'OnVanillaAccount' is executed

    Scenario: where a cloud account is set to vanilla state
        Given a cloud environment managed with AWS Organization
        And a decision has been made to validate an individual cloud account
        When the account is tagged with key 'account-state' and value 'vanilla'
        Then lambda function 'OnVanillaAccount' is executed

    Scenario: where vanilla account is processed
        Given tags have been configured for hosting organizational unit
        And SCP policies have been configured for assigned accounts in hosting organizational unit
        When lambda function 'OnVanillaAccount' is executed
        Then code tags the account with key 'account-holder' and value is the e-mail address of assigned employee
        And code tags the account account with tags configured for the organizational unit
        And code tags account with key 'account-state' and value 'assigned'
        And code attachs SCP policies configured for assigned accounts of the hosting organizational unit
        And code emits an event 'CreatedAccount'
