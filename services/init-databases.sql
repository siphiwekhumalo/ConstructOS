-- Initialize databases for each microservice
-- This script runs when the PostgreSQL container first starts

CREATE DATABASE identity_db;
CREATE DATABASE sales_db;
CREATE DATABASE finance_db;
CREATE DATABASE inventory_db;
CREATE DATABASE hr_db;
CREATE DATABASE compliance_db;
CREATE DATABASE project_db;
CREATE DATABASE document_db;
CREATE DATABASE ai_db;

-- Grant privileges to the constructos user
GRANT ALL PRIVILEGES ON DATABASE identity_db TO constructos;
GRANT ALL PRIVILEGES ON DATABASE sales_db TO constructos;
GRANT ALL PRIVILEGES ON DATABASE finance_db TO constructos;
GRANT ALL PRIVILEGES ON DATABASE inventory_db TO constructos;
GRANT ALL PRIVILEGES ON DATABASE hr_db TO constructos;
GRANT ALL PRIVILEGES ON DATABASE compliance_db TO constructos;
GRANT ALL PRIVILEGES ON DATABASE project_db TO constructos;
GRANT ALL PRIVILEGES ON DATABASE document_db TO constructos;
GRANT ALL PRIVILEGES ON DATABASE ai_db TO constructos;
