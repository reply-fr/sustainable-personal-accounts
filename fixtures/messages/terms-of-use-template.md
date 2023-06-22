---
title: User Agreement for Personal Sandbox AWS Account
---
# User Agreement for Personal Sandbox AWS Account

This User Agreement ("Agreement") governs your use of the personal AWS sandbox account ("Account") provided to you by ___corporation___. By accessing or using this Sandbox Account, you agree to be bound by this Agreement.

## Purpose of the Account

The Account is provided to you for the purpose of accelerating innovation at individual level. This is a resource for experimenting, learning, and testing AWS services and features in a non-production environment. You are not allowed to use the Account for any commercial or production purposes.

## Shared responsibility model

The Account is governed by a shared security model, where you are responsible for data and for cloud resources that you create or deploy on this account, and where ___corporation___ is responsible of the funding and for the blueprints and guardrails supporting cloud operations.

## Responsibilities of ___corporation___

___corporation___ provides long-term support to employees involved in cloud innovation, by provisioning and assigning AWS accounts to these employees. ___corporation___ support costs incurred, and allow the users of these sandboxes to learn and to experiment. Learning is referring to practical interactions with AWS Console, API and SDK. This can be done with tutorials, with guided workshops, or with the deployment of existing templates or code available from trusted sources on the Internet. Experimentations is referring to small-scale integration tests or configuration tests. This can be done with some lines of code or templates, with the objective to validate an idea and to document experimentation results.

For each sandbox account, ___corporation___ provides clear governance rules, such as:

- Level of monthly budget that you are entitled to consume on AWS platform – currently, $30 per ccount and per month

- Sandbox accounts are purged every week on Saturday at 8pm CET

- Maximum age of resources before they are automatically destroyed on your Account – currently, 1 month

- List of AWS regions where you can deploy workloads

- List of AWS services that you cannot provision or act upon

## Your responsibilities

You are responsible for capitalising on lessons that you have learnt while using your Account. For example, we recommend to use code to deploy cloud resources, so that automation is captured in git repositories and benefits all of ___corporation___.

You are responsible for all cloud resources that you deploy on the Account assigned to you, and to related data. This is meaning that you explicitly have to enforce corporate policies of ___corporation___, for example:

- Preserve confidentiality and security of credentials related to your Account (e.g., username and password, MFA).

- Use the Account only for the intended purpose described before.

- Comply with all applicable laws, regulations, and AWS & policies of ___corporation___.

- Notify Security & IT Ops team immediately of any unauthorized use or suspected security breach of your Account.

- Ensure that any data or content you upload, store, or process in the Account complies with applicable laws and does not infringe on the intellectual property rights of others.

## Usage boundaries

While the Account is supporting most products and services of the AWS platform, it is not adapted to all use cases. More specifically, following examples describe situations where your workload should be deployed on an alternate AWS account, and not on your personal sandbox:

- If you need to handle a copy of production data, then consider an AWS account adapted to production workloads, which your Account is not. Only use anonymised and computed data on your Account.

- If you need to share a cloud resource with another person, or with multiple persons, then you should deploy your workload on an account that is supporting team efforts, and not on your Account. You still can share the code developed or tested in your Account via corporate git repositories with your colleagues.

- If you need to expose a cloud resource over the network, be it a web site, a REST micro-service, a database or any other kind of server in a client-server architecture, then move your workload to an AWS account adapted to corporate workloads. Within your Account, share your personal cloud resources with other personal cloud resources, for example, for test purpose.

- If you need to access a corporate cloud resource such as a database, or a service via the corporate network, then you should deploy your workload on an account adapted to corporate workloads, and not on your Account. Within your account, only use sample data and fixtures files coming with content of git repositories.

- If you need to perform stress tests, or similar tests at scale, then deploy your workload on an account adapted to heavy temporary costs, which your Account is not. Within your account, you can perform integration tests and end-to-end functional tests, if their costs are compatible with the budget given to you.

## Termination of the Account

___corporation___ may terminate your Account at any time for any reason without notice. You may also terminate your Account at any time by following the instructions provided by ___corporation___.

## Limitations of Liability

___corporation___ will not be liable to you or any third party for any damages or losses arising from your use of the Account, including but not limited to direct, indirect, incidental, consequential, or punitive damages, even if ___corporation___ or AWS has been advised of the possibility of such damages.