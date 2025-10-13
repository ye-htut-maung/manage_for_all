
# Start from the official PostgreSQL image
FROM postgres:16-alpine

# Copy your initialization script into the special entrypoint directory
COPY init.sql /docker-entrypoint-initdb.d/