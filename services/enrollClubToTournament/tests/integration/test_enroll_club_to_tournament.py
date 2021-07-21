import os
import json
import time
from typing import NoReturn
import pytest
from localstack.services import infra
from localstack.utils.aws import aws_stack
from localstack.utils.aws.aws_stack import await_stack_completion


def create_and_await_cdk_stack() -> NoReturn:
    stack_template_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../../../../infrastructure/enrollments/cdk.out/EnrollmentsStack.template.json"
    )
    with open(stack_template_path) as f:
        template = f.read()

    cloudformation = aws_stack.connect_to_service('cloudformation')
    stack_name = 'enrollmentsStack'
    response = cloudformation.create_stack(
        StackName=stack_name,
        TemplateBody=template
    )
    assert response['ResponseMetadata']['HTTPStatusCode'] == 200
    await_stack_completion(stack_name)


def await_until_get_coupon_by_club_id(club_id: str, retries: int = 3, sleep: int = 1) -> NoReturn:
    dynamodb_client = aws_stack.connect_to_service('dynamodb')
    for i in range(0, retries + 1):
        coupon = dynamodb_client.query(
            TableName='Coupons',
            Select='ALL_ATTRIBUTES',
            KeyConditionExpression='ClubId = :clubId',
            ExpressionAttributeValues={
                ':clubId': {'S': club_id}
            }
        )
        if coupon['Items'] and coupon['Items'][0]['ClubId']['S'] == club_id:
            return coupon
        time.sleep(sleep)


class TestEnrollClubToTournament:
    @classmethod
    def setup_class(cls):
        infra.start_infra(asynchronous=True)
        create_and_await_cdk_stack()

    @classmethod
    def teardown_class(cls):
        infra.stop_infra()
        # Kill process that stay alive after stop infra
        os.system('kill $(pgrep local-kms.lin)')
        os.system('kill $(pgrep kinesis-mock)')

    def test_enroll_club_to_its_first_tournament(self):
        # Arrange
        tournament_id = 'fake-tournament-1234'
        club_id = 'fake-club-1234'
        lambda_client = aws_stack.connect_to_service('lambda')

        # Act
        lambda_client.invoke(
            FunctionName='enrollClubToTournament',
            Payload=json.dumps({
                'tournamentId': tournament_id,
                'clubId': club_id
            }).encode('utf-8')
        )

        # Assert
        dynamodb_client = aws_stack.connect_to_service('dynamodb')
        tournament_enrollment = dynamodb_client.query(
            TableName='TournamentEnrollments',
            Select='COUNT',
            KeyConditionExpression='TournamentId = :tournamentId AND ClubId = :clubId',
            ExpressionAttributeValues={
                ':tournamentId': {'S': tournament_id},
                ':clubId': {'S': club_id}
            }
        )
        assert tournament_enrollment.get('Count') == 1

        club_coupon = await_until_get_coupon_by_club_id(club_id)
        assert club_coupon['Items'][0]['DiscountInEuros']['N'] == '25'


