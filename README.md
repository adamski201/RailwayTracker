# Railway Tracker

## About

RailWatch comprises a set of related services for the analysis and monitoring of UK railway stations and rail operators.

Our website can be found [here](http://18.133.189.84:8501/).

The website contains:

- A dashboard displaying various disruption statistics for a selected train station, such as a breakdown of average
  delays per hour of the day, historical trends in delays and cancellations, and a live feed of major incidents that are
  currently affecting that station.
- A page allowing you to sign up for weekly summary reports on the performance of your chosen station.
- A page allowing you to sign up for realtime incident alerts for a given operator.

Realtime incident alerts arrive via SMS and/or Email within seconds of publication on the National Rail incident feed.

Currently, our data sources include the Real Time Trains API and the National Rail KnowledgeBase incident feed.

## Folder & Files Structure

`.github/`: Contains the GitHub Actions workflow files for CI/CD.

`alerts/`: Contains the ETL scripts for processing incident feed data and sending automated alerts to users.

`archive/`: Contains the scripts for automatically archiving data older than a month.

`dashboard/`: Contains the Streamlit dashboard code.

`database/`: Contains the database schema and related setup scripts.

`images/`: Contains images for the README.

`performance/`: Contains the ETL process for the train arrivals and disruption data.

`reports/`: Contains scripts for generating weekly summary reports.

`terraform/`: Contains the Terraform files for deploying the cloud infrastructure.

## Pre-requisites

- Python 3.11
- pip3
- PostgreSQL
- Docker
- AWS CLI
- Terraform
- Realtime Trains API account
- Rail Data Marketplace account (for the National Rail KnowledgeBase incident feed)

## Installation & Setup

1. Clone this repository to your local machine using:

```bash
git clone <repository-url>
 ```

2. Navigate to each project directory and create a virtual environment:

```bash
cd alerts/
python3 -m venv venv
# Repeat for other directories (archive/, dashboard/, performance/, reports/)
```

3. Activate the virtual environment:

```bash
source venv/bin/activate
```

4. Install the required packages:

```bash
pip3 install -r requirements.txt
````

5. Navigate into the respective directories and create an .env file in each directory as shown below:

```.env
# Example for alerts/ directory

AWS_ACCESS_KEY_ID=XXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXX
DB_HOST=XXXXXXXXXX
DB_PORT=XXXXXXXXXX
DB_USER=XXXXXXXXXX
DB_PASS=XXXXXXXXXX
DB_NAME=XXXXXXXXXX
HOST=XXXXXXXXXX
STOMP_PORT=XXXXXXXXXX
USERNAME=XXXXXXXXXX
PASSWORD=XXXXXXXXXX
INCIDENTS_TOPIC=XXXXXXXXXX
TOPIC_ARN=XXXXXXXXXX

# Example for archive/ directory:

AWS_ACCESS_KEY_ID=XXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXX
DB_HOST=XXXXXXXXXX
DB_USER=XXXXXXXXXX
DB_PASS=XXXXXXXXXX
DB_PORT=XXXXXXXXXX
DB_NAME=XXXXXXXXXX
S3_BUCKET=XXXXXXXXXX

# Example for dashboard/ directory:

AWS_ACCESS_KEY_ID=XXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXX
DB_HOST=XXXXXXXXXX
DB_PORT=XXXXXXXXXX
DB_USER=XXXXXXXXXX
DB_PASS=XXXXXXXXXX
DB_NAME=XXXXXXXXXX
TOPIC_ARN=XXXXXXXXXX

# Example for database/ directory:

DB_HOST=XXXXXXXXXX
DB_PORT=XXXXXXXXXX
DB_USER=XXXXXXXXXX
DB_PASS=XXXXXXXXXX
DB_NAME=XXXXXXXXXX

# Example for performance/ directory:

AWS_ACCESS_KEY_ID=XXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXX
DB_HOST=XXXXXXXXXX
DB_PORT=XXXXXXXXXX
DB_USER=XXXXXXXXXX
DB_PASS=XXXXXXXXXX
DB_NAME=XXXXXXXXXX
REALTIME_API_USER=XXXXXXXXXX
REALTIME_API_PASS=XXXXXXXXXX

# Example for reports/ directory:

ACCESS_KEY_ID=XXXXXXXXXX
SECRET_ACCESS_KEY=XXXXXXXXXX
DB_HOST=XXXXXXXXXX
DB_PORT=XXXXXXXXXX
DB_USER=XXXXXXXXXX
DB_PASS=XXXXXXXXXX
DB_NAME=XXXXXXXXXX
SOURCE_EMAIL=XXXXXXXXXX
LOCAL_FOLDER=XXXXXXXXXX
```

> [!Note]
> - Replace `XXXXXXXXXX` with your actual configurations.
> - Ensure not to upload your .env files to version control for security reasons.

6. Navigate to the database directory and run the following command to create and seed the database tables:

```bash
cd database/
bash init_public_tables.sh
bash init_archive_tables.sh
```

## Deployment

1. Navigate to each subdirectory within the terraform directory and create a `terraform.tfvars` file:

```bash
cd terraform/alerts/
touch terraform.tfvars
# Repeat for other directories (archive/, dashboard/, database/, performance/, reports/, s3_bucket/)
```

2. Add the necessary variables to the `terraform.tfvars` file in each directory as shown below:

```.env
# Example for alerts/ directory:

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

# Example for archive/ directory:

AWS_ACCESS_KEY_ID=XXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXX
AWS_REGION=XXXXXXXXXX
DB_HOST=XXXXXXXXXX
DB_USER=XXXXXXXXXX
DB_PASS=XXXXXXXXXX
DB_PORT=XXXXXXXXXX
DB_NAME=XXXXXXXXXX
S3_BUCKET=XXXXXXXXXX

# Example for dashboard/ directory:

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

# Example for database/ directory:

AWS_ACCESS_KEY_ID=XXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXX
SUBNET_GROUP=XXXXXXXXXX
VPC_ID=XXXXXXXXXX
DB_USER=XXXXXXXXXX
DB_PASS=XXXXXXXXXX
PUBLIC_SUBNET_ID=XXXXXXXXXX

# Example for performance/ directory:

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

# Example for reports/ directory:

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

# Example for s3_bucket/ directory:

AWS_ACCESS_KEY_ID=XXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXX
AWS_REGION=XXXXXXXXXX

```

3. To build the cloud services, run these commands:

```sh
terraform init
terraform plan
terraform apply
```

4. To remove the cloud services, run this command:

```sh
terraform destroy
```

## Documentation

### ERD diagram for Short-term Storage (Resides within the Public Schema)

![ERD diagram 1](https://github.com/adamski201/RailwayTracker/blob/main/images/public_erd.png)

### ERD diagram for Long-term Storage (Resides within the Archive Schema)

![ERD diagram 2](https://github.com/adamski201/RailwayTracker/blob/main/images/archive_erd.png)

### Cloud architecture diagram

![Cloud architecture diagram](https://github.com/adamski201/RailwayTracker/blob/main/images/arch_diagram.png)

## Contributors

* [aribasyeda](https://github.com/aribasyeda)
* [SaniyaShaikhh](https://github.com/SaniyaShaikhh)
* [adamski201](https://github.com/adamski201)
* [isaacschaessenscoleman](https://github.com/isaacschaessenscoleman)
