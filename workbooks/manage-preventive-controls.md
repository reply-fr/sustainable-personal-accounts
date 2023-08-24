# Manage preventive controls

## Overview
With this workbook you create effective guardrails and limits to what can be done within an AWS account assigned to a person.

1. [Create a service control policy](#step-1)
2. [Apply preventive controls at Organizational Unit level](#step-2)
3. [Prevent usage of account root user](#step-3)
4. [Prevent deployments anywhere](#step-4)
5. [Prevent the creation of costly resources](#step-5)
6. [Prevent long commitments](#step-6)
7. [Prevent resource sharing outside the organization](#step-7)


## Prerequisites
- You have a copy of the SPA git repository
- You have the permission to manage IAM policies of the management account of the AWS Organization
- You have the permission to configure Organizational Units of the AWS Organization

## Step 1 - Create a service control policy <a id="step-1"></a>

The preventive controls that we are looking for are specifically adapted to the use case of AWS accounts used by individual persons. As a starting point, we can copy the sample policy that is provided with SPA and deploy it. Later on, we will come back to this policy and tune it where necessary.

Complete following activities at this step:
- In a web browser, open the AWS Console of the management account of the AWS organization
- Go to the AWS Organizations Console
- In the left pane, select 'Policies'
- Click on `Service control policies'
- Click on the button 'Create policy'
- Give a memorable name to the policy, such as `SpaServiceControlPolicy`
- Enter a description, e.g., `Guardrails for personal accounts`
- Navigate the SPA git repository and look for the file `fixtures/policies/preventive_controls_for_sandboxes.json`
- Open the file and copy its content
- Switch to the web console, select the entire text of the policy, and paste the content
- Click on the bottom button 'Create policy'

## Step 2 - Apply preventive controls at Organizational Unit level <a id="step-2"></a>

Since personal accounts are put in specific Organizational Units of the AWS Organization, we will deploy preventive controls there. If all personal accounts are grouped into a single tree of Organizational Units, then focus on the top-level Organizational Unit of this tree. Preventive controls will be cascaded to child Organizational Units and to the AWS accounts that they contain.

This step can be completed with following activities:
- From within the AWS Organizations Console, click on 'AWS Accounts'
- Click on the Organizational Units that will contain personal accounts, for example, 'Sandboxes'
- Click on the tab 'Policies'
- Slide down to the section on Service control policies
- Click on the button 'Attach'
- In the following page, click the checkbox near the SCP that you created previously, e.g., `SpaServiceControlPolicy`
- Click on the button 'Attach policy'

## Step 3 - Prevent usage of account root user <a id="step-3"></a>

The normal usage of personal accounts is from Single Sign-On (SSO), controlled by corporate Identity provider. With this control we prevent actions that could be performed on direct authentication as an account root user.

This control is implemented in statement `SpaDenyEverythingFromRootUser`, that is looking like this:
```json
{
    "Sid": "SpaDenyEverythingFromRootUser",
    "Effect": "Deny",
    "Action": "*",
    "Resource": "*",
    "Condition": {
    "StringLike": {
        "aws:PrincipalArn": [
            "arn:aws:iam::*:root"
        ]
    }
    }
}
```

This control is also provided as [a standalone JSON file](https://github.com/reply-fr/sustainable-personal-accounts/blob/main/fixtures/policies/deny_everything_from_root_users.json) is you want to create a SCP that can apply to most of your AWS accounts.

If you need to perform a specific operation on an account that requires root authentication, then you have two options. First option: you can detach the SCP policy during the operation, then attach the SCP again. Second option: you move the account to another OU that does not feature the control on root account, perform the operation, then move the account back to its initial place.

## Step 4 - Prevent deployments anywhere <a id="step-4"></a>

The purge of personal accounts requires to visit multiple AWS regions. With this control we deny the creation of resources except on a limited set of well-defined regions. We also release the constraint for Control Tower itself, by checking the role that it is using across accounts.

This control is implemented in statement `SpaDenyAllOutsideRequestedRegions`, that is looking like this:
```json
{
    "Sid": "SpaDenyAllOutsideRequestedRegions",
    "Effect": "Deny",
    "NotAction": [
        "cloudfront:*",
        "iam:*",
        "route53:*",
        "support:*"
    ],
    "Resource": "*",
    "Condition": {
        "StringNotEquals": {
            "aws:RequestedRegion": [
                "ap-east-1",
                "eu-central-1",
                "eu-west-1",
                "eu-west-3",
                "us-east-1",
                "us-west-2"
            ]
        },
        "ArnNotLike": {
          "aws:PrincipalARN": "arn:aws:iam::*:role/AWSControlTowerExecution"
        }
      }
}
```

If you want to change the set of regions supported in personal accounts, edit the list using the regular names for AWS regions.

## Step 5 - Prevent the creation of costly resources <a id="step-5"></a>

While most AWS resources are inexpensive for short usage, the provisioning of some resources can induce costs of hundreds or thousands of dollars. With this control we deny the creation of such resources in personal accounts.

This control is implemented in statement `SpaDenyCreationOfCostlyResources`, that is looking like this:
```json
{
    "Sid": "SpaDenyCreationOfCostlyResources",
    "Effect": "Deny",
    "Action": [
        "acm-pca:CreateCertificateAuthority",
        "globalaccelerator:CreateAccelerator",
        "redshift:CreateCluster",
        "shield:CreateSubscription"
    ],
    "Resource": "*"
}
```

## Step 6 - Prevent long commitments <a id="step-6"></a>

Usually AWS resources are provisioned for short periods of time. However, some products and services can lead to commitments on months and years. With this control we deny the creation of such resources in personal accounts.

This control is implemented in statement `SpaDenyContractCommitments`, that is looking like this:
```json
{
    "Sid": "SpaDenyContractCommitments",
    "Effect": "Deny",
    "Action": [
        "ec2:AcceptReservedInstancesExchangeQuote",
        "ec2:CreateCapacityReservation",
        "ec2:CreateReservedInstancesListing",
        "ec2:PurchaseHostReservation",
        "ec2:PurchaseReservedInstancesOffering",
        "ec2:PurchaseScheduledInstances",
        "rds:PurchaseReservedDBInstancesOffering",
        "redshift:PurchaseReservedNodeOffering",
        "route53domains:RegisterDomain",
        "route53domains:TransferDomain",
        "s3:PutBucketObjectLockConfiguration",
        "s3:PutObjectLegalHold",
        "s3:PutObjectRetention",
        "savingsplans:*"
    ],
    "Resource": "*"
}
```

## Step 7 - Prevent resource sharing outside the organization <a id="step-7"></a>

The Resources Access Manager (RAM) is a fantastic capability to share selected AWS resources across accounts. With this control we deny the public sharing of resources a,d the sharing with AWS accounts that are not part of the same AWS organization of personal accounts.

This control is implemented in statement `SpaDenyResourceShareOutsideOrganization`, that is looking like this:
```json
{
    "Sid": "SpaDenyResourceShareOutsideOrganization",
    "Effect": "Deny",
    "Action": [
        "ram:CreateResourceShare",
        "ram:UpdateResourceShare"
    ],
    "Resource": "*",
    "Condition": {
        "Bool": {
            "ram:RequestedAllowsExternalPrincipals": "true"
        }
    }
}
```
