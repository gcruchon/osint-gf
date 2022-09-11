# OSINT - Golfin Fella

## Prerequisites

Install Docker:

```sh
brew install docker
```

Install `mongosh` (replacement of Mongo Shell)

```sh
brew install mongosh
```

## Configure

### MongoDB

CHange directory to `.docker/mongodb`.

Create a `.db_root_username` file:

```sh
cp .db_root_username-sample .db_root_username
```

Edit `.db_root_username` to ceate your superuser username

Create a `.db_root_password` file:

```sh
cp .db_root_password-sample .db_root_password
```

Edit `.db_root_password` to ceate your superuser password

Create a `.db_username` file:

```sh
cp .db_username-sample .db_username
```

Edit `.db_username` to ceate your regular user username

Create a `.db_password` file:

```sh
cp .db_password-sample .db_password
```

Edit `.db_root_password` to ceate your regulare user password

### Application

Create a `.env` file in the root folder:

```sh
cp .env-sample .env
```

Change variables:

- `TG_API_ID`
- `TG_API_HASH`
- `MONGODB_USERNAME`: password to access your MongoDB (same value as in `.db_username`)
- `MONGODB_PASSWORD`: password to access your MongoDB (same value as in `.db_password`)


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
