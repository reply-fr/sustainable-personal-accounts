# Manage Continuous Deployment

:construction: early work

## Overview
With this workbook you can automate the update of a SPA environment. This way of working is well-adapted to corporate environments where a team is responsible collectively for the target configuration and for the system updates.

1. [Understand continuous deployment of SPA](#step-1)
2. [Deploy a private repository on CodeCommit](#step-2)
3. [Deploy a pipeline to update your SPA environment](#step-3)
4. [Hook the pipeline into the private repository](#step-4)

## Prerequisites
- You have credentials to access the AWS Console
- You have received permissions to handle permissions across the AWS organizations

## Step 1 - Understand continuous deployment of SPA <a id="step-1"></a>

Here we put in place a GitOps approach for the build and for the updated of an SPA environment. This is meaning that both the code and its configuration are managed via git collaboration.

![Continuous deployment of SPA](./medias/continuous-deployment.png)

1. The code base of SPA is open source, and made available from GitHub. You do not want to update your SPA production environment on every update of this code base. Instead, you want to set explicitly which tag or commit you are using.

2. The exact configuration of your SPA environment is maintained as a private git repository on CodeCommit. Here the CloudOps team can set settings files, describe tag accounts, add full list of accounts as CSV files. They can also code customized `buildspec` files for the preparation or for the purge of accounts, or both. Each update of this repository induces an update of the SPA environment.

3. When an update is triggered, a specific CodeBuild project is executed in a separate account, named DevOps. This fetches the right version of SPA from GitHub, then combines it with the most recent version of the settings from private git repository. Then is runs tests before it builds or updates the target SPA environment.

4. Since it has a serverless architecture, the target SPA environment is built or updated one component at a time.


## Step 2 - Deploy a private repository on CodeCommit <a id="step-2"></a>

:construction: need content here

## Step 3 - Deploy a pipeline to update your SPA environment <a id="step-3"></a>

:construction: need content here

## Step 4 - Hook the pipeline into the private repository <a id="step-4"></a>

:construction: need content here
