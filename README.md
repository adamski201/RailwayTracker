# Railway Tracker

## About

RailWatch comprises a set of related services for the analysis and monitoring of UK railway stations and rail operators.

Our website can be found [here](http://18.133.189.84:8501/).

The website contains: 
    - A dashboard displaying various disruption statistics for a selected train station, such as a breakdown of average delays per hour of the day, historical trends in delays and cancellations, and a live feed of major incidents that are currently affecting that station.
    - A page allowing you to sign up for weekly summary reports on the performance of your chosen station.
    - A page allowing you to sign up for realtime incident alerts for a given operator.

Realtime incident alerts arrive via SMS and/or Email within seconds of publication on the National Rail incident feed.

Currently, our data sources include the Real Time Trains API and the National Rail KnowledgeBase incident feed.

## Folder & Files Structure

`.github/`: Contains the GitHub Actions workflow files for CI/CD.

`archive/`: Contains the scripts for automatically archiving data older than a month.

`dashboard/`: Contains the Streamlit dashboard code.

`database/`: Contains the database schema and related setup scripts.

`images/`: Contains images used in the README [across the project].

`incidents/`: Contains the ETL process for the incident feed data.

`performance_pipeline/`: Contains the ETL process for the train arrivals and disruption data.

`reports/`: Contains scripts for generating weekly summary reports.

`terraform/`: Contains the Terraform files for deploying the cloud services.

## Pre-requisites

- Python 3.11
- pip3
- Docker
- AWS CLI
- Terraform

## Installation & Setup

- What needs to already be installed
- How to install required libraries
- Required ENV variables (and format)
- Required database structure/seeding
    - `psql --host [database host] [dbname] -f schema.sql`

Create an `.env` file [in this directory] with the following structure:

```sh
Incidents/:
AWS_ACCESS_KEY_ID=XXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXX
HOST=XXXXXXXXXX
STOMP_PORT=XXXXXXXXXX
USERNAME=XXXXXXXXXX
PASSWORD=XXXXXXXXXX
INCIDENTS_TOPIC=XXXXXXXXXX
TOPIC_ARN=XXXXXXXXXX
DB_HOST=XXXXXXXXXX
DB_PORT=XXXXXXXXXX
DB_USER=XXXXXXXXXX
DB_PASS=XXXXXXXXXX
DB_NAME=XXXXXXXXXX

Reports/:
DB_HOST=XXXXXXXXXX
DB_PORT=XXXXXXXXXX
DB_USER=XXXXXXXXXX
DB_PASS=XXXXXXXXXX
DB_NAME=XXXXXXXXXX
ACCESS_KEY_ID=XXXXXXXXXX
SECRET_ACCESS_KEY=XXXXXXXXXX
SOURCE_EMAIL=XXXXXXXXXX
LOCAL_FOLDER=XXXXXXXXXX

Performance/:
REALTIME_API_USER=XXXXXXXXXX
REALTIME_API_PASS=XXXXXXXXXX
DB_HOST=XXXXXXXXXX
DB_PORT=XXXXXXXXXX
DB_USER=XXXXXXXXXX
DB_PASS=XXXXXXXXXX
DB_NAME=XXXXXXXXXX

Dashboard/:
DB_HOST=XXXXXXXXXX
DB_PORT=XXXXXXXXXX
DB_USER=XXXXXXXXXX
DB_PASS=XXXXXXXXXX
DB_NAME=XXXXXXXXXX
TOPIC_ARN=XXXXXXXXXX

Archive/:
AWS_ACCESS_KEY_ID=XXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXX
DB_HOST=XXXXXXXXXX
DB_USER=XXXXXXXXXX
DB_PASS=XXXXXXXXXX
DB_PORT=XXXXXXXXXX
DB_NAME=XXXXXXXXXX
S3_BUCKET=XXXXXXXXXX
```

`DB_HOST` should be a valid URL to a Postgres database server.

Create a terraform.tfvars in each of the respective folders in the terraform directory and add these variables:

```sh
Incidents/:
HOST=XXXXXXXXXX
STOMP_PORT=XXXXXXXXXX
USERNAME=XXXXXXXXXX
PASSWORD=XXXXXXXXXX
INCIDENTS_TOPIC=XXXXXXXXXX
TOPIC_ARN=XXXXXXXXXX
DB_HOST=XXXXXXXXXX
DB_PORT=XXXXXXXXXX
DB_USER=XXXXXXXXXX
DB_PASS=XXXXXXXXXX
DB_NAME=XXXXXXXXXX
AWS_ACCESS_KEY_I=XXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXX
VPC_ID=XXXXXXXXXX

Reports/:
AWS_ACCESS_KEY_ID=XXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXX
AWS_REGION=XXXXXXXXXX
DB_USER=XXXXXXXXXX
DB_HOST=XXXXXXXXXX
DB_NAME=XXXXXXXXXX
DB_PASS=XXXXXXXXXX
DB_PORT=XXXXXXXXXX
LOCAL_FOLDER=XXXXXXXXXX
SOURCE_EMAIL==XXXXXXXXXX

Performance/:
AWS_ACCESS_KEY_ID=XXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXX
AWS_REGION=XXXXXXXXXX
DB_USER=XXXXXXXXXX
DB_HOST=XXXXXXXXXX
DB_NAME=XXXXXXXXXX
DB_PASS=XXXXXXXXXX
DB_PORT=XXXXXXXXXX
RTT_API_PASS=XXXXXXXXXX
RTT_API_USER=XXXXXXXXXX
CLUSTER_ARN=XXXXXXXXXX
SUBNET_IDS=["XXXXXXXXXX", ...]

Dashboard/:
AWS_ACCESS_KEY_ID=XXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXX
AWS_REGION=XXXXXXXXXX
DB_USER=XXXXXXXXXX
DB_HOST=XXXXXXXXXX
DB_NAME=XXXXXXXXXX
DB_PASS=XXXXXXXXXX
DB_PORT=XXXXXXXXXX
VPC_ID=XXXXXXXXXX
TOPIC_ARN=XXXXXXXXXX


Archive/:
AWS_ACCESS_KEY_ID=XXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXX
AWS_REGION=XXXXXXXXXX
DB_HOST=XXXXXXXXXX
DB_USER=XXXXXXXXXX
DB_PASS=XXXXXXXXXX
DB_PORT=XXXXXXXXXX
DB_NAME=XXXXXXXXXX
S3_BUCKET=XXXXXXXXXX

S3_Bucket/:
AWS_ACCESS_KEY_ID=XXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXX
AWS_REGION=XXXXXXXXXX

RDS/:
AWS_ACCESS_KEY_ID=XXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXX
SUBNET_GROUP=XXXXXXXXXX
VPC_ID=XXXXXXXXXX
DB_USER=XXXXXXXXXX
DB_PASS=XXXXXXXXXX
PUBLIC_SUBNET_ID=XXXXXXXXXX
```    


## Development

- Command to run it
- Potentially other useful commands (reset DB, clear all user data, run in test mode, etc.)

## Deployment

To build the cloud services, run these commands:

```sh
terraform init
terraform plan
terraform apply
```

To remove the cloud services, run this command:

```sh
terraform destroy
```

## Documentation

### ERD diagram for Short-term Storage

![ERD diagram 1](https://github.com/adamski201/RailwayTracker/blob/readme/images/public_erd.png)

### ERD diagram for Long-term Storage

![ERD diagram 2](https://github.com/adamski201/RailwayTracker/blob/readme/images/archive_erd.png)

### Cloud architecture diagram

![Cloud architecture diagram](https://github.com/adamski201/RailwayTracker/blob/readme/images/architecture_diagram_revision.png)

## Contributors

* [aribasyeda](https://github.com/aribasyeda)
* [SaniyaShaikhh](https://github.com/SaniyaShaikhh)
* [adamski201](https://github.com/adamski201)
* [isaacschaessenscoleman](https://github.com/isaacschaessenscoleman)
