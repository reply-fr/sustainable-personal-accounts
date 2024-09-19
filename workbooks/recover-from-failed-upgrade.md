# Recover from failed upgrade

:construction: this is early initial work, without complete instructions at this stage.

## Overview

Most of the time, you can upgrade SPA with a simple `make deploy` command. This is working great if you integrate changes brought by SPA progressively. However, if you cannot upgrade an existing SPA deployment via CDK, then you can consider a full deletion and replacement of SPA assets. This workbook explains how to pass through such an upgrade smoothly.

- [Understand the implications of SPA replacement](#step-1)
- [Backup content of the reporting S3 bucket](#step-2)
- [Snapshot content of DynamoDB tables](#step-3)
- [Delete the SPA stack](#step-4)
- [Deploy a new SPA stack](#step-5)
- [Restore content of the reporting S3 bucket](#step-6)
- [Restore content of DynamoDB tables](#step-7)

## Step 1: Understand the implications of SPA replacement <a id="step-1"></a>

- content of the DynamoDB will be deleted
- content of the S3 bucket will be deleted
- SNS topics will be destroyed
- CloudWatch metrics are not deleted

## Step 2: Backup content of the reporting S3 bucket <a id="step-2"></a>

## Step 3: Snapshot content of DynamoDB tables <a id="step-3"></a>

## Step 4: Delete the SPA stack <a id="step-4"></a>

## Step 5: Deploy a new SPA stack <a id="step-5"></a>

## Step 6: Restore content of the reporting S3 bucket <a id="step-6"></a>

## Step 7: Restore content of DynamoDB tables <a id="step-7"></a>

## Follow-up

- [Inspect the new SPA system](./inspect-a-production-system.md)
