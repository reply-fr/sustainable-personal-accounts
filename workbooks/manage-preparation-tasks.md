# Manage preparation tasks

## Overview

SPA prepares an AWS account by running a CodeBuild project in it. This is happening when a account is created, and also on every maintenance window, presumably, every week or so.

1. [Set the `buildspec` that SPA will use for preparation of accounts](#step-1)
2. [Put shell commands directly in CodeBuild project](#step-2)
3. [Launch separate shell scripts in CodeBuild project](#step-3)

## Step 1: Set the `buildspec` that SPA will use for preparation of accounts <a id="step-1"></a>

SPA loads its configuration from the file mentioned in the environment variable `SETTINGS` or, by default, from `settings.yaml`.
The `buildspec` for the preparation of accounts is set in key `preparation_buildspec_template_file` in section `worker`.

For example:

```yaml
worker:  # resources deployed in managed accounts

  preparation_buildspec_template_file: "fixtures/buildspec/prepare-account-from-git.yaml"
```

SPA comes with two sample `buildspec` files that you can use directly, as in the example above.
Of course, you can prepare a preparation `buildspec` for the exact requirements of your company, and use it instead.

If the preparation of an account requires a limited number of shell commands, then you can put all of them in the `buildspec` directly.
Alternatively, code in the `buildspec` can load scripts from trusted sources and execute it. The two options are described below.

## Step 2: Put shell commands directly in CodeBuild project <a id="step-2"></a>

For example, if the preparation consists only into the configuration of a budget alert, then related statements can fit into a single `buildspec` file.

Typically, the `buildspec` starts by setting environment variables that are used by following statements. These are default settings, that can be overridden during the deployment of CodeBuild projects by SPA.

- **Infrastructure variables** - They are always set by SPA

  - `ENVIRONMENT_IDENTIFIER` - Label used for this SPA deployment
  - `EVENT_BUS_ARN` - The central EventBridge bus used by SPA
  - `TOPIC_ARN` - The SNS topic that is connected to SPA for budget alerts
  - `BUDGET_EMAIL` - The email to be used for this account

- **Settings variables** - SPA reads the `variables` list under the `preparation` key in settings file.
A typical use case is when you differentiate budget amounts across accounts and OUs. See `BUDGET_AMOUNT` in the file below.

- **Local variables** - These are set only within the `buildspec`, and they have the same value across accounts.

Shell commands are put in the `build` phase of the `buildspec`. Regular shell commands can be used, including piping, tests of variables, etc. Environment variables are preserved across statements. In addition, you can use any AWS CLI command.

This is demonstrated into the SPA file `fixtures/buildspec/preparation_account_template.yaml`, that is reproduced below.

```yaml
version: 0.2

env:
  variables:
    ALERT_THRESHOLD: 80 # percentage of budget
    BUDGET_AMOUNT: 500.0
    BUDGET_EMAIL: a@b.com
    BUDGET_NAME: SPA-budget
    ENVIRONMENT_IDENTIFIER: None
    EVENT_BUS_ARN: None
    TOPIC_ARN: None

phases:
  install:
    commands:
    - ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
    - echo "ALERT_THRESHOLD=$ALERT_THRESHOLD"
    - echo "BUDGET_AMOUNT=$BUDGET_AMOUNT"
    - echo "BUDGET_EMAIL=$BUDGET_EMAIL"
    - echo "BUDGET_NAME=$BUDGET_NAME"
    - echo "ENVIRONMENT_IDENTIFIER=$ENVIRONMENT_IDENTIFIER"
    - echo "EVENT_BUS_ARN=$EVENT_BUS_ARN"
    - echo "TOPIC_ARN=$TOPIC_ARN"

  build:
    commands:
    - |
      cat <<EOF >budget.json
      {
        "BudgetName": "${BUDGET_NAME}",
        "BudgetLimit": {
          "Amount": "${BUDGET_AMOUNT}",
          "Unit": "USD"
        },
        "BudgetType": "COST",
        "CostFilters": {},
        "CostTypes": {
          "IncludeTax": true,
          "IncludeSubscription": true,
          "UseBlended": false,
          "IncludeRefund": false,
          "IncludeCredit": false,
          "IncludeUpfront": true,
          "IncludeRecurring": true,
          "IncludeOtherSubscription": true,
          "IncludeSupport": true,
          "IncludeDiscount": true,
          "UseAmortized": false
        },
        "TimePeriod": {
          "Start": "2020-01-01T01:00:00+01:00",
          "End": "2080-01-01T02:00:00+02:00"
        },
        "TimeUnit": "MONTHLY"
      }
      EOF
    - |
      cat <<EOF >notifications-with-subscribers.json
      [
        {
          "Notification": {
            "ComparisonOperator": "GREATER_THAN",
            "NotificationType": "ACTUAL",
            "Threshold": ${ALERT_THRESHOLD},
            "ThresholdType": "PERCENTAGE"
          },
          "Subscribers": [
            {
              "Address": "${BUDGET_EMAIL}",
              "SubscriptionType": "EMAIL"
            },
            {
              "Address": "${TOPIC_ARN}",
              "SubscriptionType": "SNS"
            }
          ]
        }
      ]
      EOF
    - CURRENT_AMOUNT=$(aws budgets describe-budget --account-id $ACCOUNT --budget-name $BUDGET_NAME --query 'Budget.BudgetLimit.Amount' --output text) || true
    - |
      if [ -z "$CURRENT_AMOUNT" ]; then
        echo "Creating new budget"
        aws budgets create-budget --account-id $ACCOUNT --budget file://budget.json --notifications-with-subscribers file://notifications-with-subscribers.json
      elif [ "$CURRENT_AMOUNT" != "$BUDGET_AMOUNT" ]; then
        echo "Updating budget"
        aws budgets update-budget --account-id $ACCOUNT --new-budget file://budget.json
      else
        echo "No budget modification"
      fi
    - echo "Enforce IAM password policy"
    - aws iam update-account-password-policy --minimum-password-length 24 --require-numbers --require-uppercase-characters --require-lowercase-characters --require-symbols --max-password-age 90 --password-reuse-prevention 12 --hard-expiry
```

## Step 3: Launch separate shell scripts in CodeBuild project <a id="step-3"></a>

When multiple shell commands are needed for the preparation of an account, you can load them from a git repository or from a S3 bucket before they are executed. Git is available by default in any CodeBuild project.

The example below is extracted from `fixtures/buildspec/prepare-account-from-git.yaml`. It shows how script files are loaded from a public git repository during the `install` phase of the CodeBuild project.

```yaml
version: 0.2

env:
  variables:

    # fetch git code
    CODE_GIT_URL: "https://github.com/reply-fr/sustainable-personal-accounts.git"
    CODE_GIT_BRANCH: "main"

    # for fixtures/scripts/set-budget-alert.sh
    ALERT_THRESHOLD: 80 # percentage of budget
    BUDGET_AMOUNT: 500.0
    BUDGET_EMAIL: a@b.com
    BUDGET_NAME: SPA-budget
    ENVIRONMENT_IDENTIFIER: None
    EVENT_BUS_ARN: None
    TOPIC_ARN: None

    # for fixtures/scripts/schedule-start-stop-ec2-instances.sh
    WITH_START_STOP_EC2_INSTANCES: disabled
    CLOUD_CUSTODIAN_ROLE: rolePlaceholder
    START_CRON_EXPRESSION: "0 5 ? * MON-FRI *"
    STOP_CRON_EXPRESSION: "0 21 ? * MON-FRI *"
    TAG_WITHOUT_START_STOP: "tagKeyPlaceholder"

    # for fixtures/scripts/run-prowler.sh
    WITH_PROWLER: disabled

phases:
  install:
    commands:
    - |
      echo "Fetching public code base..."
      git clone --depth 1 -b ${CODE_GIT_BRANCH} ${CODE_GIT_URL} code

    - |
      echo "Using public scripts..."
      cd code/fixtures/scripts
      ls -al

  pre_build:
    commands:
    - ACCOUNT=$(aws sts get-caller-identity --query Account --output text)

  build:
    commands:
    - sh ./set-budget-alert.sh
    - sh ./schedule-start-stop-ec2-instances.sh
    - sh ./run-prowler.sh
```

You can write your own shell scripts and use them as execution cartridges. The execution can be triggered on some accounts, and not on others, with feature flags set as environment variables. For example, the variable `WITH_PROWLER` has to be set to `enabled` for prowler to be actually executed. This is visible in the file `fixtures/scripts/run-prowler.sh` that is reproduced below,

```shell
#!/bin/sh

[[ "${WITH_PROWLER}" = "enabled" ]] || exit 0

echo "Running prowler..."

echo "Installing prowler..."
pip install prowler

echo "Scanning this account..."
prowler
exit 0
```

The variable `WITH_PROWLER` may be set to `enabled` is the settings of SPA, maybe for some accounts only, or for some OUs. This is how you manage its execution on some accounts, and not on others.