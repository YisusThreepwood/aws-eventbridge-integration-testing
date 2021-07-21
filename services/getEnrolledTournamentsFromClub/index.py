import os
from typing import List
import boto3


def handler(event, context):
    club_id = event.get('clubId')
    dynamodb_client = boto3.client('dynamodb') if os.getenv('ENV') != 'test' \
        else boto3.client('dynamodb', endpoint_url=f"http://{os.getenv('LOCALSTACK_HOSTNAME')}:4566")

    club_enrollments = dynamodb_client.query(
        TableName='TournamentEnrollments',
        Select='ALL_ATTRIBUTES',
        KeyConditionExpression='ClubId = :clubId',
        ExpressionAttributeValues={':clubId': {'S': club_id}}
    )

    return {
        'enrolledTournaments': transform_items(club_enrollments['Items'])
        if club_enrollments['Count'] else []
    }


def transform_items(items: List[dict]) -> List[dict]:
    return list(map(
        lambda item: {'tournamentId': item['TournamentId']['S']},
        items
    ))
