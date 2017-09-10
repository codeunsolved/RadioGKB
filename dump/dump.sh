pg=$1
psql -f dump/flush.sql
psql trpkb < $1