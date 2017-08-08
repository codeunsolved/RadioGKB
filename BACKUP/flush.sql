DROP DATABASE trpkb;
CREATE DATABASE trpkb OWNER trpkb;
update pg_database set encoding = pg_char_to_encoding('UTF8') where datname = 'trpkb';