#!/bin/bash
# wait-for-postgres.sh

set -e

host="$1"
shift
cmd="$@"

until PGPASSWORD="profXsreda2018" psql -h "$host" -U "prof_user" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
exec $cmd