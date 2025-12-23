#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE n8n;
    CREATE DATABASE simstudio;
    GRANT ALL PRIVILEGES ON DATABASE n8n TO ziggie;
    GRANT ALL PRIVILEGES ON DATABASE simstudio TO ziggie;
EOSQL
