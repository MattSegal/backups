SITE=$1
S3_BUCKET=s3://swarm-db-backup/${SITE}/
LATEST_BACKUP=`aws s3 ls $S3_BUCKET | sort | grep .sql.gz | tail -n 1 | awk '{print $4}'`
aws s3 cp ${S3_BUCKET}${LATEST_BACKUP} - | \
    gunzip | \
    pg_restore --clean -d postgres -h localhost -p 25432 -U postgres --no-owner
