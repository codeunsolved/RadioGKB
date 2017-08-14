pg=$1
psql -f BACKUP/flush.sql
psql trpkb < $1