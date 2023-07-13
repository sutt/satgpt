-- create a new database and associated user/password for the app
-- run psql [-U postgres] -f init.sql
CREATE USER <user-name> WITH ENCRYPTED PASSWORD '<user-password>';
CREATE DATABASE <db-name> OWNER <user-name>;
GRANT ALL PRIVILEGES ON DATABASE <db-name> TO <user-name>;