# Database Backups

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

## to do

- automatically prune dumps older than X days
