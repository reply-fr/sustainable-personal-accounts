Feature: purge of individual cloud accounts

    As cloud practice owner,
    I purge as many resources as possible from each individual cloud account
    so as to enforce software engineering best practices

    Scenario: where account expiration is detected and processed
        Given a buildspec configuration for the purge of accounts
        And SCP policies have been configured for expired accounts in hosting organizational unit
        When the account is tagged with key 'account-state' and value 'expired'
        Then lambda function 'OnExpiredAccount' is executed
        And code emits an event 'ExpiredAccount'
        And code attachs SCP policies configured for expired accounts of the hosting organizational unit
        And code forwards codebuild events to central event bus
        And code creates codebuild project 'PurgeAccount' in target account
        And code starts codebuild project 'PurgeAccount' asynchronously

    Scenario: where account has been purged
        Given a central event bus
        And codebuild events are forwarded to central event bus
        When codebuild project 'PurgeAccount' is completed or has failed
        Then lambda function 'OnPurgedAccount' is executed
        And code tags account with key 'account-state' and value 'assigned'
        And code emits an event 'PurgedAccount'

    Scenario: where authenticated employee is prevented to create resources in expired account
        Given lambda function 'OnExpiredAccount' has been executed
        When employee assigned to the account signs in using SSO
        Then no cloud resource can be created
