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

echo "Working on budget alert for this account..."

cat <<EOF >budget.json
{
    "BudgetName": "${BUDGET_NAME}",
    "BudgetLimit": {
        "Amount": "${BUDGET_AMOUNT}",
        "Unit": "USD"
    },
    "BudgetType": "COST",
    "CostFilters": {},
    "CostTypes": {
        "IncludeTax": true,
        "IncludeSubscription": true,
        "UseBlended": false,
        "IncludeRefund": false,
        "IncludeCredit": false,
        "IncludeUpfront": true,
        "IncludeRecurring": true,
        "IncludeOtherSubscription": true,
        "IncludeSupport": true,
        "IncludeDiscount": true,
        "UseAmortized": false
    },
    "TimePeriod": {
        "Start": "2020-01-01T01:00:00+01:00",
        "End": "2080-01-01T02:00:00+02:00"
    },
    "TimeUnit": "MONTHLY"
}
EOF

cat <<EOF >notifications-with-subscribers.json
[
    {
        "Notification": {
            "ComparisonOperator": "GREATER_THAN",
            "NotificationType": "ACTUAL",
            "Threshold": ${ALERT_THRESHOLD},
            "ThresholdType": "PERCENTAGE"
        },
        "Subscribers": [
            {
                "Address": "${BUDGET_EMAIL}",
                "SubscriptionType": "EMAIL"
            },
            {
                "Address": "${TOPIC_ARN}",
                "SubscriptionType": "SNS"
            }
        ]
    }
]
EOF

CURRENT_AMOUNT=$(aws budgets describe-budget --account-id $ACCOUNT --budget-name $BUDGET_NAME --query 'Budget.BudgetLimit.Amount' --output text) || true

if [ -z "$CURRENT_AMOUNT" ]; then
    echo "Creating new budget"
    aws budgets create-budget --account-id $ACCOUNT --budget file://budget.json --notifications-with-subscribers file://notifications-with-subscribers.json
elif [ "$CURRENT_AMOUNT" != "$BUDGET_AMOUNT" ]; then
    echo "Updating budget"
    aws budgets update-budget --account-id $ACCOUNT --new-budget file://budget.json
else
    echo "No budget modification"
fi

# echo "Removing obsolete budget names"
# aws budgets delete-budget --account-id $ACCOUNT --budget-name DataReplyBudget || true
# aws budgets delete-budget --account-id $ACCOUNT --budget-name StormReplyBudget || true