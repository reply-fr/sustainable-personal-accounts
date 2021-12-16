# Sustainable Personal Accounts

With this project we promote the idea that each AWS practitioner should have his/her own account, so as to practice almost freely on the platform and accelerate innovation. At the same time, in corporate environment there is a need for managed costs and for forcing towards software automation. For this reason, accounts are purged at regular intervals, and recycled.

## Cyclic life cycle for personal accounts

Since we want to purge and to recycle accounts assigned to individuals, this can be represented as a state
machine that feature following states and transitions:
- vanilla account - when an account has just been created by Control Tower, ServiceNow, or by any other mean
- assigned account - when an account has been assigned to a person, and has to be aligned with corporate policies
- released account - when an account is made available to a person, and can be used as freely as possible
- expired account - when an account has to be purged of its content, then is cycled as an assigned account again
