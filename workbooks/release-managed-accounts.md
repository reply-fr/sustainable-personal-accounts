# Release Managed Accounts

## Overview
During normal operations of SPA, accounts are in state `released` most of the time. On each maintenance window, each account transitions to states `expired`, then `assigned`, `prepared` and `released` again. From time to time, you may experience situations where the cycle does not complete as expected. This can be due to some transient conditions of the cloud infrastructure, or from some misconfiguration, or from a bug in the software itself. As stated from Werner Vogels, the CTO of Amazon: "everything fails, all the time".

In other terms, since SPA features an event-driven architecture, it breaks when transitions are not processed as expected. Accounts that are not in state `released` are invisible to the maintenance windows of SPA. In such situations, accounts stay in transient state without additional processing.

Since the state of an account is contained in a tag attached to it, for such situations you can use AWS Organizations to change the state of any account. For this you would visit the page of each account and then change the tag `account-state` to the value `released`. This operation is feasible for some dozens of accounts, but can become tedious for large number of accounts. Therefore the need to reset accounts to the state released with a simple invocation of a Lambda function devoted to this usage. If you are stuck, one day, with hundreds of AWS accounts in strange state, then you can restore normal operations with this workbook.

## Pre-conditions
- You suspect that multiple AWS accounts are not in RELEASED state
- You have AWS credentials to access the AWS account where SPA has been deployed

## Step 1 - Go to the Lambda console where SPA has been deployed

For this step you have to do the following:
- From the AWS Console of the `Automation` account, select Lambda service
- Check that you are connected to the AWS region where SPA has been deployed

## Step 2 - Launch the Lambda function that checks AWS accounts

In this step you launch a Lambda function to list all managed accounts and to spot accounts with anomalies:
- In the list of Lambda functions, select the function `SpaCheckAccounts`. If you can't find it, maybe you have deployed SPA with a different environment identifier, e.g. `MyCustomCheckAccounts`.
- Click on the `Test` button to launch the function manually. There is no need to provide specific input data, the function will not use it.
- The time needed to execute is linearly proportional to the number of accounts that is managed by SPA. As a baseline, expect one minute for 100 accounts.
- Look at the execution log provided by Lambda.

If no transient state is reported, or if no specific message is displayed, then all accounts are in RELEASED mode. There is no need to go further and you can stop this workbook there. Else move to the next step.

## Step 3 - Launch the Lambda function that releases AWS accounts

In this step you launch a Lambda function that tags every account with state RELEASED:
- In the list of Lambda functions, select the function `SpaReleaseAccounts`. If you can't find it, maybe you have deployed SPA with a different environment identifier, e.g. `MyCustomReleaseAccounts`.
- Click on the `Test` button to launch the function manually. There is no need to provide specific input data, the function will not use it.
- The time needed to execute is linearly proportional to the number of accounts that is managed by SPA. As a baseline, expect one minute for 100 accounts.
- Look at the execution log provided by Lambda.

The function will skip inactive AWS accounts, and it ignores AWS accounts that are already in RELEASED state. All other accounts are tagged as RELEASED.
You can review the log and ensure that no error happens during this execution.

## Step 4 - Launch the Lambda function that checks AWS accounts (Optional)

After the previous step, all accounts are back to the normal state of operations, and will be handled during next maintenance window. If you want extra assurance about the state of accounts managed by SPA, then you can launch again the Lambda function that cheks all accounts:
- In the list of Lambda functions, select the function `SpaCheckAccounts`. If you can't find it, maybe you have deployed SPA with a different environment identifier, e.g. `MyCustomCheckAccounts`.
- Click on the `Test` button to launch the function manually. There is no need to provide specific input data, the function will not use it.
- The time needed to execute is linearly proportional to the number of accounts that is managed by SPA. As a baseline, expect one minute for 100 accounts.
- Look at the execution log provided by Lambda.


