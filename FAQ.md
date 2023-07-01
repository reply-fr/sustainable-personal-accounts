# Frequently Asked Questions


## Q. What is Sustainable Personal Accounts (SPA)?

Sustainable Personal Accounts automates operations on AWS accounts assigned to individual employees. Sustainable Personal Accounts is a serverless solution written in python and powered by Lambda, CodeBuild, EventBridge. Sustainable Personal Accounts is deployed and configured with YAML and CSV files, using CDK.

## Q. What can you do with SPA?

As a CTO/CCoE Leader/R&D Director:
- I recognize that innovative companies distribute sandbox AWS accounts to their staff
- I provide AWS accounts to cloud practitioners of my enterprise
- I manage these corporate resources at scale with SPA

As a person who benefits from a personal AWS account:
- After authentication, I connect to my account with `AWSAdministratorAccess` permission,
- A budget is set automatically to alert me by email,
- Cloudbuild projects are executed on my behalf for purging cloud resources and for alignment with corporate policies.

As a DevOps in charge of SPA deployment:
- I drive the behavior of SPA from a single YAML file with all settings,
- I can select when maintenance transactions are triggered,
- I can define settings for each organizational unit for easy scaling
- I can define settings for individual accounts for fine-grained tuning
- I can integrate tags from CSV files communicated by other teams (e.g., FinOps, Security, Enterprise Architecture)

As a DevOps in charge of account preparation:
- I can adjust the Codebuild project used for account preparation to evolving corporate policies
- I can prevent the execution of Codebuild preparation on selected accounts or organizational units
- I can inject different budgets and alerts across accounts or organizational units
- I can change the preparation script itself and customize it to the specific needs of my company
- I can integrate Codebuild variables from CSV files communicated by other teams (e.g., FinOps, Security, Enterprise Architecture)

As a DevOps in charge of the purge of cloud resources:
- I can adjust the Codebuild project used for account purge to evolving corporate policies
- I can prevent the execution of Codebuild purge on selected accounts or organizational units
- I foster partial purges that protects cloud resources from Control Tower
- I can select different maximum age of cloud resources accross accounts
- I can integrate Codebuild variables from CSV files communicated by other teams (e.g., FinOps, Security, Enterprise Architecture)

As a SRE in charge of SPA operations:
- I can manage preventive controls on personal accounts with SCP
- An automated CloudWatch dashboard covers technical and functional monitoring in one place
- Inventories of accounts are produced as CSV files in S3 bucket every week
- SPA activities, aka, console logins, account on-boarding, account maintenance, are reported as CSV files in S3 bucket every month
- FinOps reports are produced every month as CSV and Excel files in S3 bucket
- Management exceptions are managed interactively in Incident Manager
- Instant cost report is attached to incident records for contextual analysis

As a FinOps engineer:
- I receive cost reports every month in my mailbox
- The Excel report consolidates costs per cost center and per organizational unit for easy analysis
- The CSV report is processed with custom software for automated show-back and charge-back

## Q. How is this implemented?

SPA is featuring an event-driven architecture, and serverless infrastructure. Centralised lambda functions take care of changing states of accounts. The preparation of assigned accounts and the purge of expired accounts require heavy computing capabilities that are not compatible with Lambda. These activities run directly into target accounts as CodeBuild projects.

![architecture](./media/reference-architecture.svg)

Sustainable Personal Accounts has been designed with following principles:
- the entire solution is configured with one single YAML file
- the entire infrastructure is deployed with python code and AWS CDK
- the configuration of organizational units and accounts is store in SSM Parameter Store
- states of the state machine are implemented with tags on AWS accounts -- no database for state management
- computing resources are entirely serverless, powered by Lambda functions and CodeBuild projects
- processing is driven by events, powered by AWS EventBridge
- budget alerts are consolidated over SQS
- data persistence is provided with DynamoDB tables
- the preparation of an AWS account is done with a customizable Codebuild project -- adapt it to your corporate policy
- the purge of an AWS account is done with a customisable Codebuild project -- adapt it to your FinOps best practices
- monitoring is implemented with a CloudWatch dashboard deployed automatically
- system can be extended to specific needs via custom event processing

## Q. What do you need to deploy SPA in your environment?

Mandatory requirements:
* SPA is leveraging AWS Organization for events management and for account management across AWS accounts. The deployment of AWS Organizations can be managed by Amazon Control Tower, but Amazon Control Tower itself is not mandatory.
* SPA should be deployed on a dedicated AWS account. This facilitates the management of permissions accross a large number of AWS accounts, and contributes to the separation of concerns.
* SPA needs an assume role with permissions on the AWS Organization
* SPA needs an assume role with permissions within each AWS account that it manages

We recommend to deploy Amazon Control Tower and to benefit from cloud automation at scale on top of AWS Organizations, of AWS Service Catalog and of AWS IAM Identity Center (successor to AWS SSO).

## Q. What are account states managed by SPA?

Since we want to clean AWS accounts assigned to individuals, this can be represented as a state machine with following states and transitions.

<!--- you can use mermaid live with following link, and then save in ./media

      https://mermaid.live/edit#eyJjb2RlIjoiZ3JhcGggTFJcbiAgICBBKFZhbmlsbGEgQWNjb3VudHMpIC0tPiBCXG4gICAgQihBc3NpZ25lZCBBY2NvdW50cykgLS0-IENcbiAgICBDKFJlbGVhc2VkIEFjY291bnRzKSAtLT4gRFxuICAgIEQoRXhwaXJlZCBBY2NvdW50cykgLS0-IEJcbiIsIm1lcm1haWQiOiJ7XG4gIFwidGhlbWVcIjogXCJkYXJrXCJcbn0iLCJ1cGRhdGVFZGl0b3IiOnRydWUsImF1dG9TeW5jIjp0cnVlLCJ1cGRhdGVEaWFncmFtIjp0cnVlfQ

--->

![state machine](./media/state-machine.png)

- **Vanilla Accounts** - When an account has just been created by Control Tower, ServiceNow, or by any other mean, it is linked to a specific identity, e.g., `john.foo@example.com`. Note that Control Tower does a pretty good job to create an identity in AWS Single Sign-On (SSO) before creating a new account. For accounts in this state, the most important activity is to add tags to the account itself. Then the tagged account can be moved to the next state.

- **Assigned Accounts** - When an account has been formally linked to some identity with tags, it is considered assigned to a person. For accounts in this state, there is a need to enforce corporate policies by adjusting resources and by creating specific roles and policies in the account itself. This process can take minutes or even hours. Once it has been properly prepared, the assigned account can be moved to the next state.

- **Released Accounts** - This is the state where an account can be used almost freely by the person assigned to it. Guardrails can include: Service Control Policies (SCP) assigned to the Organisational Unit (OU) where the account is sitting, AWS CloudTrail for traceability, IAM policies to provide observability to third-party tools, Billing monitoring and alerting. Released Accounts can stay in this state as long as determined by corporate policy, but there is a need to set a limit anyway. We recommend to expire accounts at least once per month, since this preserves cloud resources for weeks, while providing a monthly window to roll out updated corporate policies or new guardrails and blueprints across personal accounts. Enterprises with strong Continuous Integration (CI) practice should adopt weekly expirations at least, or, if possible, daily expirations.

- **Expired Accounts** - Released Accounts are expired at regular intervals (e.g., daily, weekly, or monthly). Activities on expired accounts consist of systematic deletion of resources. Some resources may be preserved though the process, either because they have been tagged for explicit deadline at a later date, or because they cannot be created again (e.g., CloudFormation stacks created by Control Tower). Once accounts have been purged, they can be moved to Assigned Accounts for a new cycle.


Note that the scope of SPA is limited to the effective part of AWS accounts life cycle. Since the creation and the deletion of accounts are not specified, there are multiple options available for actual implementation. If SPA is deployed within an environment managed by Control Tower, then you can benefit from the account factory and other tools exposed to you. For other environments, it is up to you to create new accounts and to delete them when appropriate.


### Q. Can I use SPA for temporary accounts?

No. If you are looking for a vending machine of temporary accounts, then you can consider following solutions or similar:
- [AWS Samples - Sandbox Accounts for Events](https://github.com/awslabs/sandbox-accounts-for-events)
- [Disposable Cloud Environment (DCE)](https://dce.readthedocs.io/en/latest/index.html)
- [superwerker - automated best practices for AWS](https://github.com/superwerker/superwerker)

### Q. Can I use this software for my company?

Yes. Sustainable Personal Account is copyright from [Reply](http://www.reply.com) and licensed with [Apache License Version 2.0](./LICENSE)

Copyright 2023 Reply.com

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

### Q. How many accounts can be managed in a single SPA state machine?

Enterprise accounts may have thousands of software engineers. Purpose of the SPA is that each of them can get access to a personal AWS account to foster innovation and agility. Today the solution can accomodate for 100 AWS accounts or more. Our long-term objective is that up to 10,000 AWS accounts are purged and prepared on a weekly basis. In addition, the design of the system is as simple as possible, so that it should be convenient even for a single team of some developers.

### Q. How are transitions detected and managed?

When an AWS account is created into an Organisation Unit, or moved to an OU, this is detected as an event originated by AWS Organizations, and forwarded to an Amazon EventBridge bus. Similarly, when some AWS account is tagged, this is detected by AWS Organizations and forwarded to an event bus. From there, multiple rules and subscribers can be activated to handle each event appropriately.

In addition, events generated by the code of Sustainable Personal Account itself are also emitted on the same bus. Generally speaking, we compensate the fragmentation of code by centralising events into a single event bus for the entire system.

### Q. How are preparation and purge activities handled in the system?

CodeBuild has been selected for heavy processing of personal AWS accounts. CodeBuild matches all requirements that we could think about:

- it is a serverless and VPC-less service
- execution limit is 8 hours
- you pay for actual processing time, but no more
- it embeds a shell and allow for straightforward execution of AWS CLI, of python code and of AWS-Nuke
- buildspec structure is easy to manage in version control

Options that may be considered include at least Lambda, ECS, Automation and CodeBuild. Lambda is not adapted because execution is limited to 15 minutes, which is not enough for the provisioning or the destruction of complex resources such as Active Directory, FSx for Windows volume, etc. ECS does not have timing limitations, but it requires some VPC context that, strictly speaking, we do not need at all. SSM Automation is a powerful and VPC-less construct that can do almost anything. However, it is more designed to orchestrate code execution than to implement it. For example, SSM Automation can run python scripts but they are limited to a maximum duration of 10 minutes, which is not enough for our use case. At the end of the day, CodeBuild is a great candidate to automate preparation and purge activities within each account.

Credit:
- (1Strategy blog) [Automated Clean-up with AWS-Nuke in Multiple Accounts](https://www.1strategy.com/blog/2019/07/16/automated-clean-up-with-aws-nuke-in-multiple-accounts/)
- (AWS blog) [Using AWS CodeBuild to execute administrative tasks](https://aws.amazon.com/blogs/devops/using-aws-codebuild-to-execute-administrative-tasks/)

### Q. Can you list components of the SPA architecture?

Sure. Sustainable Personal Accounts features following building blocks:

- **The Organisation** - This is the specific instance of AWS Organisation that is hosting  all personal accounts managed by SPA. We recommend to land SPA into an organisation deployed by AWS Control Tower, so as to benefit from integrated SSO.

- **Vanilla Accounts**, **Assigned Accounts**, **Released Accounts** and **Expired Accounts** - These are the managed with tags attached to AWS accounts. Tag key is `account-state` and possible values are `vanilla`, `assigned`, `released` and `expired`.

- **Personal AWS accounts** - In settings files you list the Organizational Units and the accounts that SPA has to manage. If you list some Organizational Unit, all accounts that they contain are managed by SPA. Accounts that are not in scope of SPA are ignored.

- **Automation account** - This is the AWS account that hosts centralised SPA resources such as EventBridge event bus and Lambda functions. In the context of Control Tower, we recommend to place this account in the Sandbox OU. For example, you can rename the Sandbox AWS account created by Control Tower to Automation.

- **Automation region** - This is the selected AWS region to deploy EventBridge resources, Lambda functions, CodeBuild projects, and SSM Parameter Store.

- **Event bus** - This is the default EventBridge bus of the Automation Account. It is the single place to observe the entire system. Subscribing to events is a natural option for the extension and for the customisation of SPA.

- **OnVanillaAccount**, **OnAssignedAccount**, **OnPreparedAccount**, **OnReleasedAccounts**, **OnExpiredAccount** and **OnPurgedAccount** - Each Lambda function is triggered by some EventBridge rule.

- **PrepareAccount** and **PurgeAccount** - These templated CodeBuild projects are actually deployed in personal accounts, and started asynchronously, by Lambda functions **OnAssignedAccount** and **OnExpiredAccount**.

- **Parameter store** - Parameters used by SPA code, including templates for CodeBuild projects, are placed in SSM Parameter Store of the Automation account.

- **DynamoDB tables** - SPA is using several tables to persist data such as account transactions, purge logs, activity records.

- **Reporting S3 bucket** - SPA generates reports such as cost and usage reports, activity reports and account inventories.

- **Incident Manager** - SPA turns exceptions into incident records in SSM Incident Manager

### Q. What are the guiding principles for Sustainable Personal Accounts?

**We drive innovation by experimentations** - Professionals who can access the AWS console, APIs or SDK have a strong advantage to build systems out of available software and data constructs, and to prove the business opportunity or to fail fast. Large enterprises are advised to connect thousands of employees to AWS native capabilities so as to foster innovation at scale. A key performance indicator is the number of AWS accounts assigned to individuals across the corporation.

**We trust our employees and colleagues** - In most cases, temporary resources used on cloud infrastructure for some experimentation will require a very limited budget, and will stay isolated from corporate mainstream systems. This is creating an opportunity for a distinct responsibility models, where controls that are traditionally used for production and for large systems are relaxed on personal cloud accounts. For each personal cloud account, a monthly budget can be consumed without additional financial control. A key performance indicator is the number of personal cloud accounts that go above budget and that deserve specific scrutiny and corrective action.

**We influence corporate culture with recycling** - While production information systems have life cycles of multiple years, experimental information systems may be deployed for some hours only. Performing enterprises do clear cloud personal accounts used by their software engineers and data engineers for experiments and for labs. This is leading employees towards Continuous Integration (CI) practice in their day to day activities, that is foundational for sustainable agility. Business stakeholders can set the recycling horizon as a corporate policy. We recommend to start with monthly clearing of personal cloud accounts, and then move progressively towards weekly or even daily expirations. One key performance indicator is the cost saving incurred by deleted cloud resources on recycle. Another key performance indicator is the level of activity around git repositories initiated by individual persons.

**We scale with automated guardrails and with insourced blueprints** - Jeff Bezos has a saying: “Good intentions don't work. Mechanisms do.” In the context of this project, guardrails mean that corporate policies should apply automatically to personal cloud accounts. In addition, these accounts are recycled periodically. These cycles are giving security teams periodic opportunities to update security controls and, therefore, to adapt continuously to cyber-threats. On the other hand, the tooling provided to employees working on the cloud is specific to each enterprise. Also, this tooling is evolving over time. In the context of this project, we provide complete freedom regarding the execution of custom software on each personal cloud account. In addition, with periodic recycling of these accounts there is an opportunity to continuously update the toolbox provided to employees.

### Q. Can I get a presentation of this project and of the architecture?

Yes. An interactive presentation of Sustainable Personal Accounts is included with this repository.
You may have to install the MARP toolbox if this not available at your workstation.

```
$ make setup
```

The setup has to be done only once. Then, depending of your goals, use one command among following options. Type this command to start an interactive presentation of the overview slides:
```
$ make presentation
```

Type following command to produce a PDF file of the overview slides. This is useful to share reference file with your audience:
```
$ make pdf
```

If you do need to export overview slides, then following will produce a file that can be loaded and edited in Microsoft Powerpoint, in Apple Keynote or in LibreOffice:
```
$ make pptx
```

### Q. How to run the presentation of project within Cloud9?

If you have access to the AWS Console, then you are encouraged to work within a Cloud9 environment for this project. Here are the steps to upload and run the presentation:
- Got to AWS Cloud9 Console
- Create a new Cloud9 environment for yourself
- Open the Cloud9 environment
- From the menu bar, click on Files and then on Upload Local Files...
- Select the zip file of this project (possibly, compressed from your local workstation)
- In the terminal window, unzip the file
- Go into the project directory and run command `$ make setup` - this will install MARP CLI
- From the menu bar, select Run, then Run Configurations, then new Run Configuration - this will open a new panel
- In the new panel at the bottom of the screen, click on CWD and select the directory of the project
- In the Command placeholder, type `make serve` and hit enter - this will start web server
- In the menu bar, select Preview, then Preview Running Application - this will open a new panel
- In the preview panel, click on the icon to expand it to a separate tab of your browser
- Click on PITCHME.html file to navigate the presentation - make it full screen

