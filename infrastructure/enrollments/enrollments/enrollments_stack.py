import os
from aws_cdk import (
    core as cdk,
    aws_lambda as lambda_,
    aws_dynamodb as dynamodb,
    aws_events as eventbridge,
    aws_events_targets as event_target
)

SERVICES_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../../../services'
)


class EnrollmentsStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        tournament_enrollments = dynamodb.Table(
            scope=self,
            id='TournamentEnrollments',
            table_name='TournamentEnrollments',
            partition_key=dynamodb.Attribute(
                name='ClubId',
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name='TournamentId',
                type=dynamodb.AttributeType.STRING
            )
        )

        coupons = dynamodb.Table(
            scope=self,
            id='Coupons',
            table_name='Coupons',
            partition_key=dynamodb.Attribute(
                name='ClubId',
                type=dynamodb.AttributeType.STRING
            )
        )

        env = self.node.try_get_context("env") or 'dev'

        with open(os.path.join(SERVICES_PATH, 'getEnrolledTournamentsFromClub/index.py')) as f:
            lambda_code = f.read()

        get_enrolled_tournaments_from_club = lambda_.Function(
            scope=self,
            id='GetEnrolledTournamentsFromClub',
            code=lambda_.InlineCode(lambda_code),
            handler='index.handler',
            runtime=lambda_.Runtime.PYTHON_3_8,
            function_name='getEnrolledTournamentsFromClub',
            environment={'ENV': env}
        )

        tournament_enrollments.grant_read_data(get_enrolled_tournaments_from_club)

        with open(os.path.join(SERVICES_PATH, 'generateCoupon/index.py')) as f:
            lambda_code = f.read()

        generate_coupon = lambda_.Function(
            scope=self,
            id='GenerateCoupon',
            code=lambda_.InlineCode(lambda_code),
            handler='index.handler',
            runtime=lambda_.Runtime.PYTHON_3_8,
            function_name='generateCoupon',
            environment={'ENV': env}
        )

        coupons.grant_write_data(generate_coupon)
        get_enrolled_tournaments_from_club.grant_invoke(generate_coupon)

        tournament_enrollment_event_bus = eventbridge.EventBus(
            scope=self,
            id='TournamentEnrollmentEvents',
            event_bus_name='tournamentEnrollment'
        )
        eventbridge.Rule(
            scope=self,
            id='ClubEnrolledToTournamentRule',
            event_bus=tournament_enrollment_event_bus,
            rule_name='club-enrolled-to-tournament',
            event_pattern=eventbridge.EventPattern(
                detail={'state': ['CLUB_ENROLLED_FOR_TOURNAMENT']}
            ),
            targets=[event_target.LambdaFunction(generate_coupon)]
        )

        tournament_enrollment_event_bus_arn = tournament_enrollment_event_bus.event_bus_arn

        with open(os.path.join(SERVICES_PATH, 'enrollClubToTournament/index.py')) as f:
            lambda_code = f.read()

        enroll_club_to_tournament = lambda_.Function(
            scope=self,
            id='EnrollClubToTournament',
            code=lambda_.InlineCode(lambda_code),
            handler='index.handler',
            runtime=lambda_.Runtime.PYTHON_3_8,
            function_name='enrollClubToTournament',
            environment={
                'ENV': env,
                'TOURNAMENT_ENROLLMENT_EVENT_BUS': tournament_enrollment_event_bus_arn
            }
        )
        tournament_enrollments.grant_write_data(enroll_club_to_tournament)

        tournament_enrollment_event_bus.grant_put_events(enroll_club_to_tournament)
