/* use this init script if you want to test EMX2 with non-molgenis user */
CREATE DATABASE molgenis;
CREATE USER molgenis WITH LOGIN NOSUPERUSER INHERIT CREATEROLE ENCRYPTED PASSWORD 'molgenis';
GRANT ALL PRIVILEGES ON DATABASE molgenis TO molgenis;
CREATE DATABASE negotiator;
CREATE USER negotiator WITH LOGIN NOSUPERUSER INHERIT CREATEROLE ENCRYPTED PASSWORD 'negotiator';
GRANT ALL PRIVILEGES ON DATABASE negotiator TO negotiator;
\connect negotiator
GRANT ALL PRIVILEGES ON SCHEMA public TO negotiator;