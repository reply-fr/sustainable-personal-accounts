Feature: management of AWS accounts with configuration files

As a system administrator,
I edit settings files
so as to act on accounts that I manage

As a system administrator,
I edit settings files
so as to configure features of SPA itself


Scenario: where tags are set for an account
    Given a settings file 'settings.yaml' adapted to SPA semantics
      And a configuration item with identifier '123456789012' is added to the section 'accounts'
     When the configuration item features a set of tags in attribute 'account_tags'
      And the configuration item has a list of tags to remove in attribute 'unset_tags'
      And SPA is deployed with the settings file 'settings.yaml'
     Then the account '123456789012' is tagged and untagged during account preparation

Scenario: where tags are set for all accounts in an organizational unit
    Given a settings file 'settings.yaml' adapted to SPA semantics
      And a configuration item with identifier 'ou-abc' is added to the section 'organizational_units'
     When the configuration item features a set of tags in attribute 'account_tags'
      And the configuration item has a list of tags to remove in attribute 'unset_tags'
      And SPA is deployed with the settings file 'settings.yaml'
     Then all accounts in the organizational unit 'ou-abc' are tagged and untagged during account preparation

Scenario: where preparation is configured for an account
    Given a settings file 'settings.yaml' adapted to SPA semantics
      And a configuration item with identifier '123456789012' is added to the section 'accounts'
     When the configuration item has attribute 'enabled' set to 'true' in attribute 'preparation'
      And the configuration item has attribute 'variables' set to a list of key-values in attribute 'preparation'
      And SPA is deployed with the settings file 'settings.yaml'
     Then a Codebuild project 'SpaProjectForAccountPreparation' is launched in account '123456789012' during account preparation
      And the list of 'variables' in passed as environment variables to the project

Scenario: where preparation is configured for all accounts of an organizational unit
    Given a settings file 'settings.yaml' adapted to SPA semantics
      And a configuration item with identifier 'ou-abc' is added to the section 'organizational_units'
     When the configuration item has attribute 'enabled' set to 'true' in attribute 'preparation'
      And the configuration item has attribute 'variables' set to a list of key-values in attribute 'preparation'
      And SPA is deployed with the settings file 'settings.yaml'
     Then a Codebuild project 'SpaProjectForAccountPreparation' is launched in each account of the organizational unit 'ou-abc' during account preparation
      And the list of 'variables' in passed as environment variables to each project

Scenario: where purge is configured for an account
    Given a settings file 'settings.yaml' adapted to SPA semantics
      And a configuration item with identifier '123456789012' is added to the section 'accounts'
     When the configuration item has attribute 'enabled' set to 'true' in attribute 'purge'
      And the configuration item has attribute 'variables' set to a list of key-values in attribute 'purge'
      And SPA is deployed with the settings file 'settings.yaml'
     Then a Codebuild project 'SpaProjectForAccountPurge' is launched in account '123456789012' during account purge
      And the list of 'variables' in passed as environment variables to the project

Scenario: where purge is configured for all accounts of an organizational unit
    Given a settings file 'settings.yaml' adapted to SPA semantics
      And a configuration item with identifier 'ou-abc' is added to the section 'organizational_units'
     When the configuration item has attribute 'enabled' set to 'true' in attribute 'purge'
      And the configuration item has attribute 'variables' set to a list of key-values in attribute 'purge'
      And SPA is deployed with the settings file 'settings.yaml'
     Then a Codebuild project 'SpaProjectForAccountPurge' is launched in each account of the organizational unit 'ou-abc' during account purge
      And the list of 'variables' in passed as environment variables to each project

Scenario: where default settings are provided for managed organizational units and accounts
    Given a settings file 'settings.yaml' adapted to SPA semantics
     When a section 'defaults' is added to 'settings.yaml'
      And SPA is deployed with the settings file 'settings.yaml'
     Then attributes of the 'defaults' section are used as default values for items listed in the section 'organizational_units'
      And attributes of the 'defaults' section are used as default values for items listed in the section 'accounts'

Scenario: where maintenance window is configured
    Given a settings file 'settings.yaml' adapted to SPA semantics
     When the attribute 'maintenance_window_expression' is set in the section 'automation'
      And SPA is deployed with the settings file 'settings.yaml'
     Then the maintenance window is triggered by SPA according to 'maintenance_window_expression'

Scenario: where buildspec is set for the preparation of accounts
    Given a settings file 'settings.yaml' adapted to SPA semantics
     When the attribute 'preparation_buildspec_template_file' is set in the section 'worker'
      And SPA is deployed with the settings file 'settings.yaml'
     Then the content of file 'preparation_buildspec_template_file' is saved as parameter 'preparation_buildspec' at the time of SPA deployment
      And 'preparation_buildspec' is used for subsequent Codebuild projects during the preparation of accounts

Scenario: where buildspec is set for the purge of accounts
    Given a settings file 'settings.yaml' adapted to SPA semantics
     When the attribute 'purge_buildspec_template_file' is set in the section 'worker'
      And SPA is deployed with the settings file 'settings.yaml'
     Then the content of file 'purge_buildspec_template_file' is saved as parameter 'purge_buildspec' at the time of SPA deployment
      And 'purge_buildspec' is used for subsequent Codebuild projects during the purge of accounts

Scenario: where SPA is deployed on AWS
    Given a settings file 'settings.yaml' adapted to SPA semantics
     When the attribute 'account_id' is set to '123456789012' in the section 'automation'
      And the attribute 'region' is set to 'eu-west-1' in the section 'automation'
      And the attribute 'tags' in the section 'automation' features a set of tags
      And SPA is deployed with the settings file 'settings.yaml'
     Then Lambda functions and permanent resources of SPA are deployed in account '123456789012' and in region 'eu-west-1'
      And lambda functions and permanent resources of SPA are tagged according to the attribute 'tags'

Scenario: where SPA is deployed on Intel architecture
    Given a settings file 'settings.yaml' adapted to SPA semantics
     When the attribute 'with_arm_architecture' is not set to 'true' in the section 'features'
      And SPA is deployed with the settings file 'settings.yaml'
     Then Lambda functions of SPA are deployed on Intel architecture
      And CodeBuild projects of SPA are deployed on Intel architecture

Scenario: where SPA is deployed on ARM architecture
    Given a settings file 'settings.yaml' adapted to SPA semantics
     When the attribute 'with_arm_architecture' is set to 'true' in the section 'features'
      And SPA is deployed with the settings file 'settings.yaml'
     Then Lambda functions of SPA are deployed on ARM architecture
      And CodeBuild projects of SPA are deployed on ARM architecture

Scenario: where configuration is loaded from multiple CSV files
    Given a settings file 'settings.yaml' adapted to SPA semantics
     When the attribute 'with_csv_files' is set in the section 'features'
      And SPA is deployed with the settings file 'settings.yaml'
     Then SPA loads all CSV files mentioned in the attribute 'with_tag_files'
      And configuration items are created for each identifier mentioned in column 'Account'
      And configuration items have attribute 'account_tags' set to a list of key-values as per columns prefixed with 'Tag: '
      And configuration items have attribute 'variables' set to a list of key-values in attribute 'preparation' as per columns prefixed with 'Preparation: '
      And configuration items have attribute 'variables' set to a list of key-values in attribute 'purge' as per columns prefixed with 'Purge: '

Scenario: where the storage back-end for metering is configured
    Given a settings file 'settings.yaml' adapted to SPA semantics
      And the attribute 'datastore' is set in the section 'metering'
      And the attribute 'transactions_timeout_in_seconds' is set in the section 'metering'
      And SPA is deployed with the settings file 'settings.yaml'
     Then storage back-end for metering is provisioned on AWS infrastructure
      And the storage backend is configured with a TTL of 'transactions_timeout_in_seconds'
      And the storage endpoint is passed as environment variable to Lambda functions
      And deleted items are sent to Lambda function 'OnTransactionEvent'

Scenario: where timeout for on-going transactions is configured
    Given a settings file 'settings.yaml' adapted to SPA semantics
      And SPA is deployed with the settings file 'settings.yaml'
     Then the attribute 'transactions_timeout_in_seconds' is passed as environment variable to Lambda functions
