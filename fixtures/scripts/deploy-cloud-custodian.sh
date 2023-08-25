#!/bin/sh

# Copyright Reply.com or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

echo "Installing Cloud Custodian..."
pip install c7n

echo "Preparing Cloud Custodian policy for account ${ACCOUNT}..."
cat <<EOF >policy.yaml
policies:
  - name: night-stop
    mode:
      type: periodic
      schedule: cron(0 18 ? * MON-FRI *)
      role: arn:aws:iam::${ACCOUNT}:role/${CLOUD_CUSTODIAN_ROLE}
    resource: aws.ec2
    filters:
      - "tag:without-start-stop": absent
    actions:
      - type: stop

  - name: morning-start
    mode:
      type: periodic
      schedule: cron(0 6 ? * MON-FRI *)
      role: arn:aws:iam::${ACCOUNT}:role/${CLOUD_CUSTODIAN_ROLE}
    resource: aws.ec2
    filters:
      - "tag:without-start-stop": absent
    actions:
      - type: start
EOF

echo "Running Cloud Custodian..."
custodian run -s c7n.out policy.yaml