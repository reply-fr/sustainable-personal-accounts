---
title: Login in AWS CLI
permalink: /login-in-aws-cli.md
tags: ["assets", "settings"]
---
# Login in AWS CLI

## Overview
This workbook is for consultants who connect to AWS from the command line, typically in Cloud9 terminal or in a Terminal window. It allows consultants to assume a role instead of relying on some IAM user.

## Pre-conditions
* AWS CLI has been installed

## Steps

### Step 1 - check who you are
From the prompt, launch AWS CLI command to validate who you are.

```
$ aws sts get-caller-identity
```

If you cannot be authenticated for some reason, you will receive an error message like the following one:

```
$ aws sts get-caller-identity
Error loading SSO Token: The SSO access token has either expired or is otherwise invalid.
```

### Step 2 - name a new AWS profile
If you want to connect to your personal AWS account, funded by Storm Reply, then we recommend to name the profile like the following: `reply-x.yyyyy`, where `x` is first letter or your first name, and `yyyyy` is your last name. For example, my personal profile at Storm Reply is `reply-b.paques`.

### Step 3 - set an environment variable with the profile to use
You can set the profile to use at every AWS CLI command with suffix `--profile reply.x.yyyyy` or, if you are working in sessions, set the environment variable `AWS_PROFILE`.

For example, on Windows:
```
> setx AWS_PROFILE reply-b.paques
```

On macOS and Linux:
```
$ export AWS_PROFILE=reply-b.paques
```

### Step 4 - configure AWS CLI for your profile

Go to your home directory and create (or update) the file `.aws/config`. You can add a new section for your profile, that is mentioning the preferred region to work in, and the AWS Account Id as well. Below is an example that you can use:

```
[profile reply-b.paques]
region = eu-west-1
output = json
sso_start_url = https://d-93670bd35a.awsapps.com/start/
sso_region = eu-west-1
sso_account_id = 123456789012
sso_role_name = AWSAdministratorAccess
```

You can find the target AWS Account Id from the AWS Console once you have authenticated. of course, your personal AWS account is different from AWS accounts used by your colleagues.

Note that SSO region must be `eu-west-1`. However, the `region` keyword is the default region to use, and you can change it anytime by setting the environment variable `AWS_DEFAULT_REGION`.

Note also that the SSO Role Name must be `AWSAdministratorAccess` if you are accessing your personal AWS account, so that you can maximize capabilities made available to you.

Once you are done, save the new version of `.aws/config` and go back to the command line prompt.

### Step 5 - authenticate from the command line

When you start a new session of AWS commands from the command line, either directly, or via any tool such as CAWS CDK, you have to login first:

```
$ aws sso login
```

You will switch to a browser window so that you can authenticate in AWS SSO, receive temporary credentials and set them in your environment.

Once this is done, you can use any AWS command for the duration of the temporary credentials. For example, to check who you are:

```
$ aws sts get-caller-identity
{
    "UserId": "ABCAVYNQ8TM5JVS26EIHT:b.paques@reply.com",
    "Account": "123456789012",
    "Arn": "arn:aws:sts::123456789012:assumed-role/AWSReservedSSO_AWSAdministratorAccess_d7c68c853542af3c/b.paques@reply.com"
}
```

Most of the time you will just let the temporary creden tials expire. In case you would like to logout explicitly, you can do that from the command line as well:

```
$ aws sso logout
$ aws sts get-caller-identity

Error loading SSO Token: The SSO access token has either expired or is otherwise invalid.
```



## Post-conditions
