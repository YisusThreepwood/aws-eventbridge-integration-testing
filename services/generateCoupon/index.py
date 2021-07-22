import os
import string
import random
import json
import boto3


COUPON_CODE_LENGTH = 5


def handler(event, context):
    detail = event.get('detail')
    club_id = detail.get('clubId')
    tournament_id = detail.get('tournamentId')

    if is_first_tournament_enrollment(club_id, tournament_id):
        coupon_code = generate_coupon_code()
        dynamodb_client = boto3.client('dynamodb') if os.getenv(
            'ENV') != 'test' \
            else boto3.client('dynamodb', endpoint_url=f"http://{os.getenv('LOCALSTACK_HOSTNAME')}:4566")

        dynamodb_client.put_item(
            TableName='Coupons',
            Item={
                'ClubId': {'S': club_id},
                'Code': {'S': coupon_code},
                'DiscountInEuros': {'N': '25'},
            },
            ReturnValues='NONE'
        )


def is_first_tournament_enrollment(club_id: str, tournament_id: str) -> bool:
    lambda_client = boto3.client('lambda') if os.getenv('ENV') != 'test' \
        else boto3.client('lambda', endpoint_url=f"http://{os.getenv('LOCALSTACK_HOSTNAME')}:4566")
    lambda_response = lambda_client.invoke(
        FunctionName='getEnrolledTournamentsFromClub',
        Payload=json.dumps({
            'clubId': club_id
        }).encode('utf-8')
    )
    lambda_response = json.loads(
        lambda_response['Payload'].read().decode('UTF-8'))

    previous_enrollments = [
        prev_tournament.get('tournamentId')
        for prev_tournament in lambda_response.get('enrolledTournaments')
        if prev_tournament.get('tournamentId') != tournament_id
    ]

    return len(previous_enrollments) == 0


def generate_coupon_code() -> str:
    allowed_chars = list(string.ascii_letters) + list(string.digits)
    return "".join([random.choice(allowed_chars) for i in range(COUPON_CODE_LENGTH)])
