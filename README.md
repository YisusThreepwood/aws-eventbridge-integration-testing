# aws-eventbridge-integration-testing

An example of an Event Drive System built under a serverless microservices architecture, 
implemented with Python.

# Requirements:
* OS Linux
* Python ~=3.8.0
* AWS CDK ~=1.111
* Pipenv 2021.5.29

# Environment build
* Create the virtualenv for the CDK application and install de required dependencies
```
$ cd infrastructure/enrollments
~/infraestructure/enrollments$ python3 -m venv .venv
~/infraestructure/enrollments$ source .venv/bin/activate
(.venv):~/infraestructure/enrollments$ pip install -r requirements.txt
```

* Synthesize the AWS stack, using the CDK context for setting the environment up 
  as testing environment 
```
(.venv):~/infraestructure/enrollments$ cdk synth --context env=test
```

* Install service dependencies
```
~/infraestructure/enrollments$ cd ../../services/enrollClubToTournament
~/services/enrollClubToTournament$ pipenv install --dev
```

# Usage
Run the integration test for checking that all is OK :)
```
~/services/enrollClubToTournament$ pipenv shell
(enrollClubToTournament)~/services/enrollClubToTournament$ pytest
```

# Common issues
### Fail creating resources stack
_Exception: Status "CREATE_FAILED" for stack "enrollmentsStack" not in expected list: ['CREATE_COMPLETE', 'UPDATE_COMPLETE']_
  
Make sure temporary folders (_/tmp/localstack_ and _/tmp/local-kms_) have write permission

### Localstack cannot open service ports
_Exception: Port xxxxx (path: None) was not open_

  
Kill processes opened previously by localstack

```
$ sudo kill $(pgrep kinesis-mock)

$ sudo kill $(pgrep local-kms.lin)
```  


