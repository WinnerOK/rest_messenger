# Simple messenger

Simple API-based messenger. 

It doesn't fully comply to rest architecture from point of functionality due to
user authentication is done by passing uuid in request body, so some `GET` and `DELETE`
endpoints were converted to `POST`.

## Installation
0. clone repo
0. go to repo folder
0. configure environment variables in your system or at `.env` file (see section below)
0. run `docker-compose up`
0. run `docker exec -it rest_messenger bash -c './manage.py migrate`

## Environment variables
### docker-compose's vars
* `POSTGRES_TAG` - tag of used PostgreSQL container
* `SERVER_PORT` - port on which server will run

### Services' vars
* `POSTGRES_USER` - username of a postgres user
* `POSTGRES_PASSWORD` - password of the postgres user
* `POSTGRES_DB` - name of a database used inside postgres
* `SECRET_KEY` - a secret key used in Django
* `DEBUG` - if set, enables debug mode in Django. (**Do not use in production**)

### Example
Possible `.env` file is present below, 
but it is strongly recommended to generate credentials by yourself.
```
# docker-compose variables
POSTGRES_TAG=12
SERVER_PORT=8888
# services variables
POSTGRES_USER=xxe6o60v1bk74od3
POSTGRES_PASSWORD=w173y8azo6ywdi20
POSTGRES_DB=messenger_db
SECRET_KEY=s3J4gqfJD36tY82PyhhwX9gL4udT6ZT3u3hZp9PeVmLGWgvRtb
DEBUG=
```
## Run tests
To run tests execute the following command:
```
docker exec -it rest_messenger bash -c './manage.py test'
```

## API documentation
To see API documentation refer to Swagger UI at `localhost:<${SERVER_PORT}>/api/swagger/`
![](https://i.imgur.com/TNwy1e0.png)