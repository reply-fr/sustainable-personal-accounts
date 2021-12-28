# Sustainable Personal Accounts

With this project we promote the idea that each AWS practitioner should have direct access to some AWS account, so as to practice almost freely on the platform and to accelerate innovation of their company. At the same time, in corporate environment there is a need enforcing policies, for managed costs and for fostering software automation. For this reason, with Sustainable Personal Accounts (SPA), AWS accounts are purged at regular intervals, and recycled.

## Guiding principles for sustainable personal accounts

**We drive innovation by experimentations** - Professionals who can access the AWS console, APIs or SDK have a strong advantage to build systems out of available software and data constructs, and to prove the business opportunity or to fail fast. Large enterprises are advised to connect thousands of employees to AWS native capabilities so as to foster innovation at scale. A key performance indicator is the number of AWS accounts assigned to individuals across the corporation.

**We trust our employees and colleagues** - In most cases, temporary resources used on cloud infrastructure for some experimentation will require a very limited budget, and will stay isolated from corporate mainstream systems. This is creating an opportunity for a distinct responsibility models, where controls that are traditionally used for production and for large systems are relaxed on personal cloud accounts. For each personal cloud account, a monthly budget can be consumed without additional financial control. A key performance indicator is the number of personal cloud accounts that go above budget and that deserve specific scrutiny and corrective action.

**We influence corporate culture with recycling** - While production information systems have life cycles of multiple years, experimental information systems may be deployed for some hours only. Performing enterprises do clear cloud personal accounts used by their software engineers and data engineers for experiments and for labs. This is leading employees towards Continuous Integration (CI) practice in their day to day activities, that is foundational for sustainable agility. Business stakeholders can set the recycling horizon as a corporate policy. We recommend to start with monthly clearing of personal cloud accounts, and then move progressively towards weekly or even daily expirations. One key performance indicator is the cost saving incurred by deleted cloud resources on recycle. Another key performance indicator is the level of activity around git repositories initiated by individual persons.

**We scale with automated guardrails and with insourced blueprints** - Jeff Bezos has a saying: “Good intentions don't work. Mechanisms do.” In the context of this project, guardrails mean that corporate policies should apply automatically to personal cloud accounts. In addition, these accounts are recycled periodically. These cycles are giving security teams periodic opportunities to update security controls and, therefore, to adapt continuously to cyber-threats. On the other hand, the tooling provided to employees working on the cloud is specific to each enterprise. Also, this tooling is evolving over time. In the context of this project, we provide complete freedom regarding the execution of custom software on each personal cloud account. In addition, with periodic recycling of these accounts there is an opportunity to continuously update the toolbox provided to employees.

## Cyclic life cycle for personal accounts

Since we want to purge and to recycle accounts assigned to individuals, this can be represented as a state
machine that features following states and transitions. With the Sustainable Personal Accounts project, states are implemented as Organisational Units (OU) within an AWS Organization.

- **OU Vanilla Accounts** - When an account has just been created by Control Tower, ServiceNow, or by any other mean, it is linked to a specific identity. Note that Control Tower does a pretty good job to create an identity in AWS Single Sign-On (SSO) before creating a new account. For accounts in this state, the most important activity is to add tags to the account itself. Then the tagged account can be moved to the next state.

- **OU Assigned Accounts** - When an account has been formally linked to some identity with tags, it is considered assigned to a person. For accounts in this state, there is a need to enforce corporate policies by adjusting resources and by creating specific roles and policies in the account itself. This process can take minutes or even hours. Once it has been properly prepared, the assigned account can be moved to the next state.

- **OU Released Accounts** - This is the state where an account can be used almost freely by the person assigned to it. Guardrails can include: Service Control Policies (SCP) assigned to the Organisational Unit (OU) where the account is sitting, AWS CloudTrail for traceability, IAM policies to provide observability to third-party tools, Billing monitoring and alerting. Released Accounts can stay in this state as long as determined by corporate policy, but there is a need to set a limit anyway. We recommend to expire accounts at least once per month, since this preserves cloud resources for weeks, while providing a monthly window to roll out updated corporate policies or new guardrails and blueprints across personal accounts. Enterprises with strong Continuous Integration (CI) practice should adopt weekly expirations at least, or, if possible, daily expirations.

- **OU Expired Accounts** - Released Accounts are expired at regular intervals (e.g., daily, weekly, or monthly). Activities on expired accounts consist of systematic deletion of resources. Some resources may be preserved though the process, either because they have been tagged for explicit deadline at a later date, or because they cannot be created again (e.g., CloudFormation stacks created by Control Tower). Once accounts have been purged, they can be moved to Assigned Accounts for a new cycle.

## Frequently asked questions

In this question we address frequent questions about Sustainable Personal Accounts. We also explain most important design decisions on the architecture of the system.

### Q. How many accounts do we want to support in a single SPA state machine?

Enterprise accounts may have thousands of software engineers. Purpose of the SPA is that each of them can get access to a personal AWS account to foster innovation and agility. As a rule of thumb, the basic requirement is that up to 10,000 AWS accounts are purged and recycled on a weekly basis. In addition, the design of the system is as simple as possible, so that it should be convenient even for a single team of some developers.

### Q. Why are you moving accounts across multiple Organisational Units (OU)?

We build state machines out of Organisational Units (OU) because of security and because of efficiency. Since each OU has its own Security Control Policies (SCP), moving an account around also determines what a person can do, or not, after authentication. For example, when your account is moved to the OU Expired Accounts, then the SCP there is preventing you from creating any resource. Secondly, the move of an account can be easily detected at the organisation level and pushed to an event bus in AWS account devoted to automation. Thirdly, by deploying accounts across OU we do not need a separate storage engine for states. The Sustainable Personal Accounts design is both serverless and storageless, but servicefull.

### Q. How are transitions detected and managed?

When an AWS account is created into an Organisation Unit, or moved to an OU, this is detected as an event originated by AWS Organization, and forwarded to an EventBridge bus. From there, multiple rules and subscribers can be activated to handle each event appropriately.

In addition, events generated by the code of Sustainable Personal Account itself are also emitted on the same bus. Generally speaking, we compensate the fragmentation of code by centralising events into a single event bus for the entire system.

### Q. How are preparation and purge activities handled in the system?

We have selected Codebuild for heavy processing of personal AWS accounts. Codebuild matches all requirements that we could think about:

- it is a serverless and VPC-less service
- execution limit is 8 hours
- you pay for actual processing time, but no more
- it embeds a shell and allow for straightforward execution of AWS CLI, of python code and of AWS-Nuke
- buildspec structure is easy to manage in version control



Options that may be considered include at least Lambda, ECS, Automation and CodeBuild. Lambda is not adapted because execution is limited to 15 minutes, which is not enough for the provisioning or the destruction of complex resources such as Active Directory, FSx for Windows volume, etc. ECS does not have timing limitations, but it requires some VPC context that, strictly speaking, we do not need at all. SSM Automation is a powerful and VPC-less construct that can do almost anything. However, it is more designed to orchestrate code execution than to implement it. For example, SSM Automation can run python scripts but they are limited to a maximum duration of 10 minutes, which is not enough for our use case. At the end of the day, Codebuild is a great candidate to automate preparation and purge activities within each account.

Note that CodeBuild can be expensive compared to other compute options. We recommend to stick to `arm1.small`compute instance type if possible.

### Q. Is this a centralised or a distributed architecture?

SPA is featuring an event-driven architecture, and serverless infrastructure. By default, centralised lambda functions take care of changing states of accounts. However, the preparation of assigned accounts and the purge of expired accounts require heavy computing capabilities that are not compatible with Lambda. These specific activities can be either centralised in one AWS account, or distributed into the personal accounts themselves.

With centralised processing, you can deploy code only once and manage configuration files adapted to target accounts. Also, you need specific cross-account permissions to allow the creation and the destruction of resources from another account. With centralised processing, the scaling is limited by quotas related to underlying resources. For example, with Codebuild there is a limit of 60 concurrent builds in one account, that would limit the number of accounts managed in SPA if Codebuild projects were started into one centralised account.

With distributed processing, you have to deploy code within each target account and then execute it. You need cross-account permissions only to deploy code into target accounts. Codebuild quota limits are not an issue anymore. Because of the scaling that it enables, and because of the reduced IAM permissions required, we prefer a distributed design for heavy processing.

At the end of the day, some parts of SPA are centralised, while other parts are distributed:

- A single AWS account is used for centralised automation, with one EventBridge bus and some Lambda functions.

- Personal AWS accounts managed by SPA host heavy processing required for their preparation and for their purge.

### Q. Can you list the components of the SPA architecture?

Sure. Sustainable Personal Accounts features following building blocks:

- **The Organisation** - This is the specific instance of AWS Organisation that is hosting  all personal accounts managed by SPA. We recommend to land SPA into an organisation deployed by AWS Control Tower, so as to benefit from integrated SSO.

- **Vanilla Accounts**, **Assigned Accounts**, **Released Accounts** and **Expired Accounts** - These are the Organisational Unit (OU) that host all personal accounts. Each OU is a container for accounts in a given state. In the context of Control Tower, we recommend to create these four OUs as children of the Sandbox OU.

- **Personal AWS accounts** - Each account handled with SPA is put into one of the four OUs mentioned above. In addition, each account is tagged with the e-mail address of the person using it. In the context of Control Tower, the creation of a personal account can be streamlined with the account factory in Service Catalog.

- **Automation account** - This is the AWS account that hosts centralised SPA resources such as EventBridge event bus and Lambda functions. In the context of Control Tower, we recommend to place this account in the Sandbox OU. For example, you can rename the Sandbox AWS account created by Control Tower to Automation and that's it.

- **Automation region** - This is the selected AWS region to deploy Eventbridge resources, Lambda functions, Codebuild projects, and SSM Parameter Store.

- **Event bus** - This is the default EventBridge bus of the Automation Account. It is the single place to observe the entire system. Subscribing to events is a natural option for the extension and for the customization of SPA.

- **MoveVanillaAccount**, **SignalAssignedAccount**, **MoveAssignedAccount**, **ExpireReleasedAccounts**, **SignalExpiredAccount** and **MoveExpiredAccount** - Each Lambda function is triggered by some EventBridge rule.

- **PrepareAccount** and **PurgeAccount** - These templated Codebuild projects are actually deployed in personal accounts, and started asynchronously, by Lambda functions **SignalAssignedAccount** and **SignalExpiredAccount**.

- **Parameter store** - Parameters used by SPA code, including templates for Codebuild projects, are placed in SSM Parameter Store of the Automation account.

- 
