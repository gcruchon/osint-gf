# OSINT - Golfin Fella

## Prerequisites

Python: v3.9.14

Install Pipenv:

```sh
brew install pipenv
```

Install Docker:

```sh
brew install docker
```

Install `mongosh` (replacement of Mongo Shell)

```sh
brew install mongosh
```

Install AWS Cli:

```sh
brew install awscli
```


## Configure

### MongoDB

Change directory to `.docker/mongodb`.

Create the following files:

-  `.db_root_username`: contains the username for the admin user of MongoDB
-  `.db_root_password`: contains the password for the admin user of MongoDB
-  `.db_username`: contains the username for the regular user of MongoDB
-  `.db_password`: contains the password for the regular user of MongoDB
-  `.db_basicauth_username`: contains the username for the basic auth access to Mongo-Express
-  `.db_basicauth_password`: contains the password for the basic auth access to Mongo-Express

For this, you can copy the sample files:

```sh
cd .docker/mongodb
cp .db_root_username-sample .db_root_username
cp .db_root_password-sample .db_root_password
cp .db_username-sample .db_username
cp .db_password-sample .db_password
cp .db_basicauth_username-sample .db_basicauth_username
cp .db_basicauth_password-sample .db_basicauth_password
```

And then edit each file to match your own username / passwords.

### Application

Create a `.env` file in the root folder:

```sh
cp .env-sample .env
```

### Localstack

Create a default bucket name `osint` on your localstack S3 emulation

```sh
aws --endpoint-url=http://localhost:4566 --no-sign-request s3 mb s3://osint
```

Change variables:

- `TG_API_ID`
- `TG_API_HASH`
- `MONGODB_USERNAME`: password to access your MongoDB (same value as in `.db_username`)
- `MONGODB_PASSWORD`: password to access your MongoDB (same value as in `.db_password`)
- `AWS_ACCESS_KEY_ID`: AWS Credentials
- `AWS_SECRET_ACCESS_KEY`: AWS Credentials
- `AWS_REGION_NAME`: AWS Region (e.g. 'us-east-1')
- `AWS_BUCKET_NAME`: AWS location for the telegram files

## Usage

```sh
cd .docker
docker compose -p "osint-gf" up
```

```sh
docker build . -t osint-gf:0.0.1
docker run --env-file .env ubuntu bash
```

To inspect database, run:

```sh
mongosh --username superfella
```

Then enter the password you entered in `.db_root_password`.

## Sources of inspiration

- https://sourcery.ai/blog/python-docker/
