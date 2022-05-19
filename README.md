# Sustainable Personal Accounts

With this project we promote the idea that each AWS practitioner should have direct access to some AWS account, so as to practice almost freely on the platform and to accelerate innovation of their company. At the same time, in corporate environment there is a need for enforcing policies, for managing costs and for fostering software automation. For this reason, with Sustainable Personal Accounts (SPA), AWS accounts are purged at regular intervals, and recycled.

Note that alternate projects are available if SPA does not suit your specific needs:
- [Disposable Cloud Environment (DCE)](https://dce.readthedocs.io/en/latest/index.html)
- [superwerker - automated best practices for AWS](https://github.com/superwerker/superwerker)

## SPA brings maintenance windows to AWS accounts

Since we want to purge and to reset accounts assigned to individuals, this can be represented as a state machine that features following states and transitions.

<!--- you can use mermaid live with following link, and then save in ./media

      https://mermaid.live/edit#eyJjb2RlIjoiZ3JhcGggTFJcbiAgICBBKFZhbmlsbGEgQWNjb3VudHMpIC0tPiBCXG4gICAgQihBc3NpZ25lZCBBY2NvdW50cykgLS0-IENcbiAgICBDKFJlbGVhc2VkIEFjY291bnRzKSAtLT4gRFxuICAgIEQoRXhwaXJlZCBBY2NvdW50cykgLS0-IEJcbiIsIm1lcm1haWQiOiJ7XG4gIFwidGhlbWVcIjogXCJkYXJrXCJcbn0iLCJ1cGRhdGVFZGl0b3IiOnRydWUsImF1dG9TeW5jIjp0cnVlLCJ1cGRhdGVEaWFncmFtIjp0cnVlfQ

--->

![state machine](./media/state-machine.png)

- **Vanilla Accounts** - When an account has just been created by Control Tower, ServiceNow, or by any other mean, it is linked to a specific identity. Note that Control Tower does a pretty good job to create an identity in AWS Single Sign-On (SSO) before creating a new account. For accounts in this state, the most important activity is to add tags to the account itself. Then the tagged account can be moved to the next state.

- **Assigned Accounts** - When an account has been formally linked to some identity with tags, it is considered assigned to a person. For accounts in this state, there is a need to enforce corporate policies by adjusting resources and by creating specific roles and policies in the account itself. This process can take minutes or even hours. Once it has been properly prepared, the assigned account can be moved to the next state.

- **Released Accounts** - This is the state where an account can be used almost freely by the person assigned to it. Guardrails can include: Service Control Policies (SCP) assigned to the Organisational Unit (OU) where the account is sitting, AWS CloudTrail for traceability, IAM policies to provide observability to third-party tools, Billing monitoring and alerting. Released Accounts can stay in this state as long as determined by corporate policy, but there is a need to set a limit anyway. We recommend to expire accounts at least once per month, since this preserves cloud resources for weeks, while providing a monthly window to roll out updated corporate policies or new guardrails and blueprints across personal accounts. Enterprises with strong Continuous Integration (CI) practice should adopt weekly expirations at least, or, if possible, daily expirations.

- **Expired Accounts** - Released Accounts are expired at regular intervals (e.g., daily, weekly, or monthly). Activities on expired accounts consist of systematic deletion of resources. Some resources may be preserved though the process, either because they have been tagged for explicit deadline at a later date, or because they cannot be created again (e.g., CloudFormation stacks created by Control Tower). Once accounts have been purged, they can be moved to Assigned Accounts for a new cycle.


Note that the scope of SPA is limited to the effective part of AWS accounts life cycle. Since the creation and the deletion of accounts are not specified, there are multiple options available for actual implementation. If SPA is deployed within an environment managed by Control Tower, then you can benefit from the account factory and other tools exposed to you. For other environments, it is up to you to create new accounts and to delete them when appropriate.

## Get started with Sustainable Personal Accounts

### Step 1 - Deploy AWS Control Tower

The best fit for Sustainable Personal Account is to add it to an AWS Organizations deployed as part of Control Tower.

Reference:
- [AWS Control Tower Workshops](https://controltower.aws-management.tools/)
- [AWS Control Tower Documentation](https://docs.aws.amazon.com/controltower/)

### Step 2 - Select an AWS account and a region to deploy Sustainable Personal Account

We recommend to rename the "Sandbox" account created by Control Tower to "Automation". This is leaving in the Sandbox Organizational Unit.

### Step 3 - Create Organizational Units for personal accounts

We recommend to create several OUs under the Sandbox Organizational Unit. Each OU can feature specific SCP and specific settings in SPA.

### Step 4 - Clone the SPA repository on your workstation

```
$ git clone git@github.com:reply-fr/sustainable-personal-accounts.git
$ cd sustainable-personal-accounts
$ make setup
```

### Step 5 - Configure SPA

You can duplicate the file `tests/settings/settings.yaml` to `settings.yaml` and reflect parameters for your own deployment.

### Step 6 - Deploy SPA

```
$ make deploy
```

### Step 7 - Inspect the solution

Use the AWS Console on the "Automation" account. There is a CloudWatch dashboard that reflects metrics for SPA. Code execution is reflected into the Lambda console.

## Frequently asked questions

In this question we address frequent questions about Sustainable Personal Accounts. We also explain most important design decisions on the architecture of the system.

### Q. Can I use this software for my company?

Yes. Sustainable Personal Account is copyright from [Reply](http://www.reply.com) and licensed with [Apache License Version 2.0](./LICENSE)

Copyright 2022 Reply.com

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

### Q. Can I get a presentation of this project and of the architecture?

Yes. A presentation of Sustainable Personal Accounts is provided with this repository.
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

### Q. How many accounts do we want to support in a single SPA state machine?

Enterprise accounts may have thousands of software engineers. Purpose of the SPA is that each of them can get access to a personal AWS account to foster innovation and agility. As a rule of thumb, the basic requirement is that up to 10,000 AWS accounts are purged and recycled on a weekly basis. In addition, the design of the system is as simple as possible, so that it should be convenient even for a single team of some developers.

### Q. How are transitions detected and managed?

When an AWS account is created into an Organisation Unit, or moved to an OU, this is detected as an event originated by AWS Organizations, and forwarded to an Amazon EventBridge bus. Similarly, when some AWS account is tagged, this is detected by AWS Organizations and forwarded to an event bus. From there, multiple rules and subscribers can be activated to handle each event appropriately.

In addition, events generated by the code of Sustainable Personal Account itself are also emitted on the same bus. Generally speaking, we compensate the fragmentation of code by centralising events into a single event bus for the entire system.

### Q. How are preparation and purge activities handled in the system?

We have selected CodeBuild for heavy processing of personal AWS accounts. CodeBuild matches all requirements that we could think about:

- it is a serverless and VPC-less service
- execution limit is 8 hours
- you pay for actual processing time, but no more
- it embeds a shell and allow for straightforward execution of AWS CLI, of python code and of AWS-Nuke
- buildspec structure is easy to manage in version control

Options that may be considered include at least Lambda, ECS, Automation and CodeBuild. Lambda is not adapted because execution is limited to 15 minutes, which is not enough for the provisioning or the destruction of complex resources such as Active Directory, FSx for Windows volume, etc. ECS does not have timing limitations, but it requires some VPC context that, strictly speaking, we do not need at all. SSM Automation is a powerful and VPC-less construct that can do almost anything. However, it is more designed to orchestrate code execution than to implement it. For example, SSM Automation can run python scripts but they are limited to a maximum duration of 10 minutes, which is not enough for our use case. At the end of the day, CodeBuild is a great candidate to automate preparation and purge activities within each account.

Note that CodeBuild can be expensive compared to other compute options. We recommend to stick to `arm1.small`compute instance type if possible.

Credit:
- (1Strategy blog) [Automated Clean-up with AWS-Nuke in Multiple Accounts](https://www.1strategy.com/blog/2019/07/16/automated-clean-up-with-aws-nuke-in-multiple-accounts/)
- (AWS blog) [Using AWS CodeBuild to execute administrative tasks](https://aws.amazon.com/blogs/devops/using-aws-codebuild-to-execute-administrative-tasks/)

### Q. Is this a centralised or a distributed architecture?

![architecture](./media/reference-architecture.svg)

SPA is featuring an event-driven architecture, and serverless infrastructure. By default, centralised lambda functions take care of changing states of accounts. However, the preparation of assigned accounts and the purge of expired accounts require heavy computing capabilities that are not compatible with Lambda. These specific activities can be either centralised in one AWS account, or distributed into the personal accounts themselves.

With centralised processing, you can deploy code only once and manage configuration files adapted to target accounts. Also, you need specific cross-account permissions to allow the creation and the destruction of resources from another account. With centralised processing, the scaling is limited by quotas related to underlying resources. For example, with CodeBuild there is a limit of 60 concurrent builds in one account, that would limit the number of accounts managed in SPA if CodeBuild projects were started into one centralised account.

With distributed processing, you have to deploy code within each target account and then execute it. You need cross-account permissions only to deploy code into target accounts. CodeBuild quota limits are not an issue anymore. Because of the scaling that it enables, and because of the reduced IAM permissions required, we prefer a distributed design for heavy processing.

At the end of the day, some parts of SPA are centralised, while other parts are distributed:

- A single AWS account is used for centralised automation, with one EventBridge bus, some Lambda functions and SSM Parameter store.

- Personal AWS accounts managed by SPA host heavy processing required for their preparation and for their purge.

### Q. Can you list the components of the SPA architecture?

Sure. Sustainable Personal Accounts features following building blocks:

- **The Organisation** - This is the specific instance of AWS Organisation that is hosting  all personal accounts managed by SPA. We recommend to land SPA into an organisation deployed by AWS Control Tower, so as to benefit from integrated SSO.

- **Vanilla Accounts**, **Assigned Accounts**, **Released Accounts** and **Expired Accounts** - These are the managed with tags attached to AWS accounts. Tag key is `account:state` and possible values are `vanilla`, `assigned`, `released` and `expired`.

- **Personal AWS accounts** - In the context of Control Tower, the creation of a personal account can be streamlined with the account factory in Service Catalog. Each account is tagged with the e-mail address of the person using it. In addition, each account handled with SPA can be put into one Organizational Unit under the Sandbox OU.

- **Automation account** - This is the AWS account that hosts centralised SPA resources such as EventBridge event bus and Lambda functions. In the context of Control Tower, we recommend to place this account in the Sandbox OU. For example, you can rename the Sandbox AWS account created by Control Tower to Automation and that's it.

- **Automation region** - This is the selected AWS region to deploy EventBridge resources, Lambda functions, CodeBuild projects, and SSM Parameter Store.

- **Event bus** - This is the default EventBridge bus of the Automation Account. It is the single place to observe the entire system. Subscribing to events is a natural option for the extension and for the customisation of SPA.

- **OnVanillaAccount**, **OnAssignedAccount**, **OnPreparedAccount**, **OnReleasedAccounts**, **OnExpiredAccount** and **OnPurgedAccount** - Each Lambda function is triggered by some EventBridge rule.

- **PrepareAccount** and **PurgeAccount** - These templated CodeBuild projects are actually deployed in personal accounts, and started asynchronously, by Lambda functions **OnAssignedAccount** and **OnExpiredAccount**.

- **Parameter store** - Parameters used by SPA code, including templates for CodeBuild projects, are placed in SSM Parameter Store of the Automation account.

### Q. What are the guiding principles for Sustainable Personal Accounts?

**We drive innovation by experimentations** - Professionals who can access the AWS console, APIs or SDK have a strong advantage to build systems out of available software and data constructs, and to prove the business opportunity or to fail fast. Large enterprises are advised to connect thousands of employees to AWS native capabilities so as to foster innovation at scale. A key performance indicator is the number of AWS accounts assigned to individuals across the corporation.

**We trust our employees and colleagues** - In most cases, temporary resources used on cloud infrastructure for some experimentation will require a very limited budget, and will stay isolated from corporate mainstream systems. This is creating an opportunity for a distinct responsibility models, where controls that are traditionally used for production and for large systems are relaxed on personal cloud accounts. For each personal cloud account, a monthly budget can be consumed without additional financial control. A key performance indicator is the number of personal cloud accounts that go above budget and that deserve specific scrutiny and corrective action.

**We influence corporate culture with recycling** - While production information systems have life cycles of multiple years, experimental information systems may be deployed for some hours only. Performing enterprises do clear cloud personal accounts used by their software engineers and data engineers for experiments and for labs. This is leading employees towards Continuous Integration (CI) practice in their day to day activities, that is foundational for sustainable agility. Business stakeholders can set the recycling horizon as a corporate policy. We recommend to start with monthly clearing of personal cloud accounts, and then move progressively towards weekly or even daily expirations. One key performance indicator is the cost saving incurred by deleted cloud resources on recycle. Another key performance indicator is the level of activity around git repositories initiated by individual persons.

**We scale with automated guardrails and with insourced blueprints** - Jeff Bezos has a saying: “Good intentions don't work. Mechanisms do.” In the context of this project, guardrails mean that corporate policies should apply automatically to personal cloud accounts. In addition, these accounts are recycled periodically. These cycles are giving security teams periodic opportunities to update security controls and, therefore, to adapt continuously to cyber-threats. On the other hand, the tooling provided to employees working on the cloud is specific to each enterprise. Also, this tooling is evolving over time. In the context of this project, we provide complete freedom regarding the execution of custom software on each personal cloud account. In addition, with periodic recycling of these accounts there is an opportunity to continuously update the toolbox provided to employees.
