# Manage Continuous Deployment

:construction: early work

## Overview
With this workbook you can automate the update of a SPA environment. This way of working is well-adapted to corporate environments where a team is responsible collectively for the target configuration and for the system updates.

1. [Understand continuous deployment of SPA](#step-1)
2. [Segregate roles and responsibilities](#step-2)
3. [Deploy a private repository for CloudOps team](#step-3)
4. [Deploy a software pipeline for DevOps automation](#step-4)
5. [Hook the pipeline into the private repository](#step-5)

## Prerequisites
- You have credentials to access the AWS Console
- You have received permissions to handle permissions across the AWS organizations

## Step 1 - Understand continuous deployment of SPA <a id="step-1"></a>

Here we put in place a [GitOps](https://about.gitlab.com/topics/gitops/) approach for the build and for the update of an SPA environment. GitOps requires Infrastructure-as-Code, change management rooted in git, and software automation.

Our GitOps implementation for SPA has specific flavor:

- **Infrastructure-as-Code** - SPA features multiple Lambda functions, DynamoDB tables, a CloudWatch dashboard, one SSM Incident Manager response plan, etc. The code base leverages the Python language, including Infrastructure-as-Code with the AWS Cloud Development Kit (CDK). A convenient command `make deploy` is provided that deploys a ready-to-use SPA environment.

- **Change management rooted in git** - The deployment of SPA requires a public code base and private settings. Our focus here is on change management of private settings. This is implemented with a private CodeCommit repository and pull requests managed collectively by the CloudOps team.

- **Software automation** - The build and update of a SPA environment is a linear sequence of shell We put the software pipeline on a separate AWS account so that it cannot be confused with


In addition, our GitOps implementation spans multiple accounts and is deliberately embracing serverless products from AWS. The following diagram represents the overall GitOps architecture put in place for the SPA use case.

![Continuous deployment of SPA](./medias/continuous-deployment.png)

1. The code base of SPA is open source, and made available from GitHub. You do not want to update your SPA production environment on every update of this code base. Instead, you want to set explicitly which tag or commit you are using.

2. The exact configuration of your SPA environment is maintained as a private git repository on CodeCommit. Here the CloudOps team can set settings files, describe tag accounts, add full list of accounts as CSV files. They can also provide customized `buildspec` files and shell scripts for the preparation or for the purge of accounts, or both. Each update of the trunk branch induces an update of the SPA environment. Changes are managed with pull requests on branches contributed by team members. [CodeCommit supports pull requests](https://docs.aws.amazon.com/codecommit/latest/userguide/pull-requests.html) from the CodeCommit console, from the AWS CLI and from AWS SDKs. Private content is exposed to the DevOps account via a specific IAM role.

3. When an update is triggered, a specific CodeBuild project is executed in a separate account, named DevOps. This fetches the right version of SPA from GitHub, then combines it with the most recent version of the settings from private git repository. Then is runs tests before it builds or updates the target SPA environment.

4. Since it has a serverless architecture, the target SPA environment is built or updated one component at a time. The capability to act on this environment is granted to the DevOps account via a specific IAM role.


## Step 2 - Segregate roles and responsibilities <a id="step-2"></a>

The continuous deployment architecture is split across multiple AWS accounts, and this allows us to control tightly permissions given to each software entities involved in the process. The CodeBuild project has no specific super-power by itself. Instead, it gets explicit permissions by assuming roles from source and target AWS accounts.

More specifically, when the CodeBuild project is triggered on DevOps accounts, the following activities are performed successively:

1. **Fetch code from GitHub** - This is implemented with command `git clone` command. The command `make setup` is executed to download and install software dependencies. CodeBuild provides about 220 GiB of storage, so there is plenty of room for significant code base and dependencies.

2. **Assume role from CloudOps account and fetch configuration from CodeCommit repository there** - IAM permissions are handled with AWS CLI commands and local environment variables. The command `aws sts assume-role` gets a temporary token from the account CloudOps. This is turned to `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN` that, together, provide authentication context to the `git-remote-commit` package. Configuration files are fetched with command `git clone` performed over GRC protocol. Then the AWS environment variables are cleaned so the service role used by CodeBuild is restored. The configuration files are copied on the original code base.

3. **Test the code locally** - This is implemented with commands `make lint` and `make all-tests`. If one of these commands fail, then the process does not go further.

4. **Assume role from Automation account and apply changes there** - IAM permissions are handled again with AWS CLI commands and local environment variables. The command `aws sts assume-role` gets a temporary token from the account Automation. This is turned to `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN` that, together, provide authentication context to the next shell command: `make deploy`. This is what create or update the target SPA environment.


From a security perspective, we want

## Step 3 - Deploy a private repository for CloudOps team <a id="step-3"></a>

Activities to complete this step:
- Login to the AWS Console of the account `CloudOps`
- Go to the CodeCommit console in the selected region
- Create a new CodeCommit repository for the settings to manage
- Create a new role that can be

:construction: add a SCP to the CloudOps account to prevent the deletion of CodeCommit repositories

:construction: need content here

## Step 4 - Deploy a software pipeline for DevOps automation <a id="step-4"></a>

:construction: need content here

## Step 5 - Hook the pipeline into the private repository <a id="step-5"></a>

:construction: need content here
