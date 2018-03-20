pg_file=$1
psql -f dump/flush.sql
psql trpkb < $pg_file