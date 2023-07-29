Feature: manage notifications to end users

As a system administrator,
I submit terms and conditions to end users and get confirmations
so as to ensure automatic awareness of term and conditions across end users

As a system administrator,
I submit documents to end users and get confirmations
so as to notify end users through the life cycle of their personal accounts

As an end user,
I can access documents pushed to me and express feedback
so as to stay informed of terms of service and similar documents related to the service


Scenario: where no sending recipient has been configured
    Given a settings file 'settings.yaml' adapted to SPA semantics
     When the attribute 'with_sending_email_address' is not set in the section 'features'
      And SPA is deployed with the settings file 'settings.yaml'
     Then there is a warning that notifications are not effective

Scenario: where default notifications are configured
    Given a settings file 'settings.yaml' adapted to SPA semantics
     When the attribute 'notifications' is set in the configuration item 'defaults'
      And the configuration item has attribute 'enabled' set to boolean value in attribute 'notifications'
      And the configuration item has attribute 'documents' set to a list of key-values in attribute 'notifications'
      And the configuration item has attribute 'context' set to a list of key-values in attribute 'notifications'
      And SPA is deployed with the settings file 'settings.yaml'
     Then SPA loads all labels and files mentioned in the attribute 'documents'
      And one parameter is created in SSM Parameter Store for each label and file content

Scenario: where notifications are configured for an account
    Given a settings file 'settings.yaml' adapted to SPA semantics
     When a configuration item with identifier '123456789012' is added to the section 'accounts'
      And the configuration item has attribute 'enabled' set to boolean value in attribute 'notifications'
      And the configuration item has attribute 'documents' set to a list of key-values in attribute 'notifications'
      And the configuration item has attribute 'context' set to a list of key-values in attribute 'notifications'
      And SPA is deployed with the settings file 'settings.yaml'
     Then SPA loads all labels and files mentioned in the attribute 'documents'
      And each label is suffixed with '-123456789012'
      And one parameter is created in SSM Parameter Store for each label and file content

Scenario: where notifications are configured for all accounts of an organizational unit
    Given a settings file 'settings.yaml' adapted to SPA semantics
     When a configuration item with identifier 'ou-abc' is added to the section 'organizational_units'
      And the configuration item has attribute 'enabled' set to boolean value in attribute 'notifications'
      And the configuration item has attribute 'documents' set to a list of key-values in attribute 'notifications'
      And the configuration item has attribute 'context' set to a list of key-values in attribute 'notifications'
      And SPA is deployed with the settings file 'settings.yaml'
     Then SPA loads all labels and files mentioned in the attribute 'documents'
      And each label is suffixed with '-ou-abc'
      And one parameter is created in SSM Parameter Store for each label and file content

Scenario: where first missing notification is sent on account release
    Given an existing SPA system
     When lambda function 'OnReleasedAccount' is executed on account '123456789012'
     Then code retrieves settings for account '123456789012'
      And the configuration item has attribute 'enabled' set to 'true' in attribute 'notifications'
      And code retrieves the email 'alice@example.com' associated with the account
      And code retrieves past notifications for email 'alice@example.com' from the table 'NotificationsTable'
      And first missing notification is 'terms_v0'
      And code loads content of document 'terms_v0' from the SSM Parameter Store
      And code contextualises document with key-values from 'context' in attribute 'notifications'
      And code records notification for identifier 'alice@example.com' and order 'terms_v0' in the table 'NotificationsTable'
      And code prepares a mail message based on 'terms_v0' and with feedback link to Lambda function 'OnAcknowledgement'
      And code sends the mail message from recipient 'service@example.com' to recipient 'alice@example.com'
      And an event 'NotificationEvent' is emitted for account '123456789012'

Scenario: where a notification is acknowledged by end-user
    Given an existing SPA system
      And a notification message is sent over email to 'alice@example.com'
     When recipient of the message activates the notification link placed at the bottom of the message
     Then lambda function 'OnAcknowledgement' is executed with parameter 'alice@example.com terms_v0'
      And code retrieves record for identifier 'alice@example.com' and order 'terms_v0' from the table 'NotificationsTable'
      And code stops if record has been already stamped
      And code stamps record with current time and long-term ttl
      And an event 'AckowledgementEvent' is emitted for account '123456789012'

Scenario: where notifications are reported every month
    Given an existing SPA system
     When time is coming for a scheduled execution of 'OnMonthlyNotificationsReport'
     Then the Lambda function 'OnMonthlyNotificationsReport' is invoked
      And code scans records from table 'NotificationsTable'
      And code pushes list of emails and confirmed documents as monthly CSV files on S3 reporting bucket


