import os
import json
import boto3


def handler(event, context):
    tournament_id = event.get('tournamentId')
    club_id = event.get('clubId')
    env = os.getenv('ENV')
    dynamodb_client = boto3.client("dynamodb") if env != 'test' \
        else boto3.client("dynamodb", endpoint_url=f"http://{os.getenv('LOCALSTACK_HOSTNAME')}:4566")

    dynamodb_client.put_item(
        TableName="TournamentEnrollments",
        Item={
            "TournamentId": {"S": tournament_id},
            "ClubId": {"S": club_id}
        },
        ReturnValues="NONE"
    )

    event_client = boto3.client('events') if env != 'test' \
        else boto3.client("events", endpoint_url=f"http://{os.getenv('LOCALSTACK_HOSTNAME')}:4566")
    event_client.put_events(
        Entries=[{
            'Source': 'enrollClubToTournament',
            'DetailType': 'TOURNAMENT_ENROLLMENT',
            # Tenemos que usar el arn del bus, porque a la hora de crear la regla localstack usa el ARN del bus en vez del nombre
            'EventBusName': os.getenv('TOURNAMENT_ENROLLMENT_EVENT_BUS'),
            'Detail': json.dumps({
                'state': 'CLUB_ENROLLED_FOR_TOURNAMENT',
                'tournamentId': tournament_id,
                'clubId': club_id
            })
        }]
    )


