# Database Backups

WARNING: BROKEN - DOES NOT RUN IN LAMBDA ENVIRONMENT

A Flask app that can be deployed using Zappa to run database backups on a Postgres instance every 3 days.

Expect a file called settings.py which contains:

    SECRET_KEY
    BACKUP_S3_BUCKET
    DATABASES = {
        name: {
            PGHOST
            PGPORT
            PGUSER
            PGPASSWORD
            PGDATABASE
        }
    }

## Postgres Dump

`pg_dump` has to be included with the backup code (see [here](https://github.com/jameshy/pgdump-aws-lambda)).


## to do

- automatically prune dumps older than X days
