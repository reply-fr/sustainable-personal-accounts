Feature: costing of AWS consumption per cost center

As a system administrator,
I observe AWS costs as a daily metric
so as to monitor and to manage consumption of AWS resources per cost center

As an acountant,
I need a monthly breakdown of AWS costs per cost center
so as to charge back cost centers individually


Scenario: where cloud costs are computed and released every day
    Given an existing SPA system
     When the Lambda function 'OnDailyCostMetric' is invoked
     Then code inspects all accounts managed in the system
      And code computes cost report for each account on previous day
      And code sums up cost reports per cost center
      And code pushes daily costs as a CloudWatch Metric
      And daily costs are reflected in the SPA monitoring dashboard

Scenario: where cloud costs are computed and released every month
    Given an existing SPA system
     When the Lambda function 'OnMonthlyCostReport' is invoked
     Then code inspects all accounts managed in the system
      And code computes cost report for each account on previous month
      And code sums up cost reports per cost center
      And code pushes monthly costs as a CSV file on S3 reporting bucket
