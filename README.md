# Railway Tracker

## About

Brief description of project.

## Folder & Files Structure

`.github/`: Contains the GitHub Actions workflow files for CI/CD.

`dashboard/`: Contains the Streamlit dashboard code.

`images/`: Contains images used in the README [across the project].

`terraform/`: Contains the Terraform files for deploying the cloud services.

`schema/:` Contains the SQL schema for the database.

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
ACCESS_KEY_ID=XXXXXXXXXX
SECRET_ACCESS_KEY=XXXXXXXXXX
BUCKET_NAME=XXXXXXXXXX
DB_USER=XXXXXXXXXX
DB_PASSWORD=XXXXXXXXXX
SCHEMA_NAME=XXXXXXXXXX
DB_HOST=XXXXXXXXXX
DB_PORT=XXXXXXXXXX
DB_NAME=XXXXXXXXXX
```

`DB_HOST` should be a valid URL to a Postgres database server.

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

### ERD diagram

![ERD diagram](...)

### Cloud architecture diagram

![Cloud architecture diagram](...)

### Dashboard Wireframe

### Dashboard Mockup

## Contributors

* [aribasyeda](https://github.com/aribasyeda)
* [SaniyaShaikhh](https://github.com/SaniyaShaikhh)
* [adamski201](https://github.com/adamski201)
* [isaacschaessenscoleman](https://github.com/isaacschaessenscoleman)