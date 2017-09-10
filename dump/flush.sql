DROP DATABASE trpkb;
CREATE DATABASE trpkb OWNER trpkb;
UPDATE pg_database SET encoding = pg_char_to_encoding('UTF8') WHERE datname = 'trpkb';