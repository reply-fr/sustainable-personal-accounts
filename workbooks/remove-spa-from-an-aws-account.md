# Remove an account from SPA

# Understand cloud resources created by SPA in an account

The following table lists resources that can be created by SPA in an account that it manages.

| Service      | Name                                             | Note and comments |
|--------------|--------------------------------------------------|-------------------|
| CodeBuild    | `SpaProjectForAccountPreparation`                | The project that is ran for the periodic preparation of an AWS account |
| CodeBuild    | `SpaProjectForAccountPurge`                      | The project that is ran for the periodic preparation of an AWS account |
| EventBridge  | `SpaEventsRuleForCodebuild`                      | Centralize events related to the CodeBuild |
| EventBridge  | `SpaEventsRuleForConsoleLogin`                   | Centralize events related to console login |
| IAM          | `SpaRoleForServerlessComputing`                  | Role given to serverless computing services triggered by SPA: CodeBuild, ECS and Lambda |
| IAM          | `SpaRoleForEvents`                               | Role given to EventBridge service |
| IAM          | `SpaPermissionToPutEvents`                       | Custom policy attached to the role `SpaRoleForEvents` |
| SNS          | `SpaAlertTopic`                                  | Target SNS topic that can be used for budget alerts |
| SSM          | `SpaPurgeMessage`                                | An item in SSM Parameter Store that logs the last execution of the purge CodeBuild project - Depends on actual `buildspec` content |
| CloudWatch   | `/aws/codebuild/SpaProjectForAccountPreparation` | The CloudWatch log group used for the preparation CodeBuild project |
| CloudWatch   | `/aws/codebuild/SpaProjectForAccountPurge`       | The CloudWatch log group used for the purge CodeBuild project |
| Budgets      | `SpaBudget`                                      | The budget alert that is created and updated by SPA - Depends on actual `buildspec` content |
