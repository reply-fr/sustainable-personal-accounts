Feature: manage confirmations from end users

As a system administrator,
I maintain a list of documents for end users
so as to ensure automatic awareness of term and conditions across end users

As an end user,
I can access documents pushed to me and express feedback
so as to stay informed of terms of service and similar documents related to the service


Scenario: where no sending recipient has been configured
    Given a settings file 'settings.yaml' adapted to SPA semantics
     When the attribute 'with_sending_email_address' is not set in the section 'features'
      And SPA is deployed with the settings file 'settings.yaml'
     Then cloud resources are not deployed for automated confirmations

Scenario: where a sending recipient is configured
    Given a settings file 'settings.yaml' adapted to SPA semantics
     When the attribute 'with_sending_email_address' is set to 'service@example.com' in the section 'features'
      And SPA is deployed with the settings file 'settings.yaml'
     Then cloud resources are deployed for automated confirmations
      And lambda function 'OnUserDocumentAssociation' is triggered on event 'UserDocumentAssociation'
      And lambda function 'OnUserDocumentConfirmation' is triggered on function URL
      And lambda function 'OnUserDocumentExpiration' is triggered on transaction stream
      And lambda function 'OnMonthlyConfirmationsReport' is triggered on first day of each month

Scenario: where end-user documents are loaded into the system
    Given a settings file 'settings.yaml' adapted to SPA semantics
     When the attribute 'with_sending_email_address' is set to 'service@example.com' in the section 'features'
      And the attribute 'with_end_user_documents' is set in the section 'features'
      And SPA is deployed with the settings file 'settings.yaml'
     Then SPA loads all files mentioned in the attribute 'with_end_user_documents'
      And each document is put as a separate parameter in the SSM Parameter Store

Scenario: where missing confirmations are checked on account release
    Given an existing SPA system
     When an event 'ReleasedAccount' for account '123456789012' is posted to the bus
     Then lambda function 'OnUserDocumentCheck' handles the event 'ReleasedAccount'
      And code retrieves settings for account '123456789012'
      And the configuration item has attribute 'enabled' set to 'true' in attribute 'confirmations'
      And code retrieves the email 'alice@example.com' associated with the account
      And code scans the list of documents from SSM parameter store
      And code scans transactions for 'alice@example.com'
      And code emits event 'UserDocumentAssociation' for email 'alice@example.com' and for first missing document

Scenario: where an end-user is associated with a document
    Given an existing SPA system
     When the attribute 'with_sending_email_address' is set to 'service@example.com' in the section 'features'
      And an event 'UserDocumentAssociation' for email 'alice@example.com' and document 'terms_v0' is posted to the bus
     Then lambda function 'OnUserDocumentAssociation' handles the event 'UserDocumentAssociation'
      And code loads content of document 'terms_v0' from the SSM Parameter Store
      And code stops if a transaction 'alice@example.com terms_v0' already exists
      And a transaction 'alice@example.com terms_v0' is set with time of 'UserDocumentAssociation' and short-term ttl
      And code prepares a mail message based on 'terms_v0' and with feedback link to Lambda function 'OnUserDocumentConfirmation'
      And code sends the mail message from recipient 'service@example.com' to recipient 'alice@example.com'

Scenario: where an end-user confirms the reading of the document
    Given an existing SPA system
      And a confirmation message is sent over email to 'alice@example.com'
     When recipient of the message activates the confirmation link placed at the bottom of the message
     Then lambda function 'OnUserDocumentConfirmation' is executed with parameter 'alice@example.com terms_v0'
      And code retrieves transaction 'alice@example.com terms_v0'
      And code stops if there is no transaction 'alice@example.com terms_v0'
      And code stops if transaction 'alice@example.com terms_v0' has been already stamped
      And code stamps transaction 'alice@example.com terms_v0' with current time and long-term ttl
      And an event 'SuccessfulUserDocumentAssociation' is emitted for email 'alice@example.com' and document 'terms_v0'

Scenario: where a document association fails on time-out
    Given an existing SPA system
      And a confirmation message is sent over email to 'alice@example.com'
     When no invocation of lambda function 'OnUserDocumentConfirmation' is taking place with parameter 'alice@example.com terms_v0'
     Then the transaction 'alice@example.com terms_v0' is expired
      And lambda function 'OnUserDocumentExpiration' is executed
      And an event 'FailedUserDocumentAssociation' is emitted for email 'alice@example.com' and document 'terms_v0'

Scenario: where confirmations are reported every month
    Given an existing SPA system
     When the Lambda function 'OnMonthlyConfirmationsReport' is invoked
     Then code scans transactions
      And code pushes list of emails and confirmed documents as monthly CSV files on S3 reporting bucket


