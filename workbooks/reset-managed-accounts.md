# Reset Managed Accounts

## Overview
Sometimes SPA is deployed after the creation of accounts that it manages. These accounts are missing the tag `account-state` that is needed for proper operations of the state machine. As a consequence, these accounts are not prepared as expected before they are accessed by end-users.

Another use case for account reset is when the state machine is broken during a major change of SPA itself. This can also happen if you change the tag prefix in the settings file and redeploy SPA. In both situations, accounts will not feature the expected tags.

Since the state of an account is contained in a tag attached to it, for such situations you can use AWS Organizations to change tags of any account. For this you would visit the page of each account and then add the tag `account-state` and set it to value `vanilla`. This operation is feasible for some dozens of accounts, but can become tedious for large number of accounts. Therefore the need to reset accounts to the VANILLA state with a simple invocation of a Lambda function devoted to this usage. If you are stuck, one day, with hundreds of AWS accounts in strange state, then you can restore normal operations with this workbook.

1. [Go to the Lambda console where SPA has been deployed](#step-1)
2. [Launch the Lambda function that checks AWS accounts](#step-2)
3. [Launch the Lambda function that reset AWS accounts](#step-3)
4. [Launch the Lambda function that checks AWS accounts (Optional)](#step-4)

## Prerequisites
- You suspect that multiple AWS accounts are not tagged appropriately
- You have AWS credentials to access the AWS account where SPA has been deployed

## Step 1 - Go to the Lambda console where SPA has been deployed <a id="step-1"></a>

For this step you have to do the following:
- From the AWS Console of the `Automation` account, select Lambda service
- Check that you are connected to the AWS region where SPA has been deployed

## Step 2 - Launch the Lambda function that checks AWS accounts <a id="step-2"></a>

In this step you launch a Lambda function to list all managed accounts and to spot accounts with anomalies:
- In the list of Lambda functions, select the function `SpaCheckAccounts`. If you can't find it, maybe you have deployed SPA with a different environment identifier, e.g. `MyCustomCheckAccounts`.
- Click on the `Test` button to launch the function manually. There is no need to provide specific input data, the function will not use it.
- The time needed to execute is linearly proportional to the number of accounts that is managed by SPA. As a baseline, expect one minute for 100 accounts.
- Look at the execution log provided by Lambda.

If no transient state is reported, or if no specific message is displayed, then all accounts are in RELEASED mode. There is no need to go further and you can stop this workbook there. Else move to the next step.

## Step 3 - Launch the Lambda function that reset AWS accounts <a id="step-3"></a>

In this step you launch a Lambda function that tags every account with state RELEASED:
- In the list of Lambda functions, select the function `SpaResetAccounts`. If you can't find it, maybe you have deployed SPA with a different environment identifier, e.g. `MyCustomResetAccounts`.
- Click on the `Test` button to launch the function manually. There is no need to provide specific input data, the function will not use it.
- The time needed to execute is linearly proportional to the number of accounts that is managed by SPA. As a baseline, expect one minute for 100 accounts.
- Look at the execution log provided by Lambda.

The function will skip inactive AWS accounts, and it ignores AWS accounts that are already in VANILLA state. All other accounts are tagged as RELEASED.
You can review the log and ensure that no error happens during this execution.

## Step 4 - Launch the Lambda function that checks AWS accounts (Optional) <a id="step-4"></a>

After the previous step, all accounts are back to the normal state of operations, and are prepared immediately. If you want extra assurance about the state of accounts managed by SPA, then you can launch again the Lambda function that cheks all accounts:
- In the list of Lambda functions, select the function `SpaCheckAccounts`. If you can't find it, maybe you have deployed SPA with a different environment identifier, e.g. `MyCustomCheckAccounts`.
- Click on the `Test` button to launch the function manually. There is no need to provide specific input data, the function will not use it.
- The time needed to execute is linearly proportional to the number of accounts that is managed by SPA. As a baseline, expect one minute for 100 accounts.
- Look at the execution log provided by Lambda.


