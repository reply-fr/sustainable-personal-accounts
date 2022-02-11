#!/usr/bin/env python3
"""
Copyright Reply.com or its affiliates. All Rights Reserved.
SPDX-License-Identifier: Apache-2.0
Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

# credit:
# - https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_cloudwatch.Metric.html
# - https://medium.com/dtlpub/custom-cloudwatch-dashboard-to-monitor-lambdas-e399ef251f07
# - https://github.com/cdk-patterns/serverless/blob/main/the-cloudwatch-dashboard/python/the_cloudwatch_dashboard/the_cloudwatch_dashboard_stack.py


from constructs import Construct
from aws_cdk.aws_cloudwatch import (ComparisonOperator,
                                    Dashboard,
                                    GraphWidget,
                                    Metric,
                                    SingleValueWidget,
                                    TextWidget,
                                    TreatMissingData)


class Cockpit(Construct):

    def __init__(self, scope: Construct, id: str, functions):
        super().__init__(scope, id)

        self.cockpit = Dashboard(
            self,
            id=id,
            dashboard_name=id)

        self.cockpit.add_widgets(
            self.get_text_label_widget())

    #     self.cockpit.add_widgets(
    #         self.get_text_label_widget(),
    #         self.get_ec2_statuscheckfailed_widget(servers))
    #
    #     self.cockpit.add_widgets(
    #         self.get_ec2_cpuutilization_widget(servers),
    #         self.get_ec2_networkout_widget(servers))
    #

    def get_text_label_widget(self):
        ''' show static banner that has been configured for this dashboard '''

        return TextWidget(markdown=toggles.cockpit_text_label,
                          height=3,
                          width=18)

    # def get_ec2_statuscheckfailed_widget(self, servers):
    #     ''' show the total number of EC2 status check that have failed '''
    #
    #     metrics = []
    #     for instance in servers.list_all_servers():
    #         metrics.append(Metric(
    #             metric_name="StatusCheckFailed",
    #             namespace="AWS/EC2",
    #             dimensions_map=dict(InstanceId=instance.instance_id),
    #             statistic="avg"))
    #
    #     return SingleValueWidget(
    #         title="EC2 Status Check Failed",
    #         metrics=metrics,
    #         height=3,
    #         width=6)
    #
    # def get_ec2_cpuutilization_widget(self, servers):
    #     ''' graph CPU Utilization percentage for computers in the cluster '''
    #
    #     metrics = []
    #     alarms = []
    #     for instance in servers.list_all_servers():
    #         metric = Metric(
    #             metric_name="CPUUtilization",
    #             namespace="AWS/EC2",
    #             dimensions_map=dict(InstanceId=instance.instance_id),
    #             statistic="avg")
    #         alarm = metric.create_alarm(
    #             self,
    #             "EC2CPUAlarm-{}".format(self.resolve(instance.instance_id)),
    #             threshold=90,
    #             comparison_operator=ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
    #             evaluation_periods=5,
    #             treat_missing_data=TreatMissingData.NOT_BREACHING)
    #         metrics.append(metric)
    #         alarms.append(alarm.to_annotation())
    #
    #     return GraphWidget(
    #         title="EC2 CPU Utilization",
    #         left=metrics,
    #         left_annotations=alarms,
    #         height=10,
    #         width=12)
    #
    # def get_ec2_networkout_widget(self, servers):
    #     ''' graph network out traffic for computers in the cluster '''
    #
    #     metrics = []
    #     for instance in servers.list_all_servers():
    #         metrics.append(Metric(
    #             metric_name="NetworkOut",
    #             namespace="AWS/EC2",
    #             dimensions_map=dict(InstanceId=instance.instance_id),
    #             statistic="avg"))
    #
    #     return GraphWidget(
    #         title="EC2 Network Out",
    #         left=metrics,
    #         height=10,
    #         width=12)