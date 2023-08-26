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


[[ "${WITH_START_STOP_EC2_INSTANCES}" = "enabled" ]] || exit 0

echo "Automating the start and stop of EC2 instances..."

START_CRON_EXPRESSION="${START_CRON_EXPRESSION:-0 5 ? * MON-FRI *}"
echo "- will start EC2 instances on cron '${START_CRON_EXPRESSION}'"

STOP_CRON_EXPRESSION="${STOP_CRON_EXPRESSION:-0 21 ? * MON-FRI *}"
echo "- will stop EC2 instances on cron '${STOP_CRON_EXPRESSION}'"

TAG_WITHOUT_START_STOP="${TAG_WITHOUT_START_STOP:-operations-do-not-schedule}"
echo "- will skip EC2 instances tagged with '${TAG_WITHOUT_START_STOP}'"

[[ "${ACCOUNT}" ]] || (echo "- ERROR: missing variable ACCOUNT"; exit 1)

[[ "${CLOUD_CUSTODIAN_ROLE}" ]] || (echo "- ERROR: missing variable CLOUD_CUSTODIAN_ROLE"; exit 1)

echo "Installing Cloud Custodian..."
pip install c7n

echo "Preparing Cloud Custodian policy for account ${ACCOUNT}..."
cat <<EOF >policy.yaml
policies:
  - name: night-stop
    mode:
      type: periodic
      schedule: cron(${STOP_CRON_EXPRESSION})
      role: arn:aws:iam::${ACCOUNT}:role/${CLOUD_CUSTODIAN_ROLE}
    resource: aws.ec2
    filters:
      - "tag:${TAG_WITHOUT_START_STOP}": absent
    actions:
      - type: stop

  - name: morning-start
    mode:
      type: periodic
      schedule: cron(${START_CRON_EXPRESSION})
      role: arn:aws:iam::${ACCOUNT}:role/${CLOUD_CUSTODIAN_ROLE}
    resource: aws.ec2
    filters:
      - "tag:${TAG_WITHOUT_START_STOP}": absent
    actions:
      - type: start
EOF

echo "Running Cloud Custodian..."
custodian run -s c7n.out policy.yaml