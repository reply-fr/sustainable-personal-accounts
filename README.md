# Sustainable Personal Accounts

With this project we promote the idea that each AWS practitioner should have direct access to some AWS account, so as to practice almost freely on the platform and accelerate innovation. At the same time, in corporate environment there is a need enforcing policies, for managed costs and for fostering software automation. For this reason, with this project AWS accounts are purged at regular intervals, and recycled.

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
Enterprise accounts may have thousands of software engineers. Purpose of the SPA is that each of them can get access to a personal AWS account to foster innovation and agility. As a rule of thumb, the basic requirement is that 1,000 AWS accounts are purged and recycled on a weekly basis.

### Q. Why are you moving accounts across multiple Organisational Units (OU)?
We build state machines out of Organisational Units (OU) because of security and because of efficiency. Since each OU has its own Security Control Policies (SCP), moving an account around also determines what a person can do, or not, after authentication. For example, when your account is moved to the OU Expired Accounts, then the SCP there is preventing you from creating any resource. Secondly, the move of an account can be easily detected at the organisation level and pushed to an event bus in AWS account devoted to automation. Thirdly, by deploying accounts across OU we do not need a separate storage engine for states. The Sustainable Personal Accounts design is both serverless and storageless, but servicefull.

### Q. How are transitions detected and managed?
When an AWS account is created into an Organisation Unit, or moved to an OU, this is detected as an event originated by AWS Organization, and forwarded to an EventBridge bus. From there, multiple rules and subscribers can be activated to handle each event appropriately.

In addition, events generated by the code of Sustainable Personal Account itself are also emitted on the same bus. Generally speaking, we compensate the fragmentation of code by centralising events into a single event bus for the entire system.

### Q. How are preparation and purge activities handled in the system?
The first design decision is about running related code either in a one central account, or to spread code within target accounts. With centralised processing, you can deploy code only once and manage configuration files adapted to target accounts. Also, you need specific cross-account permissions to allow the creation and the destruction of resources from another account. With centralised processing, the limiting factor is the maximum quota of underlying resource. For example, the maximum number of concurrent invocations of Lambda is 1,000 in one account, and this could impose a limit to the number of accounts managed in SPA. With distributed processing, you have to deploy code within each target account and then execute it. You need cross-account permissions only to deploy the preparation or purge code. There is no limiting factor per account anymore. Because of the scaling that it enables, and because of the reduced IAM permissions required, we prefer a distrubuted design where possible.

The second design decision is to select the most appropriate service in this context. Options that may be considered include at least Lambda, ECS, Automation and CodeBuild. Lambda is not adapted because execution is limited to 15 minutes, which is not enough for the provisioning or the destruction of complex resources such as Active Directory, FSx for Windows volume, etc. ECS does not have timing limitations, but it requires some VPC context that, strictly speaking, we do not need at all. SSM Automation is a powerful and VPC-less construct that can do almost anything. However, it is more designed to orchestrate code execution than to implement it. For example, SSM Automation can not run AWS-Nuke natively, but it can spawn some support function to do it. Also, SSM Automation can run python scripts but they are limited to a maximum duration of 10 minutes, which is not enough for our use case. At the end of the day, Codebuild is a great candidate to automate preparation and purge activities within each account.

Some advantages of CodeBuild include:
- it is a serverless and VPC-less service
- execution limit is 8 hours
- you pay for actual processing time, but no more
- it embeds a shell and allow for straightforward shell statements
- buildspec structure is easy to manage in version control
- execution logs can be centralised for easy control and troubleshooting

Note that CodeBuild can be expensive compared to other compute options. Also, quotas set for Codebuild would not be compatible with a centralised design. They are making sense only because we have decided to distribute code execution as much as possible.
