#!/usr/bin/env python3
from aws_cdk import core as cdk
from enrollments.enrollments_stack import EnrollmentsStack


app = cdk.App()
EnrollmentsStack(
    app,
    "EnrollmentsStack",
    env=cdk.Environment(account='000000000000', region='us-east-1'),
)

app.synth()
