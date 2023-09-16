# Manage account states

## Overview
With this workbook you will deep dive on account states and understand how they relate to tags attached to them. This will allow you to troubleshoot issues and to recover from failures.

1. [Inspect an account managed by SPA](#step-1)
2. [Start an on-boarding transaction manually](#step-2)
3. [Start a maintenance transaction manually](#step-3)
4. [Force an on-boarding transaction for all accounts](#step-4)
5. [Force a maintenance transaction for all accounts](#step-5)
6. [Release all accounts](#step-6)
7. [Get reports on account states](#step-7)

## Prerequisites
- You have credentials to access the AWS Console
- You have the permission to tag AWS accounts via the AWS Organization Console
- You have the permission to access the CloudWatch Console of the `Automation` account (where SPA has been deployed)

## Step 1. Inspect an account managed by SPA <a id="step-1"></a>

The state of an account is managed as a value of a tag of the account itself. Therefore, by inspecting any account of the AWS Organization you will immediately understand its state, and view the outcome of settings as well.

Complete following activities at this step:
- In a web browser, open the AWS Console of the management account of the AWS organization
- Go to the AWS Organizations Console
- Unfold Organization Units and navigate the organization to find the target account
- Click on an AWS account that is managed by SPA

Inspect the tags of the account. You should have typically:
- `account-state` - one of following values: `vanilla`, `assigned`, `released` and `expired`
- `account-holder` - the email address of the person assigned to this account
- `cost-center` - the label used for FinOps reporting
- `cost-owner` - the email address of the budget owner for costs incurred by this account

The two first tags, `account-state` and `account-holder` are set by SPA as part of state management. Other tags are set by SPA from the settings file. The keys `cost-center` and `cost-owner` are recommended, yet you can add your tags, that support your specific corporate policies.

If an account has no tag, or if it does not have the expected value for a tag, then there is an issue with SPA that you have to fix. The normal state for an AWS account that is managed by SPA is `released`. Any other value is either transient, or it is meaning that SPA is stuck.

## Step 2. Start an on-boarding transaction manually <a id="step-2"></a>

Sometimes the setup of SPA is not complete when a personal account is created. Or maybe you have changed settings and want to test the effect on one sample account before the addition of more accounts. In both situations you have to start manually an on-boarding transaction.

This step can be completed by setting the tag `account-state` to the value `vanilla`:
- From the detail page of the personal account in the AWS Organization Console, click on `Manage tags`
- If tag `account-state` is present, then change its value to `vanilla`
- Else add a tag, enter `account-state` as key and `vanilla` as value
- Click on button `Save changes`

This will create an event from AWS Organization that will be handled by the Lambda function `SpaOnVanillaAccountTag` in the account `Automation`. You can inspect the CloudWatch of this function to confirm adequate processing. If the CloudWatch log stays empty, then there is an issue in the forwarding of the event from AWS Organizations in `us-east-1`.

Then move to the AWS Console of the `Automation` account and check the log of the Lambda function `SpaOnAccountEvent`. You should get the full sequence of state changes over a couple of minutes: `CreatedAccount`, `AssignedAccount`, `PreparedAccount` then `ReleasedAccount`.

After this sequence, you can go to the AWS Console of the personal account and inspect the budget that has been set by SPA. In addition, you can also review the Codebuild project that has been executed by SPA during the preparation phase.

In the end, if you visit the page of the personal account in AWS Organization, then the value of the tag `account-state` should be `released`.

## Step 3. Start a maintenance transaction manually <a id="step-3"></a>

This is useful for example is you have changed the script of the purge and you want to test it on one account before the next maintenance cycle.

This step is similar to the previous one, except that you will set the tag `account-state` to the value `expired`:
- From the detail page of the personal account in the AWS Organization Console, click on `Manage tags`
- If tag `account-state` is present, then change its value to `expired`
- Else add a tag, enter `account-state` as key and `expired` as value
- Click on button `Save changes`

This will create an event from AWS Organization that will be handled by the Lambda function `SpaOnExpiredAccount` in the account `Automation`. You can inspect the CloudWatch of this function to confirm adequate processing. If the CloudWatch log stays empty, then there is an issue in the forwarding of the event from AWS Organizations in `us-east-1`.

Then move to the AWS Console of the `Automation` account and check the log of the Lambda function `SpaOnAccountEvent`. You should get the full sequence of state changes over a couple of minutes: `ExpiredAccount`, `PurgedAccount`, `AssignedAccount`, `PreparedAccount` then `ReleasedAccount`.

After this sequence, you can go to the AWS Console of the personal account and inspect the budget that has been set by SPA. In addition, you can also review the two Codebuild projects that have been executed by SPA during the purge phase and during the preparation phase.

In the end, if you visit the page of the personal account in AWS Organization, then the value of the tag `account-state` should be `released`.

## Step 4. Force an on-boarding transaction for all accounts <a id="step-4"></a>

Sometimes SPA is deployed after the creation of accounts that it manages. These accounts are missing the tag `account-state` that is needed for proper operations of the state machine. As a consequence, these accounts are not prepared as expected before they are accessed by end-users.

Another use case for account reset is when the state machine is broken during a major change of SPA itself. This can also happen if you change the tag prefix in the settings file and redeploy SPA. In both situations, accounts will not feature the expected tags.

You could change tags by yourself to fix such situations, but this is feasible only with few accounts. For large deployments, you can trigger manually the Lambda function `SpaResetAccounts` to tag all accounts at once with tag `account-state` and value `vanilla`.

Activities to on-board existing accounts that are managed by SPA:
- Move to the AWS Console of the `Automation` account
- Select the Lambda service
- Look for the Lambda function `SpaResetAccounts`
- Select the tab `Test`
- Click on the button `Test` to trigger the function and to tag managed accounts with tag `account-state` and value `vanilla`.

Learn more:
- Check the [reset managed accounts](./reset-managed-accounts.md) workbook

## Step 5. Force a maintenance transaction for all accounts <a id="step-5"></a>

SPA triggers maintenance transactions on schedule. But you may want to trigger an urgent purge for some reasons, for example after a major change of the buildspec used for the purge. In such situation you can invoke by yourself the function that expires all accounts. This will set tag `account-state` to the value `expired` and trigger the maintenance cycle.

Activities to start a maintenance window manually:
- Move to the AWS Console of the `Automation` account
- Select the Lambda service
- Look for the Lambda function `SpaOnMaintenanceWindow`
- Select the tab `Test`
- Click on the button `Test` to trigger the function and to tag managed accounts with tag `account-state` and value `expired`.

## Step 6. Release all accounts <a id="step-6"></a>

During normal operations of SPA, accounts are in state `released` most of the time. On each maintenance window, each account transitions to states `expired`, then `assigned`, `prepared` and `released` again. From time to time, you may experience situations where the cycle does not complete as expected. This can be due to some transient conditions of the cloud infrastructure, or from some misconfiguration, or from a bug in the software itself. As stated from Werner Vogels, the CTO of Amazon: "everything fails, all the time".

In other terms, since SPA features an event-driven architecture, it breaks when transitions are not processed as expected. Accounts that are not in state `released` are invisible to the maintenance windows of SPA. In such situations, accounts stay in transient state without additional processing.

You could change tags by yourself to fix such situations, but this is feasible only with few accounts. For large deployments, you can trigger manually the Lambda function `SpaReleaseAccounts` to tag all accounts at once with tag `account-state` and value `released`.

Activities to release accounts that are managed by SPA:
- Move to the AWS Console of the `Automation` account
- Select the Lambda service
- Look for the Lambda function `SpaReleaseAccounts`
- Select the tab `Test`
- Click on the button `Test` to trigger the function and to tag managed accounts with tag `account-state` and value `released`.

Learn more:
- Check the [release managed accounts](./release-managed-accounts.md) workbook

## Step 7. Get reports on account states <a id="step-7"></a>

Every week, SPA generates an inventory of accounts that it manages and saves this as a CSV file in the reporting S3 buckets. These reports feature a column `state` that reflects the value of the tag `account-state`. This can be useful for automated inspection of account states at regular intervals. From the S3 console of the `Automation` account, look for the bucket deployed by SPA, then navigate `SpaReports` and `Inventories`.

## Follow-up

If you experience issues with automated state transitions, then you may want to double-check the [full setup of SPA](./full-setup-of-spa.md).

