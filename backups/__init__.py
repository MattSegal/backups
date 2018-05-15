import re
import os
import subprocess
from datetime import datetime

import flask
from zappa.async import task, run

from .settings import SECRET_KEY, DATABASES
from .store import list_s3_files, upload_fileobj_to_s3

app = flask.Flask(__name__)
app.secret_key = SECRET_KEY


@app.route('/', methods=['GET'])
def home_page():
    backups = (parse_s3_backup(b) for b in list_s3_files())
    backups = [b for b in backups if b]
    backups = sorted(backups, key=lambda b: -b['timestamp'])
    return flask.render_template('index.html', **{
        'backups': backups,
    })


def parse_s3_backup(backup):
    key = backup['Key']
    site, filename = key.split('/')
    if not filename:
        return

    return {
        'site': site.title(),
        'filename': filename,
        'size': format_size(backup['Size']),
        'date': get_date(filename),
        'timestamp': get_timestamp(filename)
    }


def get_date(filename):
    timestamp = get_timestamp(filename)
    if timestamp:
        return datetime.fromtimestamp(timestamp).strftime('%a %d %b at %H:%M')
    else:
        return '-'


def get_timestamp(filename):
    # Look for '_1522926954.' from 'postgres_dump_1522926954.sql.gz'
    date_pattern = re.compile(r'_\d+\.')
    match = date_pattern.search(filename)
    if match:
        return int(match.group()[1:-1])


def format_size(num):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return '%3.1f%sB' % (num, unit)
        num /= 1024.0
    return '%.1f%s%s' % (num, 'Yi', 'B')


def take_backups():
    """
    Takes database snapshots for each database
    """
    print('Creating database backups')
    for db_name in DATABASES:
        run(take_backup, args=[], kwargs={'db_name': db_name})

    print('Done disptaching database backup jobs')


@app.route('/backups/', methods=['GET'])
def take_backups():
    """
    Takes database snapshots for each database
    """
    print('Creating database backups')
    for db_name in DATABASES:
        take_backup(*[], **{'db_name': db_name})

    print('Done disptaching database backup jobs')
    return 'Done!'


@task
def take_backup(*args, **kwargs):
    """
    Take a particular database backup
    """
    db_name = kwargs.get('db_name')
    if not db_name:
        print('No database name provided for creating backup')
        return

    print('[{}] Creating backup'.format(db_name))
    backup_file = '/tmp/{}.sql'.format(db_name)
    dir_path = os.path.dirname(os.path.abspath(__file__))
    pg_dump_path = os.path.join(dir_path, 'bin', 'pg_dump')
    env = {
        **DATABASES[db_name],
    }
    process = subprocess.Popen(
        ['pg_dump', '--format=custom', '--file={}'.format(backup_file)],
        env=env
    )
    print('[{}] Waiting for pg_dump'.format(db_name))
    process.wait()
    print('[{}] Done creating backup'.format(db_name))
    if not os.path.exists(backup_file):
        print('[{}] Could not create backup file with pg_dump'.format(db_name))
        return

    process = subprocess.Popen(['gzip', backup_file])
    print('[{}] Gzipping {}'.format(db_name, backup_file))
    process.wait()
    backup_file += '.gz'
    if not os.path.exists(backup_file):
        print('[{}] Could not gzip backup file'.format(db_name))
        return

    timestamp = int(datetime.now().timestamp())
    filename = 'postgres_dump_{}.sql.gz'.format(timestamp)
    key = '{}/{}'.format(db_name, filename)

    with open(backup_file, 'rb') as f:
        print('[{}] Uploading {} to S3 key {}'.format(db_name, backup_file, key))
        upload_fileobj_to_s3(f, key)

    print('[{}] Finished uploading {} to S3 key {}'.format(db_name, backup_file, key))
    print('[{}] Done creating backup'.format(db_name))


if __name__ == '__main__':
    app.run()
