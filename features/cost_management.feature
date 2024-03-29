Feature: costing of AWS consumption per cost center

    As a system administrator,
    I observe AWS costs as a daily metric
    so as to monitor and to manage consumption of AWS resources per cost center

    As an accountant,
    I need a monthly breakdown of AWS costs per cost center
    so as to charge back cost centers individually


    Scenario: where no cost management tag has been configured
        Given a settings file 'settings.yaml' adapted to SPA semantics
        When the attribute 'with_cost_management_tag' is not set in the section 'features'
        And SPA is deployed with the settings file 'settings.yaml'
        Then the daily cost metric is not deployed
        And the monthly cost report is not deployed

    Scenario: where the tag used for cost management is configured
        Given a settings file 'settings.yaml' adapted to SPA semantics
        When the attribute 'with_cost_management_tag' is set to 'cost-center' in the section 'features'
        And SPA is deployed with the settings file 'settings.yaml'
        Then the daily cost metric is deployed
        And the monthly cost report is deployed
        And the dashboard reflects daily costs per cost center
        And the reporting bucket is populated with monthly reports per cost center

    Scenario: where additional currencies are configured for reports
        Given a settings file 'settings.yaml' adapted to SPA semantics
        When the attribute 'with_cost_extra_currencies' is set to '[EUR, GBP]' in the section 'features'
        And SPA is deployed with the settings file 'settings.yaml'
        Then the environment variable 'COST_EXTRA_CURRENCIES' is set to '[EUR, GBP]' for function 'OnMonthlyCostReport'

    Scenario: where cloud costs are computed and released every day
        Given an existing SPA system
        When time is coming for a scheduled execution of 'OnDailyCostsMetric'
        Then the Lambda function 'OnDailyCostsMetric' is invoked
        And code inspects all accounts managed in the system
        And code computes cost report for each account on previous day
        And code sums up cost reports per cost center
        And code pushes daily costs as a CloudWatch Metric
        And daily costs are reflected in the SPA monitoring dashboard

    Scenario: where cloud costs are computed and released every month
        Given an existing SPA system
        When time is coming for a scheduled execution of 'OnMonthlyCostsReport'
        Then the Lambda function 'OnMonthlyCostsReport' is invoked
        And code inspects all accounts managed in the system
        And code computes cost report for each account on previous month
        And code sums up cost reports per cost center
        And code pushes detailed monthly reports as one CSV file per cost center on S3 reporting bucket
        And code pushes detailed monthly reports as one Excel file per cost center on S3 reporting bucket
        And code pushes summary monthly report as one CSV file listing every cost center on S3 reporting bucket
        And code pushes summary monthly report as one Excel file listing every cost center on S3 reporting bucket

    Scenario: where reports are produced for extra currencies
        Given an existing SPA system
        When the Lambda function 'OnMonthlyCostsReport' is invoked
        Then code pushes one summary report as one Excel file for each currency of variable 'COST_EXTRA_CURRENCIES'

    Scenario: where costs per cost center are spread over email every month
        Given an existing SPA system
        And the attribute 'with_origin_email_recipient' is set to 'cost@example.com' in the section 'features'
        And the attribute 'with_cost_email_recipients' is set to 'alice@example.com, bob@example.com' in the section 'features'
        When the Lambda function 'OnMonthlyCostsReport' is invoked
        Then code sends the summary monthly reports (Excel and CSV files) over email to recipients 'alice@example.com, bob@example.com'
